from flask import Flask, render_template, jsonify, request
import json
import random
import requests
import os

app = Flask(__name__)

SETTINGS_FILE = 'settings.json'
TRADE_FILE = 'trades.json'

# Utility Functions
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return {
        "stake": 5,
        "target_profit": 5,
        "max_trades": 20,
        "cooldown": 1,
        "reinvest": True
    }

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@app.route('/')
def dashboard():
    settings = load_settings()
    return render_template('dashboard.html', settings=settings)

@app.route('/prices')
def prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"]
        })
    except Exception as e:
        print("Error fetching prices:", e)
        return jsonify({"BTC": None, "ETH": None}), 500

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        data = request.get_json()
        save_settings(data)
        return jsonify({"status": "saved"})
    return jsonify(load_settings())

@app.route('/backtest')
def backtest():
    # Placeholder: simulate backtest result
    growth = [100 + i * random.uniform(0.5, 1.5) for i in range(20)]
    return jsonify({"growth": growth})

if __name__ == '__main__':
    app.run(debug=True)
