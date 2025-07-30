# trade_logger.py

import sqlite3
from datetime import datetime

DB_FILE = "trades.db"

def init_trade_table():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                profit REAL,
                capital_before REAL,
                capital_after REAL
            )
        """)
        conn.commit()

def save_trade(symbol, profit, capital_before, capital_after):
    timestamp = datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades (timestamp, symbol, profit, capital_before, capital_after)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, symbol, profit, capital_before, capital_after))
        conn.commit()

def fetch_all_trades():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, symbol, profit, capital_before, capital_after
            FROM trades
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
    return [
        {
            "timestamp": row[0],
            "symbol": row[1],
            "profit": row[2],
            "capital_before": row[3],
            "capital_after": row[4]
        } for row in rows
    ]
