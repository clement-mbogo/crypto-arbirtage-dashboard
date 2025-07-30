import sqlite3
from datetime import datetime

DB_FILE = "trades.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                exchange_from TEXT,
                exchange_to TEXT,
                symbol TEXT,
                volume REAL,
                profit REAL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                capital REAL,
                profit_percent REAL,
                total_trades INTEGER
            )
        """)
        conn.commit()

def fetch_all_trades():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM trades ORDER BY timestamp DESC")
        return c.fetchall()

def fetch_performance_data():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT capital, profit_percent, total_trades
            FROM performance
            ORDER BY id DESC
            LIMIT 1
        """)
        row = c.fetchone()
    if row:
        return {"capital": row[0], "profit_percent": row[1], "total_trades": row[2]}
    return {"capital": 0.0, "profit_percent": 0.0, "total_trades": 0}

def fetch_performance_history(limit=100):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT timestamp, capital, profit_percent, total_trades
            FROM performance
            ORDER BY timestamp ASC
            LIMIT ?
        """, (limit,))
        rows = c.fetchall()
    return [
        {"timestamp": r[0], "capital": r[1], "profit_percent": r[2], "total_trades": r[3]}
        for r in rows
    ]
