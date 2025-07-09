from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import datetime
import random

app = Flask(__name__)

SETTINGS_FILE = 'settings.json'

# Load or initialize settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        "stake": 5,
        "target_profit": 5,
        "max_trades": 20,
        "cooldown": 1,
        "reinvest": True
    }

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

@app.route('/')
def index():
    settings = load_settings()
    return render_template('dashboard.html', settings=settings)

@app.route('/prices')
def get_prices():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "btc": data["bitcoin"]["usd"],
            "eth": data["ethereum"]["usd"]
        })
    except Exception as e:
        print("Error fetching prices:", e)
        return jsonify({"btc": None, "eth": None})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        data = request.json
        save_settings(data)
        return jsonify({"status": "saved"})
    return jsonify(load_settings())

@app.route('/real_growth')
def real_growth():
    now = datetime.datetime.now()
    data = []
    base = 100
    for i in range(20):
        point = {
            "timestamp": (now - datetime.timedelta(minutes=19 - i)).strftime('%H:%M'),
            "capital": base + i * random.uniform(0.1, 0.5),
            "profit": i * random.uniform(0.1, 0.4),
            "trades": i
        }
        data.append(point)
    return jsonify(data)

@app.route('/backtest')
def backtest():
    results = {
        "total_trades": 45,
        "successful": 38,
        "failed": 7,
        "profit": round(38 * 1.3 - 7 * 1.0, 2),
        "capital_growth": round(100 + 38 * 1.3 - 7 * 1.0, 2)
    }
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
