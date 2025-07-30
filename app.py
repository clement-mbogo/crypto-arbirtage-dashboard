import os
import json
import logging
import sqlite3
from threading import Thread
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv

from binance_utils import load_binance_client, get_balance, place_market_order
from arbitrage import run_arbitrage
from database import (
    init_db,
    fetch_all_trades,
    fetch_performance_data as fetch_latest_performance,
)
from performance import fetch_performance_history
from notifier import send_telegram_message
from scheduler import run_scheduler
from backtest_control import toggle_backtest, is_backtest_enabled

# Load env
load_dotenv()

# Config
API_KEY = os.getenv("API_AUTH_KEY", "mysecret")
DB_FILE = os.getenv("DB_FILE", "trades.db")

# App setup
app = Flask(__name__)
CORS(app)
Swagger(app)

# Ensure DB tables exist
init_db()

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Auth decorator
def require_auth(fn):
    def wrapper(*args, **kwargs):
        if request.headers.get("x-api-key") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# Routes

@app.route("/")
def index():
    return jsonify({"message": "Crypto Arbitrage Dashboard API running"}), 200

@app.route("/api/run_arbitrage", methods=["POST"])
@require_auth
def api_run_arbitrage():
    data = request.get_json() or {}
    symbols = data.get("symbols", [])
    capital = data.get("capital", 100)
    try:
        opps = run_arbitrage(symbols, capital)
        return jsonify({
            "mode": "backtest" if is_backtest_enabled() else "live",
            "opportunities": opps
        })
    except Exception as e:
        logging.error(f"run_arbitrage error: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/balance/<asset>", methods=["GET"])
@require_auth
def api_balance(asset):
    client = load_binance_client()
    bal = get_balance(client, asset)
    return jsonify({"asset": asset, "balance": bal})

@app.route("/api/performance", methods=["GET"])
@require_auth
def api_performance():
    return jsonify(fetch_latest_performance())

@app.route("/api/performance/history", methods=["GET"])
@require_auth
def api_performance_history():
    # Optional limit query param
    limit = int(request.args.get("limit", 100))
    return jsonify(fetch_performance_history(limit))

@app.route("/api/trades", methods=["GET"])
@require_auth
def api_trades():
    return jsonify(fetch_all_trades())

@app.route("/api/toggle_backtest", methods=["POST"])
@require_auth
def api_toggle_backtest():
    eb = toggle_backtest()
    return jsonify({"backtest_enabled": eb})

@app.route("/api/send_alert", methods=["POST"])
@require_auth
def api_send_alert():
    data = request.get_json() or {}
    msg = data.get("message", "")
    send_telegram_message(msg)
    return jsonify({"status": "sent"})

@app.route("/api/download_trades", methods=["GET"])
@require_auth
def api_download_trades():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades")
    rows = cursor.fetchall()
    conn.close()

    csv = "id,timestamp,exchange_from,exchange_to,symbol,volume,profit\n"
    for r in rows:
        csv += ",".join(map(str, r)) + "\n"

    return (csv, 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=trades.csv"
    })

# Start scheduler in background
Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
