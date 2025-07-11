from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "performance.db")

def fetch_data(source):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT timestamp, capital, profit, trade_count FROM performance WHERE source = ? ORDER BY timestamp"
    cursor.execute(query, (source,))
    rows = cursor.fetchall()
    conn.close()
    timestamps = [r[0] for r in rows]
    capital = [r[1] for r in rows]
    profit = [r[2] for r in rows]
    trade_count = [r[3] for r in rows]
    return {
        "timestamps": timestamps,
        "capital": capital,
        "profit": profit,
        "trade_count": trade_count
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/real_growth")
def real_growth():
    return jsonify(fetch_data("real"))

@app.route("/backtest_growth")
def backtest_growth():
    return jsonify(fetch_data("backtest"))

@app.route("/start_backtest")
def start_backtest():
    # Simulate starting process or invoke backend script
    return "Started"

@app.route("/stop_backtest")
def stop_backtest():
    # Simulate stopping process or invoke backend logic
    return "Stopped"

if __name__ == "__main__":
    app.run(debug=True)
