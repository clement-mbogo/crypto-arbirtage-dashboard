from flask import Flask, render_template, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)

DB_PATH = "trades.db"

def create_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            capital REAL,
            profit REAL,
            trade_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/get_chart_data')
def get_chart_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, capital, profit, trade_count FROM trades ORDER BY timestamp ASC")
    rows = c.fetchall()
    conn.close()

    timestamps = [row[0] for row in rows]
    capital = [row[1] for row in rows]
    profit = [row[2] for row in rows]
    trades = [row[3] for row in rows]

    return jsonify({
        "timestamps": timestamps,
        "capital": capital,
        "profit": profit,
        "trades": trades
    })

@app.route('/seed_chart')
def seed_chart():
    create_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM trades")  # Clear existing data

    base_capital = 1000
    base_profit = 0
    total_trades = 0
    now = datetime.now()

    for i in range(10):
        timestamp = (now - timedelta(minutes=(9 - i) * 5)).strftime('%H:%M')
        trade_profit = random.uniform(-10, 15)
        base_profit += trade_profit
        base_capital += trade_profit
        total_trades += random.randint(1, 3)

        c.execute("INSERT INTO trades (timestamp, capital, profit, trade_count) VALUES (?, ?, ?, ?)",
                  (timestamp, round(base_capital, 2), round(base_profit, 2), total_trades))

    conn.commit()
    conn.close()
    return "Sample chart data seeded."

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
