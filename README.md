# Sales Call Summary Bot

## Project Description

Sales Call Summary Bot is a GenAI + NLP project that converts sales call transcripts into short summaries, sentiment, action items, and downloadable reports.

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- NLP: Hugging Face Transformers
- Database: SQLite
- Language: Python

## Features

- Enter sales call transcript
- Generate AI summary
- Extract action items
- Analyze sentiment
- Store history in SQLite database
- Download report as text file

## How to Run

### Install dependencies

pip install -r requirements.txt

### Run Backend

cd backend  
uvicorn main:app --reload

### Run Frontend

cd frontend  
streamlit run app.py

## Input

Sales call transcript.

## Output

- Summary
- Sentiment
- Action items
- Downloadable report
- History