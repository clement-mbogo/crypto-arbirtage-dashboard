from flask import Flask, render_template, jsonify, request
import requests
import json
import random
import os
from datetime import datetime

app = Flask(__name__)

SETTINGS_FILE = "settings.json"
BACKTEST_FILE = "backtest.json"

# Load settings
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 1,
            "reinvest": True
        }, f)

# Route: Home
@app.route("/")
def index():
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)
    return render_template("dashboard.html", settings=settings)

# Route: Prices
@app.route("/prices")
def prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "btc": data.get("bitcoin", {}).get("usd", "N/A"),
            "eth": data.get("ethereum", {}).get("usd", "N/A")
        })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prices: {e}")
        return jsonify({"btc": "Error", "eth": "Error"}), 500

# Route: Update Settings
@app.route("/settings", methods=["GET", "POST"])
def update_settings():
    if request.method == "POST":
        data = request.json
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        return jsonify({"message": "Settings updated"})
    else:
        with open(SETTINGS_FILE) as f:
            return jsonify(json.load(f))

# Route: Backtest (static demo data)
@app.route("/backtest")
def backtest():
    # Return dummy performance data
    return jsonify({
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "capital": [100, 105, 110, 108, 115],
        "profits": [0, 5, 5, -2, 7],
        "trades": [1, 2, 3, 2, 4]
    })

# Start
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
