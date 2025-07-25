# app.py
from flask import Flask, jsonify
from scheduler import start_scheduler
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Binance Arbitrage Bot Running"

if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))


# trade_executor.py
from binance_utils import load_binance_client
from telegram_alert import send_telegram_message
import os

PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

# Dummy balance store for paper trades
virtual_balances = {}

def execute_trade(symbol, side, quantity):
    if PAPER_TRADING:
        virtual_balances[symbol] = virtual_balances.get(symbol, 0) + (quantity if side == 'BUY' else -quantity)
        msg = f"[PAPER] {side} {quantity} of {symbol}. New virtual balance: {virtual_balances[symbol]:.4f}"
        send_telegram_message(msg)
        return {"paper_trade": True, "symbol": symbol, "side": side, "quantity": quantity}

    client = load_binance_client()
    try:
        order = client.create_order(
            symbol=symbol,
            side=side.upper(),
            type='MARKET',
            quantity=quantity
        )
        send_telegram_message(f"Executed {side} order on {symbol} for {quantity}")
        return order
    except Exception as e:
        send_telegram_message(f"Trade error: {str(e)}")
        return {"error": str(e)}


# arbitrage.py
from trade_executor import execute_trade
from binance_utils import load_binance_client

THRESHOLD = 0.5  # % gain

def find_arbitrage_opportunity():
    client = load_binance_client()
    tickers = client.get_all_tickers()
    for ticker in tickers:
        symbol = ticker['symbol']
        price = float(ticker['price'])
        if 'BTC' in symbol and price > 100:
            execute_trade(symbol, 'BUY', 0.001)


# telegram_alert.py
import requests

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)


# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from arbitrage import find_arbitrage_opportunity

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(find_arbitrage_opportunity, 'interval', seconds=60)
    scheduler.start()


# binance_utils.py
from binance.client import Client
import os

def load_binance_client():
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    return Client(api_key, api_secret)


# settings.json
{
  "stake_percentage": 10,
  "trade_interval": 60,
  "threshold": 0.5
}


# requirements.txt
flask
python-binance
apscheduler
requests


# Procfile
web: python app.py
