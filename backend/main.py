from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import os
import re

# Import your own utility modules correctly
import audio_utils
import database
import report_generator

app = FastAPI(title="Sales Call Summary API")

print("Initializing AI Models...")

# Lazy Loading Containers
sum_model = None
sum_tokenizer = None
sentiment_analyzer = None
transcriber = None

# Automatically spin up database schema on start
database.create_table()

def get_summarizer():
    global sum_model, sum_tokenizer
    if sum_model is None:
        print("Loading Summarization Model...")
        model_id = "sshleifer/distilbart-cnn-12-6"
        sum_tokenizer = AutoTokenizer.from_pretrained(model_id)
        sum_model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    return sum_model, sum_tokenizer

def get_sentiment():
    global sentiment_analyzer
    if sentiment_analyzer is None:
        print("Loading Sentiment Model...")
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    return sentiment_analyzer

def get_transcriber():
    global transcriber
    if transcriber is None:
        print("Loading Whisper Tiny Model...")
        transcriber = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            chunk_length_s=30
        )
    return transcriber

class TextInput(BaseModel):
    text: str

def extract_customer_needs(text):
    sentences = re.split(r'[.!?\n]+', text)
    keywords = ['need', 'want', 'looking for', 'require', 'interested in', 'budget', 'problem', 'issue', 'solve', 'help with']
    needs = []
    for s in sentences:
        s = s.strip()
        if len(s.split()) > 4 and any(k in s.lower() for k in keywords):
            s = re.sub(r'^[A-Za-z0-9\s]+:\s*', '', s)
            needs.append(s[0].upper() + s[1:])
    needs = list(dict.fromkeys(needs))
    return needs[:4] if needs else ["No explicit customer needs detected in this call."]

def extract_action_items(text):
    sentences = re.split(r'[.!?\n]+', text)
    keywords = ['will', 'need to', 'must', 'action', 'task', 'follow up', 'schedule', 'send', 'prepare', 'arrange']
    raw_items = [s.strip() for s in sentences if any(k in s.lower() for k in keywords)]
    
    clean_items = []
    for item in raw_items:
        if len(item) < 10: continue
        item = re.sub(r'^[A-Za-z0-9\s]+:\s*', '', item)
        fillers = [r'^Of course,?\s*', r'^Sure,?\s*', r'^Thank you,?\s*', r'^Okay,?\s*', r'^Yes,?\s*', r'^Yeah,?\s*']
        for f in fillers:
            item = re.sub(f, '', item, flags=re.IGNORECASE)
        item = re.sub(r'^(I|We)\s+will\s+', '', item, flags=re.IGNORECASE)
        if item:
            clean_items.append(item[0].upper() + item[1:])
            
    clean_items = list(dict.fromkeys(clean_items))
    return clean_items if clean_items else ["No specific action items detected."]

@app.post("/process_text")
async def process_text(input_data: TextInput):
    text = input_data.text
    words = text.split()

    if len(words) < 15 or "[Music]" in text:
        raise HTTPException(
            status_code=400,
            detail="Audio rejected: No valid speech detected. Ensure this is a conversation."
        )

    sum_model, sum_tokenizer = get_summarizer()
    sentiment_analyzer = get_sentiment()

    # Summarization
    inputs = sum_tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    input_len = inputs["input_ids"].shape[1]
    max_len = min(100, max(20, int(input_len * 0.6)))
    min_len = min(10, max_len - 5)
    
    summary_ids = sum_model.generate(
        inputs["input_ids"], max_length=max_len, min_length=min_len, do_sample=False, early_stopping=True
    )
    summary = sum_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # Sentiment Chunk Analyzer
    chunk_size = 400
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)] or [text]
    total_pos, total_neg = 0.0, 0.0

    for chunk in chunks:
        result = sentiment_analyzer(chunk[:512])[0]
        if result["label"] == "NEGATIVE":
            total_neg += result["score"]
        else:
            total_pos += result["score"]

    total_score = total_pos + total_neg
    if total_neg > total_pos:
        sentiment = f"NEGATIVE ({round((total_neg / total_score) * 100, 2)}%)"
    else:
        sentiment = f"POSITIVE ({round((total_pos / total_score) * 100, 2)}%)"

    action_items = extract_action_items(text)
    customer_needs = extract_customer_needs(text)

    # Generate localized report file
    report_path = report_generator.generate_report(text, summary, action_items, sentiment)

    # Save cleanly into database using your centralized database utility!
    database.insert_call(
        transcript=text,
        summary=summary,
        action_items=action_items,
        sentiment=sentiment,
        report_path=report_path
    )

    return {
        "transcript": text,
        "summary": summary,
        "sentiment": sentiment,
        "action_items": action_items,
        "customer_needs": customer_needs
    }

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        file_path = audio_utils.save_uploaded_file(file)
        transcriber = get_transcriber()
        result = transcriber(file_path)
        transcript = result["text"]

        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

    return await process_text(TextInput(text=transcript))

@app.get("/history")
async def get_history():
    # Fetch rows cleanly utilizing database.py mapping
    rows = database.get_history()
    return [{"id": r[0], "summary": r[1], "sentiment": r[2]} for r in rows][:5]

@app.get("/")
async def root():
    return {"message": "Sales Call Summary API is running successfully!"}