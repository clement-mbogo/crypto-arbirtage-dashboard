import time
import random
from binance_utils import place_market_order, load_binance_client
from backtest_control import is_backtest_mode
from database import log_trade
import json

# Simulate price fetching logic – replace with real logic if needed
def fetch_prices():
    # Example mock data
    return {
        "BTCUSDT": {
            "bid": round(random.uniform(29800, 30200), 2),
            "ask": round(random.uniform(29800, 30200), 2)
        },
        "ETHUSDT": {
            "bid": round(random.uniform(1850, 1900), 2),
            "ask": round(random.uniform(1850, 1900), 2)
        }
    }

def find_arbitrage_opportunities(prices):
    opportunities = []
    for symbol, data in prices.items():
        spread = data['ask'] - data['bid']
        profit_pct = (spread / data['bid']) * 100
        if profit_pct > 0.4:  # Arbitrage threshold (customize)
            opportunities.append({
                "symbol": symbol,
                "buy": data['bid'],
                "sell": data['ask'],
                "profit_pct": round(profit_pct, 2),
                "timestamp": time.time()
            })
    return opportunities

def execute_arbitrage(opportunity, stake_usdt):
    client = load_binance_client()
    symbol = opportunity['symbol']
    quantity = stake_usdt / opportunity['buy']
    trade_details = {
        "symbol": symbol,
        "buy_price": opportunity['buy'],
        "sell_price": opportunity['sell'],
        "quantity": round(quantity, 6),
        "profit_pct": opportunity['profit_pct'],
        "mode": "backtest" if is_backtest_mode() else "live",
        "timestamp": time.time()
    }

    if is_backtest_mode():
        print(f"[BACKTEST] Simulating trade: {json.dumps(trade_details, indent=2)}")
    else:
        try:
            # Place a real buy (and optionally sell) order
            place_market_order(symbol, "BUY", quantity)
            print(f"[LIVE TRADE] Executed BUY order for {symbol}, quantity={quantity}")
        except Exception as e:
            print(f"[ERROR] Live trade failed: {e}")
            return None

    # Log the trade
    log_trade(trade_details)
    return trade_details

def run_arbitrage_cycle(stake_usdt):
    prices = fetch_prices()
    opportunities = find_arbitrage_opportunities(prices)
    for opp in opportunities:
        print(f"[ALERT] Arbitrage found: {opp}")
        execute_arbitrage(opp, stake_usdt)
