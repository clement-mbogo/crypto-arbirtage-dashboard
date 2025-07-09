from flask import Flask, render_template, jsonify, request
import json
import time
import os
import requests

app = Flask(__name__)

# Load initial settings
SETTINGS_FILE = 'settings/settings.json'
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
else:
    settings = {
        "stake": 5,
        "target_profit": 5,
        "max_trades": 20,
        "cooldown": 60,
        "reinvest": True
    }

# Cache CoinGecko prices to prevent rate-limiting
last_prices = {}
last_fetch_time = 0

@app.route("/")
def index():
    return render_template("dashboard.html", settings=settings)

@app.route("/prices")
def prices():
    global last_fetch_time, last_prices
    now = time.time()

    if now - last_fetch_time < 30:
        return jsonify(last_prices)

    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")
        response.raise_for_status()
        prices = response.json()
        last_prices = prices
        last_fetch_time = now
        return jsonify(prices)
    except Exception as e:
        print("Error fetching prices:", e)
        return jsonify({"error": "API limit reached"}), 500

@app.route("/settings", methods=[GET, "POST"])
def update_settings():
    if request.method == 'POST':
        new_settings = request.json
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(new_settings, f, indent=2)
        return jsonify({"message": "Settings updated"})

    return jsonify(settings)

@app.route("/backtest")
def backtest():
    # Simple placeholder response
    return jsonify({"results": [
        {"timestamp": "2025-07-01", "profit": 4.3},
        {"timestamp": "2025-07-02", "profit": 2.7},
        {"timestamp": "2025-07-03", "profit": 5.1},
    ]})

if __name__ == "__main__":
    app.run(debug=True)
