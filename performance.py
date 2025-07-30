# performance.py

import sqlite3
import os
from datetime import datetime

DB_FILE = os.getenv("DB_FILE", "trades.db")

def init_performance_table():
    """
    Ensure the performance table exists.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                capital REAL NOT NULL,
                profit_percent REAL NOT NULL,
                total_trades INTEGER NOT NULL
            )
        """)
        conn.commit()

def save_performance(capital: float, profit_percent: float, total_trades: int):
    """
    Insert a new performance snapshot.
    """
    ts = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO performance (timestamp, capital, profit_percent, total_trades)
            VALUES (?, ?, ?, ?)
        """, (ts, capital, profit_percent, total_trades))
        conn.commit()

def fetch_latest_performance():
    """
    Retrieve the most recent performance snapshot.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, capital, profit_percent, total_trades
              FROM performance
             ORDER BY id DESC
             LIMIT 1
        """)
        row = cursor.fetchone()

    if row:
        return {
            "timestamp": row[0],
            "capital": row[1],
            "profit_percent": row[2],
            "total_trades": row[3]
        }
    # Fallback if no data yet
    return {"timestamp": None, "capital": 0.0, "profit_percent": 0.0, "total_trades": 0}

def fetch_performance_history(limit: int = 100):
    """
    Retrieve up to `limit` historical performance records in chronological order.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, capital, profit_percent, total_trades
              FROM performance
             ORDER BY id ASC
             LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    return [
        {"timestamp": r[0], "capital": r[1], "profit_percent": r[2], "total_trades": r[3]}
        for r in rows
    ]
