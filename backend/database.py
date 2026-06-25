import sqlite3
from datetime import datetime

DB_NAME = "sales_calls.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript TEXT,
            summary TEXT,
            action_items TEXT,
            sentiment TEXT,
            report_path TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Changed action_items to accept a pre-formatted string directly
def insert_call(transcript, summary, action_items, sentiment, report_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales_calls 
        (transcript, summary, action_items, sentiment, report_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        transcript,
        summary,
        action_items,  # No .join() here, pass the string directly
        sentiment,
        report_path,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, summary, sentiment, report_path, created_at 
        FROM sales_calls 
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows