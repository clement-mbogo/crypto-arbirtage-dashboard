from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
import json
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

SETTINGS_FILE = 'settings.json'
DB_FILE = 'trades.db'

# Initialize settings file if not exist
def init_settings():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 1,
            "reinvest": True,
            "live_mode": False
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)

# Load settings from file
def load_settings():
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

# Save settings to file
def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize trades database if not exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    pair TEXT,
                    profit REAL,
                    capital REAL
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    settings = load_settings()
    return render_template('dashboard.html', settings=settings)

@app.route('/prices')
def prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        btc = data['bitcoin']['usd']
        eth = data['ethereum']['usd']
        return jsonify({"btc": btc, "eth": eth})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        data = request.get_json()
        save_settings(data)
        return jsonify({"status": "updated"})
    return jsonify(load_settings())

@app.route('/growth')
def growth():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT time, profit, capital FROM trades ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "time": r[0],
            "profit": r[1],
            "capital": r[2]
        })
    return jsonify(result)

@app.route('/backtest')
def backtest():
    # Dummy result (real logic to be added)
    return jsonify({
        "status": "completed",
        "trades": 15,
        "profit": 42.5
    })

if __name__ == '__main__':
    init_settings()
    init_db()
    app.run(debug=True)
