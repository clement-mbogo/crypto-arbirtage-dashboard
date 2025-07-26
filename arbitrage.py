from binance_utils import get_price
from database import save_trade
from notifier import send_telegram_alert
from backtest_control import is_backtest_enabled

# Core arbitrage logic
def check_arbitrage_opportunities(symbols, capital):
    opportunities = []

    for symbol in symbols:
        price = get_price(symbol)
        if price is None:
            continue

        # Example logic: mock condition to simulate opportunity
        if price < 100:  # Simulate undervaluation
            opportunity = {
                "symbol": symbol,
                "price": price,
                "capital": capital,
                "type": "buy"
            }

            # Log or save if not backtesting
            if not is_backtest_enabled():
                save_trade(opportunity)
                send_telegram_alert(f"Arbitrage Opportunity Found: {symbol} at ${price:.2f}")

            opportunities.append(opportunity)

    return opportunities
