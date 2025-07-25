import os
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
import random

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TRADE_MODE = os.getenv("TRADE_MODE", "paper").lower()


def load_binance_client():
    if TRADE_MODE == "live":
        return Client(API_KEY, API_SECRET)
    else:
        return None  # Paper mode


def get_balance(client, asset):
    if TRADE_MODE == "live":
        balances = client.get_asset_balance(asset=asset)
        return float(balances['free'])
    else:
        # Simulated paper balance
        paper_balances = {"USDT": 10000.0, "BTC": 1.0, "ETH": 5.0}
        return paper_balances.get(asset.upper(), 0.0)


def place_market_order(client, symbol, side, quantity):
    if TRADE_MODE == "live":
        try:
            order = client.order_market(
                symbol=symbol,
                side=side.upper(),
                quantity=quantity
            )
            return {"status": "executed", "order": order}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        # Simulated paper trade
        fake_price = round(random.uniform(20000, 40000), 2)
        timestamp = datetime.now().isoformat()
        return {
            "status": "simulated",
            "symbol": symbol,
            "side": side,
            "price": fake_price,
            "quantity": quantity,
            "timestamp": timestamp
        }
