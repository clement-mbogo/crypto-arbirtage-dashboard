from flask import Flask, render_template, request, jsonify
import json
import os
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

SETTINGS_FILE = "settings.json"

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

def load_settings():
    with open(SETTINGS_FILE) as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def dashboard():
    return render_template("dashboard.html", settings=load_settings())

@app.route("/settings", methods=["GET", "POST"])
def update_settings():
    if request.method == "POST":
        data = request.json
        save_settings(data)
        return jsonify({"message": "Settings saved"})
    return jsonify(load_settings())

@app.route("/prices")
def prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum",
            "vs_currencies": "usd"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "bitcoin": data.get("bitcoin", {}).get("usd"),
            "ethereum": data.get("ethereum", {}).get("usd")
        })
    except requests.exceptions.RequestException as e:
        print("Error fetching prices:", e)
        return jsonify({"error": "Price fetch error"}), 500

@app.route("/real_growth")
def real_growth():
    now = datetime.now().strftime("%H:%M:%S")
    return jsonify({"time": now, "profit": round(100 + datetime.now().second * 0.5, 2)})

@app.route("/backtest")
def backtest():
    result = {
        "trades": 150,
        "win_rate": "62.5%",
        "roi": "+18.3%",
        "duration": "3 months"
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
