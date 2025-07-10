from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import random

app = Flask(__name__)

# === Load settings from JSON ===
SETTINGS_FILE = 'settings.json'

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 60,
            "reinvest": True
        }
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

# === Routes ===
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_settings')
def get_settings():
    return jsonify(load_settings())

@app.route('/get_prices')
def get_prices():
    # Simulated live prices
    return jsonify({
        "BTC": round(29250 + random.uniform(-50, 50), 2),
        "ETH": round(1875 + random.uniform(-10, 10), 2)
    })

@app.route('/get_chart_data')
def get_chart_data():
    # Simulated chart data (should be replaced with actual DB or bot data)
    timestamps = [(datetime.now().strftime("%H:%M")) for _ in range(5)]
    capital = [100, 110, 115, 113, 120]
    profit = [0, 10, 15, 13, 20]
    trade_count = [0, 1, 2, 3, 4]

    return jsonify({
        "labels": timestamps,
        "capital": capital,
        "profit": profit,
        "trade_count": trade_count
    })

# === Run the app locally ===
if __name__ == '__main__':
    app.run(debug=True)
