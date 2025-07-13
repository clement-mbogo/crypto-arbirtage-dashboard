from flask import Flask, render_template, jsonify, request
from datetime import datetime
from dotenv import load_dotenv
import os, random, csv, threading, time, requests

load_dotenv()

app = Flask(__name__)

# === Config ===
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TELEGRAM_THRESHOLD = 10

capital = 1000.0
simulated_pnl = 0.0
backtest_logs = []
coins = ["BTC", "ETH", "BNB", "SOL"]

coin_data = {coin: {"pnl": 0.0, "trades": [], "wins": 0} for coin in coins}

# === Helpers ===
def simulate_price(base=100, spread=3):
    return round(base + random.uniform(-spread, spread), 2)

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TG_CHAT_ID, "text": message})
    except Exception as e:
        print(f"[Telegram Error] {e}")

def arbitrage_logic(coin, base_price, strategy="random"):
    global simulated_pnl, capital
    binance = simulate_price(base_price)
    kraken = simulate_price(base_price)

    if strategy == "threshold":
        binance += 1.5
    elif strategy == "spread":
        binance += random.uniform(0, 3)
        kraken -= random.uniform(0, 3)

    diff = round(abs(binance - kraken), 2)
    threshold = 1.0
    profit = 0
    action = "Hold"

    if diff > threshold:
        profit = round(diff * 0.5, 2)
        simulated_pnl += profit
        coin_data[coin]["pnl"] += profit
        capital += profit
        coin_data[coin]["wins"] += 1
        action = f"Arbitrage +${profit}"
        if profit >= TELEGRAM_THRESHOLD:
            send_telegram_alert(f"🚨 {coin} arbitrage profit: ${profit} (Diff: {diff})")

    trade = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "Binance": binance,
        "Kraken": kraken,
        "Diff": diff,
        "Action": action,
        "profit": profit
    }
    coin_data[coin]["trades"].append(trade)
    return trade

def auto_save_logs(interval=60):
    def loop():
        while True:
            for coin in coins:
                trades = coin_data[coin]["trades"]
                if trades:
                    with open(f"{coin.lower()}_autosave.csv", "w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                        writer.writeheader()
                        writer.writerows(trades)
            print("[Auto-Save] Logs saved.")
            time.sleep(interval)
    threading.Thread(target=loop, daemon=True).start()

# === Routes ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_backtest")
def run_backtest():
    base_prices = {"BTC": 29000, "ETH": 1900, "BNB": 250, "SOL": 70}
    strategy = request.args.get("strategy", "random")
    steps = int(request.args.get("steps", 1))

    for _ in range(steps):
        row = {"time": datetime.now().strftime("%H:%M:%S")}
        for coin in coins:
            t = arbitrage_logic(coin, base_prices[coin], strategy)
            for k, v in t.items():
                row[f"{coin}_{k}"] = v
        backtest_logs.append(row)

    return jsonify({"status": f"{strategy} strategy run for {steps} steps"})

@app.route("/get_backtest_logs")
def get_logs():
    summaries = {}
    for coin in coins:
        trades = coin_data[coin]["trades"]
        pnl = coin_data[coin]["pnl"]
        wins = coin_data[coin]["wins"]
        summaries[f"{coin.lower()}_summary"] = {
            "trades": len(trades),
            "wins": wins,
            "win_rate": round((wins / len(trades)) * 100, 2) if trades else 0,
            "total": round(pnl, 2),
            "avg": round(pnl / len(trades), 2) if trades else 0,
        }
        summaries[f"{coin.lower()}_pnl"] = round(pnl, 2)

    return jsonify({
        "logs": backtest_logs[-50:],
        "pnl": round(simulated_pnl, 2),
        "capital": round(capital, 2),
        **summaries
    })

@app.route("/reset")
def reset():
    global backtest_logs, simulated_pnl, capital
    simulated_pnl = 0.0
    capital = 1000.0
    backtest_logs = []
    for coin in coins:
        coin_data[coin] = {"pnl": 0.0, "trades": [], "wins": 0}
    return jsonify({"status": "reset"})

@app.route("/save_<coin>_log")
def save_log(coin):
    coin = coin.upper()
    trades = coin_data[coin]["trades"]
    if trades:
        with open(f"{coin.lower()}_log.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=trades[0].keys())
            writer.writeheader()
            writer.writerows(trades)
    return jsonify({"status": f"{coin} log saved"})

if __name__ == "__main__":
    auto_save_logs(interval=60)
    app.run(debug=True)
