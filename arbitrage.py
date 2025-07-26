import time
from utils import fetch_prices
from notifier import send_telegram_alert
from database import store_trade
from backtest_control import is_backtest_enabled
from settings_manager import get_settings

def check_arbitrage_opportunities():
    settings = get_settings()
    if not settings.get("arbitrage_enabled", True):
        return

    prices = fetch_prices()
    if not prices:
        return

    # Example arbitrage logic: Buy where price is lowest, sell where price is highest
    min_exchange = min(prices, key=lambda x: x['price'])
    max_exchange = max(prices, key=lambda x: x['price'])

    profit_percent = ((max_exchange['price'] - min_exchange['price']) / min_exchange['price']) * 100

    if profit_percent >= settings.get("min_profit_threshold", 0.5):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        message = (
            f"📈 Arbitrage Opportunity\n\n"
            f"Buy from: {min_exchange['exchange']} at {min_exchange['price']}\n"
            f"Sell on: {max_exchange['exchange']} at {max_exchange['price']}\n"
            f"Profit: {profit_percent:.2f}%\n"
            f"Time: {timestamp}"
        )

        print("[INFO]", message)
        send_telegram_alert(message)

        if not is_backtest_enabled():
            store_trade(min_exchange, max_exchange, profit_percent, timestamp)
