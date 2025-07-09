from flask import Flask, render_template, request, jsonify
import requests
import json
import sqlite3
import random
import os
from datetime import datetime

app = Flask(__name__)

# Load or initialize settings
SETTINGS_FILE = "settings.json"
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {\        "stake": 5,
        "target_profit": 5,
        "max_trades": 20,
        "cooldown": 1,
        "reinvest": True
    }

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()

# SQLite DB setup
conn = sqlite3.connect("trades.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT,
    buy_price REAL,
    sell_price REAL,
    profit REAL,
    timestamp TEXT
)''')
conn.commit()

# Fetch prices from CoinGecko
@app.route("/prices")
def prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "btc": data.get("bitcoin", {}).get("usd", "Error"),
            "eth": data.get("ethereum", {}).get("usd", "Error")
        })
    except Exception as e:
        print("Error fetching prices:", e)
        return jsonify({"btc": "Error", "eth": "Error"}), 500

# Main dashboard
@app.route("/")
def dashboard():
    return render_template("dashboard.html", settings=settings)

# Update settings
@app.route("/settings", methods=["POST"])
def update_settings():
    data = request.form.to_dict()
    settings.update({
        "stake": float(data.get("stake", settings["stake"])),
        "target_profit": float(data.get("target_profit", settings["target_profit"])),
        "max_trades": int(data.get("max_trades", settings["max_trades"])),
        "cooldown": int(data.get("cooldown", settings["cooldown"])),
        "reinvest": data.get("reinvest", "false") == "true"
    })
    save_settings(settings)
    return ("", 204)

# Simulated graph data
@app.route("/real_growth")
def real_growth():
    times = [datetime.now().strftime("%H:%M:%S") for _ in range(10)]
    capital = [100 + i * random.uniform(1, 3) for i in range(10)]
    profit = [v - 100 for v in capital]
    trades = [i for i in range(10)]
    return jsonify({"time": times, "capital": capital, "profit": profit, "trades": trades})

# Backtest endpoint (mock)
@app.route("/backtest")
def backtest():
    return jsonify({"message": "Backtest completed", "profit": round(random.uniform(5, 50), 2)})

if __name__ == "__main__":
    app.run(debug=True)
