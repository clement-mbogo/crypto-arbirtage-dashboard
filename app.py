from flask import Flask, render_template, jsonify, request
import requests
import json
import os
import time
from datetime import datetime

app = Flask(__name__)

SETTINGS_FILE = "settings.json"
PRICE_CACHE = {}
CACHE_DURATION = 60  # seconds

# Helper to load settings
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default = {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 1,
            "reinvest": True
        }
        save_settings(default)
        return default
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

# Helper to save settings
def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Cache API prices to reduce rate limit hits
def get_cached_prices():
    now = time.time()
    if "timestamp" in PRICE_CACHE and now - PRICE_CACHE["timestamp"] < CACHE_DURATION:
        return PRICE_CACHE["data"]

    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                         params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"})
        r.raise_for_status()
        data = r.json()
        PRICE_CACHE["data"] = data
        PRICE_CACHE["timestamp"] = now
        return data
    except Exception as e:
        print("Error fetching prices:", e)
        return {}

@app.route("/")
def dashboard():
    settings = load_settings()
    return render_template("dashboard.html", settings=settings)

@app.route("/prices")
def prices():
    data = get_cached_prices()
    return jsonify(data)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    form = request.form
    settings = {
        "stake": float(form.get("stake", 5)),
        "target_profit": float(form.get("target_profit", 5)),
        "max_trades": int(form.get("max_trades", 20)),
        "cooldown": int(form.get("cooldown", 1)),
        "reinvest": form.get("reinvest") == "true"
    }
    save_settings(settings)
    return "Updated", 200

@app.route("/simulate_backtest")
def simulate_backtest():
    fake_data = []
    capital = 100
    for i in range(20):
        capital += capital * 0.02
        fake_data.append({
            "time": f"T{i+1}",
            "capital": round(capital, 2),
            "profit": round(capital - 100, 2),
            "trades": i+1
        })
    return jsonify(fake_data)

if __name__ == "__main__":
    app.run(debug=True)
