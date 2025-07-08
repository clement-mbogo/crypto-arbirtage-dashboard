from flask import Flask, render_template, request, redirect, jsonify, send_file
import os
import json
import datetime
import time
import threading
import sqlite3
import requests

app = Flask(__name__)

# --- SETTINGS ---
SETTINGS_PATH = "settings.json"
DB_PATH = "trades.db"

# --- ROUTES ---

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/prices")
def live_prices():
    try:
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        eth = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()
        return jsonify({
            "BTC": btc["bitcoin"]["usd"],
            "ETH": eth["ethereum"]["usd"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analytics")
def analytics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), AVG(profit), SUM(profit) FROM trades")
    total, avg_profit, total_profit = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM trades WHERE profit > 0")
    wins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades WHERE profit < 0")
    losses = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(profit), MIN(profit) FROM trades")
    best, worst = cursor.fetchone()

    cursor.execute("""
        SELECT strftime('%Y-%m-%d', timestamp) AS day, SUM(profit)
        FROM trades
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """)
    daily = cursor.fetchall()

    conn.close()

    return jsonify({
        "total": total or 0,
        "avg_profit": round(avg_profit or 0, 4),
        "total_profit": round(total_profit or 0, 4),
        "wins": wins or 0,
        "losses": losses or 0,
        "win_ratio": round((wins / total), 2) if total else 0,
        "best_trade": round(best or 0, 4),
        "worst_trade": round(worst or 0, 4),
        "daily": [{"date": d, "profit": round(p, 4)} for d, p in daily]
    })

if __name__ == "__main__":
    app.run(debug=True)
