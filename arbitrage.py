# arbitrage.py

import logging
import random
from datetime import datetime

from binance_utils import load_binance_client, get_price
from database import log_trade
from notifier import send_telegram_message
from backtest_control import is_backtest_enabled

def detect_arbitrage_opportunity(symbol: str):
    """
    Placeholder for real arbitrage detection logic.
    Returns a dict with buy/sell prices and profit percentage.
    """
    buy_price = round(random.uniform(29500, 30500), 2)
    sell_price = round(random.uniform(30600, 31500), 2)
    profit_percent = round((sell_price - buy_price) / buy_price * 100, 2)
    return {
        "symbol": symbol,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "profit_percent": profit_percent,
        "timestamp": datetime.utcnow().isoformat()
    }

def run_arbitrage(symbols=None, capital=100):
    """
    Check arbitrage opportunities for given symbols.
    In backtest mode, logs simulated trades.
    In live mode, sends Telegram alerts and logs real trades.
    """
    symbols = symbols or ["BTCUSDT", "ETHUSDT"]
    opportunities = []

    for symbol in symbols:
        opp = detect_arbitrage_opportunity(symbol)
        logging.info(f"Arbitrage check for {symbol}: {opp['profit_percent']}%")
        
        # Only act on sufficiently profitable opportunities
        if opp["profit_percent"] >= 1.0:
            opportunities.append(opp)

            # Log trade (backtest or real)
            log_trade(
                exchange_from="EX1",
                exchange_to="EX2",
                symbol=symbol,
                volume=capital / opp["buy_price"],
                profit=opp["profit_percent"]
            )

            # Send alert in live mode
            if not is_backtest_enabled():
                message = (
                    f"🚀 *Arbitrage Opportunity Detected!*\n"
                    f"Symbol: `{symbol}`\n"
                    f"Buy @ ${opp['buy_price']}\n"
                    f"Sell @ ${opp['sell_price']}\n"
                    f"Profit: {opp['profit_percent']}%\n"
                    f"Time: {opp['timestamp']}"
                )
                send_telegram_message(message)

    return opportunities
