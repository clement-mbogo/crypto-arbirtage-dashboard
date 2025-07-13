from flask import Flask, render_template, jsonify, request
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import random, csv
import os

app = Flask(__name__)

# Database setup
Base = declarative_base()
db_path = "sqlite:///trades.db"
engine = create_engine(db_path)
Session = sessionmaker(bind=engine)
session = Session()

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    coin = Column(String)
    time = Column(DateTime)
    binance = Column(Float)
    kraken = Column(Float)
    diff = Column(Float)
    action = Column(String)
    profit = Column(Float)

Base.metadata.create_all(engine)

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

def arbitrage_logic(coin, base_price, strategy="random", use_ai=False):
    global simulated_pnl, capital
    binance = simulate_price(base_price)
    kraken = simulate_price(base_price)
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
        "profit": profit
    }

    coin_data[coin]["trades"].append(trade)

    db_trade = Trade(
        coin=coin,
        time=datetime.now(),
        binance=binance,
        kraken=kraken,
        diff=diff,
        action=action,
        profit=profit
    )
    session.add(db_trade)
    session.commit()

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

@app.route("/get_db_trades")
def get_db_trades():
    trades = session.query(Trade).order_by(Trade.id.desc()).limit(50).all()
    return jsonify([{
        "coin": t.coin,
        "time": t.time.strftime("%Y-%m-%d %H:%M:%S"),
        "binance": t.binance,
        "kraken": t.kraken,
        "diff": t.diff,
        "action": t.action,
        "profit": t.profit
    } for t in trades])

@app.route("/export_db")
def export_db():
    trades = session.query(Trade).all()
    with open("all_trades.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["coin", "time", "binance", "kraken", "diff", "action", "profit"])
        for t in trades:
            writer.writerow([t.coin, t.time, t.binance, t.kraken, t.diff, t.action, t.profit])
    return jsonify({"status": "exported to all_trades.csv"})

@app.route("/reset")
def reset():
    global backtest_logs, simulated_pnl, capital
    simulated_pnl = 0.0
    capital = 1000.0
    backtest_logs = []
    for coin in coins:
        coin_data[coin] = {"pnl": 0.0, "trades": [], "wins": 0}

    session.query(Trade).delete()
    session.commit()
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(debug=True)
