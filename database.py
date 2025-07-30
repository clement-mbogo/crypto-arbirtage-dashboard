import sqlite3
from datetime import datetime

DB_FILE = "trades.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            buy_exchange TEXT,
            sell_exchange TEXT,
            buy_price REAL,
            sell_price REAL,
            profit REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            capital REAL,
            profit_percent REAL,
            trades_executed INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_trade(symbol, buy_exchange, sell_exchange, buy_price, sell_price, profit):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (timestamp, symbol, buy_exchange, sell_exchange, buy_price, sell_price, profit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.utcnow().isoformat(),
        symbol,
        buy_exchange,
        sell_exchange,
        buy_price,
        sell_price,
        profit
    ))
    conn.commit()
    conn.close()

def fetch_all_trades():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_performance_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM performance ORDER BY timestamp DESC")
    data = cursor.fetchall()
    conn.close()
    return data
def get_trade_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trades")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_current_capital():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT capital FROM performance ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 1000.0  # Default fallback capital

