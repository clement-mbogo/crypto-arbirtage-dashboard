import os
import json
import sqlite3
import random
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
from dotenv import load_dotenv
load_dotenv()

# === CONFIGURATION ===
SETTINGS_FILE = 'settings.json'
DB_FILE = 'trades.db'
HISTORICAL_PRICES_FILE = 'historical_prices.json'

app = Flask(__name__)
app.secret_key = 'your-secret-key'
PAIRS = ['BTC', 'ETH']

# === LOAD/INIT SETTINGS ===
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default = {
            "pair": "BTC",
            "stake": 5,
            "target_profit": 5,
            "max_trades": 20,
            "cooldown": 60,
            "reinvest": True,
            "mode": "paper"
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default, f)
    with open(SETTINGS_FILE) as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f)

# === DB SETUP ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS trades (
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
    conn.close()

init_db()

# === GLOBAL STATE ===
bot_running = False
bot_thread = None

# === PRICE FETCHING ===
def fetch_binance_prices():
    try:
        res = requests.get('https://api.binance.com/api/v3/ticker/price?symbols=["BTCUSDT","ETHUSDT"]').json()
        return {
            'BTC': float([x for x in res if x['symbol'] == 'BTCUSDT'][0]['price']),
            'ETH': float([x for x in res if x['symbol'] == 'ETHUSDT'][0]['price'])
        }
    except:
        return {'BTC': 0, 'ETH': 0}

def fetch_kucoin_prices():
    try:
        res = requests.get('https://api.kucoin.com/api/v1/market/allTickers').json()
        tickers = res['data']['ticker']
        btc = next(item for item in tickers if item['symbolName'] == 'BTC-USDT')
        eth = next(item for item in tickers if item['symbolName'] == 'ETH-USDT')
        return {
            'BTC': float(btc['last']),
            'ETH': float(eth['last'])
        }
    except:
        return {'BTC': 0, 'ETH': 0}

def fetch_coingecko_prices():
    try:
        result = requests.get('https://api.coingecko.com/api/v3/simple/price', params={
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd'
        }).json()
        return {
            'BTC': result['bitcoin']['usd'],
            'ETH': result['ethereum']['usd']
        }
    except:
        return {'BTC': 0, 'ETH': 0}

def get_prices():
    return {
        'coingecko': fetch_coingecko_prices(),
        'binance': fetch_binance_prices(),
        'kucoin': fetch_kucoin_prices()
    }

# === TELEGRAM ALERT ===
def send_telegram_alert(message):
    try:
        token = os.getenv("TG_BOT_TOKEN") or "your_bot_token"
        chat_id = os.getenv("TG_CHAT_ID") or "your_chat_id"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {'chat_id': chat_id, 'text': message}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram alert error:", e)

# === TRADING SIMULATION LOOP ===
def run_bot():
    global bot_running
    while bot_running:
        settings = load_settings()
        prices = get_prices()['binance']
        coin = settings['pair']
        price = prices.get(coin, 0)
        if price == 0:
            time.sleep(settings['cooldown'])
            continue

        spread = round(random.uniform(0.5, 2.5), 2)
        if spread >= settings['target_profit']:
            profit = round((spread / 100) * settings['stake'], 2)
            now = datetime.now().isoformat()
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute('''INSERT INTO trades (timestamp, pair, buy_exchange, sell_exchange, buy_price, sell_price, profit)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (now, coin, "Binance", "KuCoin",
                         price * (1 - spread / 200),
                         price * (1 + spread / 200),
                         profit))
            conn.commit()
            conn.close()
            send_telegram_alert(f"📈 {coin} Arbitrage executed!\nProfit: ${profit:.2f}")
        time.sleep(settings['cooldown'])

# === BACKTEST LOGIC ===
def load_historical_prices():
    try:
        with open(HISTORICAL_PRICES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Error loading historical prices:", e)
        return []

@app.route('/backtest', methods=['POST'])
def backtest():
    settings = load_settings()
    target_profit = settings.get('target_profit', 5)
    stake = settings.get('stake', 5)
    pair = settings.get('pair', 'BTC')

    prices = load_historical_prices()
    trades = []
    total_profit = 0

    for price_point in prices:
        price = price_point.get(pair)
        if not price:
            continue

        spread = round(random.uniform(0.5, 2.5), 2)

        if spread >= target_profit:
            profit = round((spread / 100) * stake, 2)
            trades.append({
                'timestamp': price_point['timestamp'],
                'pair': pair,
                'buy_price': round(price * (1 - spread / 200), 2),
                'sell_price': round(price * (1 + spread / 200), 2),
                'profit': profit
            })
            total_profit += profit

    result = {
        'total_trades': len(trades),
        'total_profit': round(total_profit, 2),
        'average_profit_per_trade': round(total_profit / len(trades), 2) if trades else 0,
        'trades': trades
    }

    return jsonify({'status': 'ok', 'result': result})

# === ROUTES ===
@app.route('/')
def index():
    if not session.get("user"):
        return redirect(url_for('login'))
    settings = load_settings()
    prices = get_prices()
    return render_template('dashboard.html', prices=prices, settings=settings, pairs=PAIRS)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    save_settings(data)
    return jsonify({'status': 'success'})

@app.route('/get_settings')
def get_settings():
    return jsonify(load_settings())

@app.route('/get_prices')
def live_prices():
    return jsonify(get_prices())

@app.route('/get_trades')
def get_trades():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM trades ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/get_chart_data')
def get_chart_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, profit FROM trades ORDER BY timestamp")
    rows = cur.fetchall()
    data = []
    capital = 0
    for idx, row in enumerate(rows):
        capital += row[1]
        data.append({
            'timestamp': row[0],
            'capital': round(capital, 2),
            'profit': round(row[1], 2),
            'trade_count': idx + 1
        })
    return jsonify(data)

@app.route('/start_bot')
def start_bot():
    global bot_running, bot_thread
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()
    return jsonify({'status': 'started'})

@app.route('/stop_bot')
def stop_bot():
    global bot_running
    bot_running = False
    return jsonify({'status': 'stopped'})

@app.route('/export_trades')
def export_trades():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM trades")
    rows = cur.fetchall()
    csv = "timestamp,pair,buy_exchange,sell_exchange,buy_price,sell_price,profit\n"
    for row in rows:
        csv += ",".join(map(str, row[1:])) + "\n"
    return csv, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename="trades.csv"'
    }

@app.route('/real_growth')
def real_growth():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, profit FROM trades ORDER BY timestamp")
    rows = cur.fetchall()
    data = []
    capital = 0
    for row in rows:
        capital += row[1]
        data.append(round(capital, 2))
    return jsonify(data)

# === AUTH ROUTES ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Simple login stub (for demo). Replace with proper auth.
    session['user'] = 'admin'
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# === BINANCE TESTNET SETUP ===
from binance.client import Client

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
binance_client.API_URL = 'https://testnet.binance.vision/api'

@app.route('/binance_balance')
def binance_balance():
    try:
        balances = binance_client.get_account()['balances']
        clean = {b['asset']: float(b['free']) for b in balances if float(b['free']) > 0}
        return jsonify(clean)
    except Exception as e:
        return jsonify({'error': str(e)})

# === MAIN RUN ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
