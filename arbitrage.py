import logging
import random
from datetime import datetime

from binance_utils import load_binance_client
from database import log_trade
from notifier import send_telegram_message
from backtest_control import is_backtest_enabled

def detect_arbitrage_opportunity(symbol: str):
    """
    Simulates an arbitrage opportunity with random buy/sell prices.
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
    Run arbitrage detection and log/simulate trades depending on mode.
    """
    symbols = symbols or ["BTCUSDT", "ETHUSDT"]
    opportunities = []

    for symbol in symbols:
        opp = detect_arbitrage_opportunity(symbol)
        logging.info(f"Arbitrage check for {symbol}: {opp['profit_percent']}%")

        if opp["profit_percent"] >= 1.0:
            opportunities.append(opp)

            # Volume calculation
            volume = round(capital / opp["buy_price"], 6)

            # Log trade using correct argument order:
            # symbol, buy_exchange, sell_exchange, buy_price, sell_price, profit
            log_trade(
                symbol,
                "EX1",  # buy_exchange
                "EX2",  # sell_exchange
                opp["buy_price"],
                opp["sell_price"],
                opp["profit_percent"]
            )

            # Telegram alert if not in backtest mode
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
