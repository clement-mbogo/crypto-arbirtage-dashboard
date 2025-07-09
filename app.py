import json
import sqlite3
import threading
import time
from datetime import datetime
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DB_PATH = 'trades.db'
SETTINGS_PATH = 'settings.json'

# Load or initialize settings
def load_settings():
    try:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        settings = {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 60,
            "reinvest": True
        }
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f)
        return settings

# Save settings
def save_settings(data):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(data, f)

# Init DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    pair TEXT,
                    profit REAL
                )''')
    conn.commit()
    conn.close()

init_db()
settings = load_settings()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', settings=settings)

@app.route('/settings', methods=['GET', 'POST'])
def update_settings():
    if request.method == 'POST':
        data = request.get_json()
        save_settings(data)
        return jsonify({"status": "updated"})
    return jsonify(load_settings())

@app.route('/prices')
def prices():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")
        r.raise_for_status()
        return jsonify(r.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/growth')
def growth():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, SUM(profit) OVER (ORDER BY id) FROM trades")
    data = c.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/backtest')
def backtest():
    fake_results = [{"timestamp": datetime.now().isoformat(), "profit": i} for i in range(10)]
    return jsonify(fake_results)

if __name__ == '__main__':
    app.run(debug=True)
