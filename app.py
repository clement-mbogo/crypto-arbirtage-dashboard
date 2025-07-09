from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import requests
import time
import os
from datetime import datetime

app = Flask(__name__)

# === Load Settings ===
SETTINGS_FILE = "settings.json"
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

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

settings = load_settings()

# === Dashboard Routes ===
@app.route("/")
def dashboard():
    return render_template("dashboard.html", settings=settings)

@app.route("/settings", methods=["POST"])
def update_settings():
    data = request.form.to_dict()
    data["stake"] = float(data.get("stake", 5))
    data["target_profit"] = float(data.get("target_profit", 5))
    data["max_trades"] = int(data.get("max_trades", 20))
    data["cooldown"] = int(data.get("cooldown", 1))
    data["reinvest"] = "reinvest" in data
    save_settings(data)
    return redirect(url_for("dashboard"))

@app.route("/prices")
def prices():
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
            headers={"Accept": "application/json"}
        )
        if response.status_code == 429:
            return jsonify({"BTC": "Rate limit", "ETH": "Rate limit"}), 500

        prices = response.json()
        btc = prices.get("bitcoin", {}).get("usd", "?")
        eth = prices.get("ethereum", {}).get("usd", "?")
        return jsonify({"BTC": btc, "ETH": eth})
    except Exception as e:
        return jsonify({"BTC": "Error", "ETH": "Error"}), 500

@app.route("/backtest")
def backtest():
    return "Backtest page placeholder. Coming soon."

@app.route("/real_growth")
def real_growth():
    now = datetime.now().timestamp()
    data = {
        "labels": [now - 60, now - 30, now],
        "capital": [100, 105, 110],
        "profit": [0, 2, 5],
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
