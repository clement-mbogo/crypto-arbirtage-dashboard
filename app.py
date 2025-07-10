from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
from binance.client import Client
import time, threading, json, sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load user settings from JSON
SETTINGS_FILE = 'settings.json'
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({
                "stake": 5,
                "target_profit": 5,
                "max_trades": 20,
                "cooldown": 60,
                "reinvest": True,
                "live_mode": False,
                "api_key": "",
                "api_secret": ""
            }, f)
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

settings = load_settings()

# Initialize Binance clients
binance_client_live = None
binance_client_paper = Client(api_key='', api_secret='')

# DB Setup
conn = sqlite3.connect('trades.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades
             (id INTEGER PRIMARY KEY, timestamp TEXT, pair TEXT, buy_price REAL, sell_price REAL, profit REAL, mode TEXT)''')
conn.commit()

# Utility
def log_trade(pair, buy, sell, profit, mode):
    c.execute("INSERT INTO trades (timestamp, pair, buy_price, sell_price, profit, mode) VALUES (?, ?, ?, ?, ?, ?)",
              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pair, buy, sell, profit, mode))
    conn.commit()

def get_binance_client():
    if settings['live_mode']:
        return Client(api_key=settings['api_key'], api_secret=settings['api_secret'])
    return binance_client_paper

# Arbitrage Logic
trading_active = False

def run_bot():
    global trading_active
    client = get_binance_client()
    while trading_active:
        # Simulated price logic (replace with real API calls)
        btc_price = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        eth_price = float(client.get_symbol_ticker(symbol="ETHUSDT")['price'])

        spread = abs(btc_price - eth_price)
        if spread > settings['target_profit']:
            profit = spread
            if settings['live_mode']:
                # Real Trade Execution
                try:
                    order = client.order_market_buy(symbol="BTCUSDT", quantity=settings['stake'])
                    log_trade("BTCUSDT", btc_price, btc_price + profit, profit, "live")
                except Exception as e:
                    print("Live trade error:", e)
            else:
                # Paper trade log
                log_trade("BTCUSDT", btc_price, btc_price + profit, profit, "paper")

        time.sleep(settings['cooldown'])

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/start')
def start_bot():
    global trading_active
    trading_active = True
    threading.Thread(target=run_bot).start()
    return "Bot started"

@app.route('/stop')
def stop_bot():
    global trading_active
    trading_active = False
    return "Bot stopped"

@app.route('/update_settings', methods=['POST'])
def update_settings():
    global settings
    new_data = request.json
    settings.update(new_data)
    save_settings(settings)
    return jsonify({"status": "updated"})

@app.route('/get_settings')
def get_settings():
    return jsonify(settings)

@app.route('/get_prices')
def get_prices():
    client = get_binance_client()
    try:
        btc = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        eth = float(client.get_symbol_ticker(symbol="ETHUSDT")['price'])
        return jsonify({"BTC": btc, "ETH": eth})
    except:
        return jsonify({"BTC": 0, "ETH": 0})

@app.route('/get_chart_data')
def get_chart_data():
    c.execute("SELECT timestamp, profit FROM trades")
    rows = c.fetchall()
    return jsonify(rows)

@app.route('/backtest', methods=['POST'])
def backtest():
    return jsonify({"status": "completed"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        return redirect(url_for('home'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
