from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from arbitrage import check_arbitrage_opportunities
from binance_utils import load_binance_client
from telegram_alert import send_telegram_alert
from database import store_trade, fetch_performance_data
from backtest_control import is_backtest_enabled
import json

app = Flask(__name__)
CORS(app)

# Load settings
with open("settings.json", "r") as f:
    settings = json.load(f)

scheduler = BackgroundScheduler()
scheduler.start()

# --- Periodic Arbitrage Check ---
def scheduled_arbitrage_check():
    print("🔁 Running scheduled arbitrage scan...")
    mode = "backtest" if is_backtest_enabled() else "live"
    client = load_binance_client(mode)
    results = check_arbitrage_opportunities(client, backtest=is_backtest_enabled())
    for result in results:
        send_telegram_alert(result)
        store_trade(result, mode=mode)

scheduler.add_job(scheduled_arbitrage_check, 'interval', seconds=settings["arbitrage_interval"])

# --- API Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/performance", methods=["GET"])
def api_performance():
    return jsonify(fetch_performance_data())

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "GET":
        return jsonify(settings)
    elif request.method == "POST":
        data = request.json
        settings.update(data)
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        return jsonify({"message": "Settings updated"})

@app.route("/api/backtest_toggle", methods=["POST"])
def api_toggle_backtest():
    from backtest_control import toggle_backtest
    toggle_backtest()
    return jsonify({"backtest": is_backtest_enabled()})

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "backtest": is_backtest_enabled(),
        "arbitrage_interval": settings.get("arbitrage_interval"),
    })

if __name__ == "__main__":
    app.run(debug=True, port=10000)
