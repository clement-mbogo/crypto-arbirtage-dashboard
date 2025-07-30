from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import os

def load_binance_client():
    key = os.getenv("BINANCE_API_KEY")
    secret = os.getenv("BINANCE_API_SECRET")
    if not key or not secret:
        raise ValueError("Set BINANCE_API_KEY and BINANCE_API_SECRET")
    return Client(key, secret)

def get_balance(client, asset="USDT"):
    b = client.get_asset_balance(asset=asset)
    return float(b["free"]) if b else 0.0

def place_market_order(client, symbol, side, quantity):
    return client.create_order(
        symbol=symbol,
        side=SIDE_BUY if side.upper()=="BUY" else SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=quantity
    )
