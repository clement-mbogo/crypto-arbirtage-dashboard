from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

SETTINGS_PATH = "settings.json"

# === Helpers ===
def get_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {
        "stake": 5,
        "target_profit": 5,
        "max_trades": 20,
        "cooldown": 60,
        "reinvest": True,
        "mode": "live"
    }

def save_settings(data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f)

# === Routes ===
@app.route("/")
def dashboard():
    settings = get_settings()
    return render_template("dashboard.html", settings=settings)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        data = request.json
        save_settings(data)
        return jsonify({"message": "Settings saved successfully"})
    return jsonify(get_settings())

@app.route("/prices")
def prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "BTC": data.get("bitcoin", {}).get("usd", "N/A"),
            "ETH": data.get("ethereum", {}).get("usd", "N/A")
        })
    except Exception as e:
        print("Error fetching prices:", e)
        return jsonify({"BTC": "Error", "ETH": "Error"}), 500

@app.route("/real_growth")
def real_growth():
    # Mock graph data
    now = datetime.now()
    data = [{"time": now.strftime("%H:%M:%S"), "capital": 100 + i*5, "profit": i*2, "trades": i} for i in range(10)]
    return jsonify(data)

@app.route("/backtest")
def backtest():
    return jsonify({"message": "Backtest started (mocked)"})

# === Main ===
if __name__ == "__main__":
    app.run(debug=True)
