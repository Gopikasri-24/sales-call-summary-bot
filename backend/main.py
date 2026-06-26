from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import sqlite3
import os
import re
import audio_utils

app = FastAPI(title="Sales Call Summary API")

print("Initializing AI Models...")

# -----------------------------
# Lazy Loading Variables
# -----------------------------
sum_model = None
sum_tokenizer = None
sentiment_analyzer = None
transcriber = None


# -----------------------------
# Load Summarization Model
# -----------------------------
def get_summarizer():
    global sum_model, sum_tokenizer

    if sum_model is None:
        print("Loading Summarization Model...")
        model_id = "sshleifer/distilbart-cnn-12-6"

        sum_tokenizer = AutoTokenizer.from_pretrained(model_id)
        sum_model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    return sum_model, sum_tokenizer


# -----------------------------
# Load Sentiment Model
# -----------------------------
def get_sentiment():
    global sentiment_analyzer

    if sentiment_analyzer is None:
        print("Loading Sentiment Model...")

        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    return sentiment_analyzer


# -----------------------------
# Load Whisper Model
# -----------------------------
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


# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect("sales_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript TEXT,
            summary TEXT,
            sentiment TEXT,
            action_items TEXT,
            customer_needs TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# Request Model
# -----------------------------
class TextInput(BaseModel):
    text: str


# -----------------------------
# Extract Customer Needs
# -----------------------------
def extract_customer_needs(text):
    sentences = re.split(r'[.!?\n]+', text)

    keywords = [
        'need', 'want', 'looking for', 'require', 'interested in',
        'budget', 'problem', 'issue', 'solve', 'help with'
    ]

    needs = []

    for s in sentences:
        s = s.strip()

        if len(s.split()) > 4 and any(k in s.lower() for k in keywords):
            s = re.sub(r'^[A-Za-z0-9\s]+:\s*', '', s)
            needs.append(s[0].upper() + s[1:])

    needs = list(dict.fromkeys(needs))

    if not needs:
        return ["No explicit customer needs detected in this call."]

    return needs[:4]


# -----------------------------
# Extract Action Items
# -----------------------------
def extract_action_items(text):
    sentences = re.split(r'[.!?\n]+', text)

    keywords = [
        'will', 'need to', 'must', 'action', 'task', 'follow up',
        'schedule', 'send', 'prepare', 'arrange'
    ]

    raw_items = [
        s.strip()
        for s in sentences
        if any(k in s.lower() for k in keywords)
    ]

    clean_items = []

    for item in raw_items:
        if len(item) < 10:
            continue

        item = re.sub(r'^[A-Za-z0-9\s]+:\s*', '', item)

        fillers = [
            r'^Of course,?\s*', r'^Sure,?\s*', r'^Thank you,?\s*',
            r'^Okay,?\s*', r'^Yes,?\s*', r'^Yeah,?\s*'
        ]

        for f in fillers:
            item = re.sub(f, '', item, flags=re.IGNORECASE)

        item = re.sub(
            r'^(I|We)\s+will\s+',
            '',
            item,
            flags=re.IGNORECASE
        )

        if item:
            clean_items.append(item[0].upper() + item[1:])

    clean_items = list(dict.fromkeys(clean_items))

    if not clean_items:
        return ["No specific action items detected."]

    return clean_items


# -----------------------------
# Process Text Endpoint
# -----------------------------
@app.post("/process_text")
async def process_text(input_data: TextInput):
    text = input_data.text
    words = text.split()

    if len(words) < 15 or "[Music]" in text:
        raise HTTPException(
            status_code=400,
            detail="Audio rejected: No valid speech detected."
        )

    # Dynamically load model contexts safely
    local_sum_model, local_sum_tokenizer = get_summarizer()
    local_sentiment_analyzer = get_sentiment()

    # Summarization
    inputs = local_sum_tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )

    input_len = inputs["input_ids"].shape[1]
    max_len = min(100, max(20, int(input_len * 0.6)))
    min_len = min(10, max_len - 5)

    summary_ids = local_sum_model.generate(
        inputs["input_ids"],
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        early_stopping=True
    )

    summary = local_sum_tokenizer.decode(
        summary_ids[0],
        skip_special_tokens=True
    )

    # Sentiment Analysis
    chunk_size = 400
    chunks = [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

    if not chunks:
        chunks = [text]

    total_pos = 0.0
    total_neg = 0.0

    for chunk in chunks:
        result = local_sentiment_analyzer(chunk[:512])[0]
        if result["label"] == "NEGATIVE":
            total_neg += result["score"]
        else:
            total_pos += result["score"]

    if (total_pos + total_neg) > 0:
        if total_neg > total_pos:
            sentiment = f"NEGATIVE ({round((total_neg / (total_pos + total_neg)) * 100, 2)}%)"
        else:
            sentiment = f"POSITIVE ({round((total_pos / (total_pos + total_neg)) * 100, 2)}%)"
    else:
        sentiment = "NEUTRAL (100%)"

    action_items = extract_action_items(text)
    customer_needs = extract_customer_needs(text)

    action_items_str = "\n".join(f"- {item}" for item in action_items)
    customer_needs_str = "\n".join(f"- {item}" for item in customer_needs)

    conn = sqlite3.connect("sales_bot.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO history
        (transcript, summary, sentiment, action_items, customer_needs)
        VALUES (?, ?, ?, ?, ?)
        """,
        (text, summary, sentiment, action_items_str, customer_needs_str)
    )
    conn.commit()
    conn.close()

    return {
        "transcript": text,
        "summary": summary,
        "sentiment": sentiment,
        "action_items": action_items,
        "customer_needs": customer_needs
    }


# -----------------------------
# Process Audio Endpoint
# -----------------------------
@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded audio file using utility
        file_path = audio_utils.save_uploaded_file(file)

        # Lazy load context for speech-to-text pipeline
        local_transcriber = get_transcriber()

        # Transcribe audio file to text
        result = local_transcriber(file_path)
        transcript = result["text"]

        # Clean up temporary disk files safely
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )

    # Route straight into the existing text execution block
    return await process_text(TextInput(text=transcript))


# -----------------------------
# History Endpoint
# -----------------------------
@app.get("/history")
async def get_history():
    conn = sqlite3.connect("sales_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, summary, sentiment
        FROM history
        ORDER BY id DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "summary": row[1],
            "sentiment": row[2]
        })

    return history


# -----------------------------
# Health Check Endpoint
# -----------------------------
@app.get("/")
async def root():
    return {
        "message": "Sales Call Summary API is running successfully!"
    }