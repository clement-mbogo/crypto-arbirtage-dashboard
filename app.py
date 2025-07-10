from flask import Flask, render_template, request, jsonify
from binance.client import Client
import sqlite3
import os, json

app = Flask(__name__)

# === Settings ===
SETTINGS_FILE = "settings.json"
DB_FILE = "trades.db"

# === Binance ===
def get_binance_client():
    with open(".env") as f:
        lines = f.readlines()
        keys = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in lines if '=' in line}
    return Client(keys['BINANCE_API_KEY'], keys['BINANCE_API_SECRET'])

def get_binance_balance(asset="USDT"):
    try:
        client = get_binance_client()
        account = client.get_account()
        balances = {bal['asset']: float(bal['free']) for bal in account['balances']}
        return balances.get(asset, 0)
    except Exception as e:
        print("Binance balance error:", e)
        return 0

def get_trade_count_from_binance(symbol="BTCUSDT"):
    try:
        client = get_binance_client()
        trades = client.get_my_trades(symbol=symbol)
        return len(trades)
    except Exception:
        return 0

# === DB ===
def get_all_trades():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, pair TEXT, amount REAL, profit REAL)")
    trades = c.execute("SELECT * FROM trades").fetchall()
    conn.close()
    return trades

def calculate_simulated_capital(trades, settings):
    capital = float(settings.get("initial_capital", 100))
    for t in trades:
        capital += float(t[3])  # profit
    return capital

# === Settings ===
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return {}

@app.route("/get_chart_data")
def get_chart_data():
    settings = load_settings()
    live_mode = settings.get("mode") == "live"

    if live_mode:
        capital = get_binance_balance("USDT")
        profit = capital - float(settings.get("initial_capital", 100))
        trades = get_trade_count_from_binance("BTCUSDT")
    else:
        data = get_all_trades()
        capital = calculate_simulated_capital(data, settings)
        profit = capital - float(settings.get("initial_capital", 100))
        trades = len(data)

    return jsonify({
        "capital": round(capital, 2),
        "profit": round(profit, 2),
        "trades": trades
    })

if __name__ == "__main__":
    app.run(debug=True)
