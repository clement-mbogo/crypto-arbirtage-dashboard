import sqlite3
from datetime import datetime

DB_FILE = "trades.db"

def init_performance_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            capital REAL,
            profit_pct REAL,
            trade_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def record_performance(capital, profit_pct, trade_count):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO performance (timestamp, capital, profit_pct, trade_count)
        VALUES (?, ?, ?, ?)
    ''', (datetime.utcnow().isoformat(), capital, profit_pct, trade_count))
    conn.commit()
    conn.close()

def fetch_performance_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT timestamp, capital, profit_pct, trade_count FROM performance ORDER BY timestamp ASC')
    data = c.fetchall()
    conn.close()
    return data
