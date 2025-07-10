from flask import Flask, render_template, request, jsonify, send_file
import json
import sqlite3
import time
from binance_utils import load_binance_client, get_balance, place_market_order

app = Flask(__name__)
DB_FILE = "trades.db"
SETTINGS_FILE = "settings.json"

# Load settings
def load_settings():
    with open(SETTINGS_FILE) as f:
        return json.load(f)

# Save settings
def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Binance
settings = load_settings()
binance_client = load_binance_client()

@app.route("/")
def dashboard():
    return render_template("dashboard.html", settings=settings)

@app.route("/settings", methods=["GET", "POST"])
def update_settings():
    if request.method == "POST":
        new_settings = request.json
        save_settings(new_settings)
        return jsonify({"message": "Settings saved"})
    else:
        return jsonify(load_settings())

@app.route("/binance_balance")
def binance_balance():
    try:
        usdt = get_balance(binance_client, "USDT")
        btc = get_balance(binance_client, "BTC")
        eth = get_balance(binance_client, "ETH")
        return jsonify({"USDT": usdt, "BTC": btc, "ETH": eth})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/trade_example")
def trade_example():
    result = place_market_order(binance_client, "BTCUSDT", "buy", 0.001)
    return jsonify(result)

@app.route("/real_growth")
def real_growth():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, capital, profit, trade_count FROM performance")
    data = cursor.fetchall()
    conn.close()
    result = {
        "timestamps": [row[0] for row in data],
        "capital": [row[1] for row in data],
        "profit": [row[2] for row in data],
        "trades": [row[3] for row in data],
    }
    return jsonify(result)

@app.route("/export_trades")
def export_trades():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades")
    rows = cursor.fetchall()
    conn.close()

    csv_path = "trades_export.csv"
    with open(csv_path, "w") as f:
        f.write("id,timestamp,pair,action,price,quantity,profit\n")
        for row in rows:
            f.write(",".join(str(x) for x in row) + "\n")
    return send_file(csv_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
