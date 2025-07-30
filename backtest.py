from database import insert_trade
from binance_utils import simulate_trade

def run_backtest(opportunity, capital):
    if not opportunity:
        return None

    # Simulate the trade using the opportunity and capital
    result = simulate_trade(opportunity, capital)

    # Record simulated trade in database
    insert_trade(
        asset=result["symbol"],
        capital=capital,
        profit=result["profit"],
        timestamp=result["timestamp"],
        is_backtest=True
    )

    return result
