from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# === Settings File ===
SETTINGS_FILE = "settings.json"
DB_FILE = "trades.db"

# === Load Settings ===
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 1,
            "reinvest": True
        }

# === Save Settings ===
def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

# === Price Fetching ===
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

def fetch_prices():
    try:
        response = requests.get(COINGECKO_URL)
        response.raise_for_status()
        prices = response.json()
        btc_price = prices.get("bitcoin", {}).get("usd", "Error")
        eth_price = prices.get("ethereum", {}).get("usd", "Error")
        return btc_price, eth_price
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return "Error", "Error"

# === Routes ===
@app.route("/")
def index():
    settings = load_settings()
    return render_template("dashboard.html", settings=settings)

@app.route("/prices")
def prices():
    btc, eth = fetch_prices()
    return jsonify({"btc": btc, "eth": eth})

@app.route("/settings", methods=["GET", "POST"])
def update_settings():
    if request.method == "POST":
        data = request.json
        save_settings(data)
        return jsonify({"status": "success"})
    else:
        return jsonify(load_settings())

@app.route("/simulate", methods=["POST"])
def simulate():
    settings = load_settings()
    initial = float(settings.get("stake", 5))
    growth = [initial]
    for i in range(int(settings.get("max_trades", 20))):
        profit = growth[-1] * float(settings.get("target_profit", 5)) / 100
        if not settings.get("reinvest", True):
            growth.append(growth[-1] + profit)
        else:
            growth.append(growth[-1] * (1 + float(settings.get("target_profit", 5)) / 100))
    return jsonify({"growth": growth})

# === Run ===
if __name__ == "__main__":
    app.run(debug=True)
