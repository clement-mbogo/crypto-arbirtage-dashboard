from flask import Flask, render_template, request, jsonify
import json
import os
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

SETTINGS_FILE = 'settings.json'
DB_FILE = 'trades.db'

# Load settings from file
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 1,
            "reinvest": True
        }
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

# Save settings to file
def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f)

# Price fetch endpoint
@app.route('/prices')
def prices():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "BTC": data.get("bitcoin", {}).get("usd", "N/A"),
            "ETH": data.get("ethereum", {}).get("usd", "N/A")
        })
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return jsonify({"BTC": "Error", "ETH": "Error"}), 500

# Chart data simulation
@app.route('/chart-data')
def chart_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT timestamp, profit, capital, trades FROM performance ORDER BY timestamp ASC")
        data = c.fetchall()
        conn.close()
        return jsonify([{
            'time': row[0],
            'profit': row[1],
            'capital': row[2],
            'trades': row[3]
        } for row in data])
    except:
        return jsonify([])

# Get settings
@app.route('/settings')
def get_settings():
    return jsonify(load_settings())

# Save settings
@app.route('/settings', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        save_settings(data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Backtest endpoint
@app.route('/backtest', methods=['POST'])
def backtest():
    try:
        # Dummy simulation
        return jsonify({"status": "complete", "message": "Backtest simulation complete"})
    except:
        return jsonify({"status": "error"})

# Main dashboard
@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
