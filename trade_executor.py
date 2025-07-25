# trade_executor.py

import os
from datetime import datetime
from dotenv import load_dotenv
from database import Trade, SessionLocal
from binance.client import Client
from binance.exceptions import BinanceAPIException

load_dotenv()

# Determine mode
LIVE_MODE = os.getenv("LIVE_MODE", "false").lower() == "true"

# Load Binance client
binance_client = Client(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET")
)

def log_trade(pair, action, price, quantity, profit=0.0):
    session = SessionLocal()
    trade = Trade(
        timestamp=datetime.utcnow(),
        pair=pair,
        action=action,
        price=price,
        quantity=quantity,
        profit=profit
    )
    session.add(trade)
    session.commit()
    session.close()

def execute_trade(pair: str, action: str, quantity: float):
    """
    Executes a live or paper trade depending on LIVE_MODE.
    Logs trade to DB either way.
    """
    try:
        if LIVE_MODE:
            # Execute actual trade
            if action == "buy":
                order = binance_client.order_market_buy(symbol=pair, quantity=quantity)
            else:
                order = binance_client.order_market_sell(symbol=pair, quantity=quantity)

            price = float(order['fills'][0]['price'])
            log_trade(pair, action, price, quantity)
            return {"status": "live", "price": price, "qty": quantity}

        else:
            # Simulate price and log paper trade
            ticker = binance_client.get_symbol_ticker(symbol=pair)
            price = float(ticker["price"])
            log_trade(pair, action, price, quantity)
            return {"status": "paper", "price": price, "qty": quantity}

    except BinanceAPIException as e:
        return {"error": str(e)}
    except Exception as ex:
        return {"error": f"Trade failed: {str(ex)}"}
