from flask import Flask, render_template, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
import random
from binance_utils import load_binance_client, get_balance

app = Flask(__name__)

DB_FILE = "bot.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                capital REAL NOT NULL,
                profit REAL NOT NULL,
                trade_count INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

def seed_fake_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    base_capital = 10000
    for i in range(14):
        timestamp = (datetime.now() - timedelta(days=14 - i)).strftime('%Y-%m-%d')
        profit = round(random.uniform(20, 200), 2)
        capital = round(base_capital + profit * i, 2)
        trades = random.randint(5, 20)
        cursor.execute("INSERT INTO performance (timestamp, capital, profit, trade_count) VALUES (?, ?, ?, ?)",
                       (timestamp, capital, profit, trades))
    conn.commit()
    conn.close()

# ✅ Initialize on startup
init_db()
seed_fake_data()  # 🔁 COMMENT this out after DB is seeded once

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/binance_balance")
def binance_balance():
    client = load_binance_client(testnet=True)
    usdt = get_balance(client, "USDT")
    btc = get_balance(client, "BTC")
    eth = get_balance(client, "ETH")
    return jsonify({"USDT": usdt, "BTC": btc, "ETH": eth})

@app.route("/real_growth")
def real_growth():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, capital, profit, trade_count FROM performance")
    rows = cursor.fetchall()
    conn.close()

    data = {
        "labels": [row[0] for row in rows],
        "capital": [row[1] for row in rows],
        "profit": [row[2] for row in rows],
        "trades": [row[3] for row in rows],
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
