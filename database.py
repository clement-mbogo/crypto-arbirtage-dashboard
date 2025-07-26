import sqlite3
from datetime import datetime

DB_FILE = "trades.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    price REAL,
                    quantity REAL,
                    side TEXT,
                    timestamp TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    capital REAL,
                    profit_percent REAL,
                    trade_count INTEGER,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

def save_trade(symbol, price, quantity, side):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    c.execute("INSERT INTO trades (symbol, price, quantity, side, timestamp) VALUES (?, ?, ?, ?, ?)",
              (symbol, price, quantity, side, timestamp))
    conn.commit()
    conn.close()

def save_performance(capital, profit_percent, trade_count):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    c.execute("INSERT INTO performance (capital, profit_percent, trade_count, timestamp) VALUES (?, ?, ?, ?)",
              (capital, profit_percent, trade_count, timestamp))
    conn.commit()
    conn.close()

def fetch_performance_data(limit=100):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM performance ORDER BY id DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data[::-1]  # return chronological

def fetch_all_trades():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM trades ORDER BY id DESC")
    trades = c.fetchall()
    conn.close()
    return trades
