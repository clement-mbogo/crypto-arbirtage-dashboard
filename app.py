from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random, csv, requests

app = Flask(__name__)

capital = 1000.0
simulated_pnl = 0.0
backtest_logs = []

coins = ["BTC", "ETH", "BNB", "SOL"]

coin_data = {
    "BTC": {"pnl": 0.0, "trades": [], "wins": 0},
    "ETH": {"pnl": 0.0, "trades": [], "wins": 0},
    "BNB": {"pnl": 0.0, "trades": [], "wins": 0},
    "SOL": {"pnl": 0.0, "trades": [], "wins": 0},
}

def simulate_price(base=100, spread=3):
    return round(base + random.uniform(-spread, spread), 2)

def get_real_prices(coin):
    try:
        coin_symbol = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "BNB": "BNBUSDT",
            "SOL": "SOLUSDT"
        }[coin]

        # Binance price
        binance_url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin_symbol}"
        binance_price = float(requests.get(binance_url, timeout=3).json()["price"])

        # Kraken price
        kraken_symbol = {
            "BTC": "XBTUSD",
            "ETH": "ETHUSD",
            "BNB": "BNBUSD",
            "SOL": "SOLUSD"
        }[coin]
        kraken_url = f"https://api.kraken.com/0/public/Ticker?pair={kraken_symbol}"
        kraken_data = requests.get(kraken_url, timeout=3).json()
        kraken_price = float(kraken_data["result"][list(kraken_data["result"].keys())[0]]["c"][0])

        return binance_price, kraken_price
    except Exception as e:
        print(f"[ERROR] Price fetch failed: {e}")
        return simulate_price(), simulate_price()

def arbitrage_logic(coin, base_price, strategy="random", use_ai=False):
    global simulated_pnl, capital
    binance, kraken = get_real_prices(coin)
    diff = round(abs(binance - kraken), 2)
    threshold = 1.0

    profit = 0
    action = "Hold"

    if use_ai:
        total_trades = len(coin_data[coin]["trades"])
        win_rate = (coin_data[coin]["wins"] / total_trades) * 100 if total_trades else 0
        threshold = 0.75 if win_rate > 60 else 1.2

    if diff > threshold:
        profit = round(diff * 0.5, 2)
        simulated_pnl += profit
        coin_data[coin]["pnl"] += profit
        capital += profit
        coin_data[coin]["wins"] += 1
        action = f"AI Arb +${profit}" if use_ai else f"Arbitrage +${profit}"

    trade = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "Binance": binance,
        "Kraken": kraken,
        "Diff": diff,
        "Action": action,
    }
    coin_data[coin]["trades"].append({**trade, "profit": profit})
    return trade

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_backtest")
def run_backtest():
    base_prices = {"BTC": 29000, "ETH": 1900, "BNB": 250, "SOL": 70}
    strategy = request.args.get("strategy", "random")
    steps = int(request.args.get("steps", 1))
    use_ai = request.args.get("ai", "false").lower() == "true"

    for _ in range(steps):
        row = {"time": datetime.now().strftime("%H:%M:%S")}
        for coin in coins:
            t = arbitrage_logic(coin, base_prices[coin], strategy=strategy, use_ai=use_ai)
            for k, v in t.items():
                row[f"{coin}_{k}"] = v
        backtest_logs.append(row)

    return jsonify({"status": "running"})

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
        "logs": backtest_logs[-20:],
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

# Shared log saving function
def save_log(coin):
    trades = coin_data[coin]["trades"]
    if trades:
        with open(f"{coin.lower()}_log.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=trades[0].keys())
            writer.writeheader()
            writer.writerows(trades)
    return jsonify({"status": f"{coin} log saved"})

# Individual routes for each coin
@app.route("/save_btc_log")
def save_btc_log():
    return save_log("BTC")

@app.route("/save_eth_log")
def save_eth_log():
    return save_log("ETH")

@app.route("/save_bnb_log")
def save_bnb_log():
    return save_log("BNB")

@app.route("/save_sol_log")
def save_sol_log():
    return save_log("SOL")

if __name__ == "__main__":
    app.run(debug=True)
