from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import os

def load_binance_client():
    key = os.getenv("BINANCE_API_KEY")
    secret = os.getenv("BINANCE_API_SECRET")
    if not key or not secret:
        raise ValueError("Set BINANCE_API_KEY and BINANCE_API_SECRET")
    return Client(key, secret)

def get_price(client, symbol: str) -> float:
    """
    Fetch the current market price for a symbol.
    """
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])

def get_balance(client, asset="USDT") -> float:
    """
    Return the free balance for the given asset.
    """
    b = client.get_asset_balance(asset=asset)
    return float(b["free"]) if b else 0.0

def place_market_order(client, symbol: str, side: str, quantity: float):
    """
    Place a MARKET order on Binance.
    """
    return client.create_order(
        symbol=symbol,
        side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=quantity
    )
