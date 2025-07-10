from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from flask_mail import Mail, Message
from datetime import datetime
import time, os, json, sqlite3, io, csv
from threading import Thread
from binance.client import Client
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
mail = Mail(app)

app.config.update(
    MAIL_SERVER='smtp.sendgrid.net',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='apikey',
    MAIL_PASSWORD=os.getenv("SENDGRID_API_KEY", "your_sendgrid_api_key"),
    MAIL_DEFAULT_SENDER='no-reply@crypto-bot.com'
)
mail = Mail(app)

DB_PATH = 'trades.db'
SETTINGS_PATH = 'settings.json'

# === DATABASE INIT ===
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pair TEXT,
            buy_exchange TEXT,
            sell_exchange TEXT,
            buy_price REAL,
            sell_price REAL,
            profit REAL
        )''')
        conn.commit()
init_db()

# === SETTINGS INIT ===
def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        default_settings = {
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 1,
            "reinvest": True
        }
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(default_settings, f)
    with open(SETTINGS_PATH, 'r') as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(data, f)

# === DUMMY LIVE PRICES ===
@app.route("/get_prices")
def get_prices():
    prices = {
        "BTC": round(60000 + time.time() % 1000, 2),
        "ETH": round(3000 + time.time() % 100, 2)
    }
    return jsonify(prices)

# === GET SETTINGS ===
@app.route("/get_settings")
def get_settings():
    return jsonify(load_settings())

# === UPDATE SETTINGS ===
@app.route("/update_settings", methods=['POST'])
def update_settings():
    data = request.json
    save_settings(data)
    return jsonify({"status": "success"})

# === EXPORT CSV ===
@app.route('/export_csv')
def export_csv():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Pair', 'Buy Exchange', 'Sell Exchange', 'Buy Price', 'Sell Price', 'Profit'])
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='trades.csv')

# === GET CHART DATA ===
@app.route("/get_chart_data")
def get_chart_data():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, profit FROM trades")
        rows = cursor.fetchall()

    capital = 100
    points = []
    for row in rows:
        capital += row[1]
        points.append({"x": row[0], "y": round(capital, 2)})

    return jsonify(points)

# === BACKTEST (Mock) ===
@app.route("/backtest", methods=['POST'])
def backtest():
    return jsonify({"status": "backtest complete"})

# === HOME ===
@app.route("/")
def index():
    return render_template("dashboard.html")

# === RUN ===
if __name__ == '__main__':
    app.run(debug=True)
