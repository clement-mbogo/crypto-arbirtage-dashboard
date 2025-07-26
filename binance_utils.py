from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
use_testnet = os.getenv("BINANCE_USE_TESTNET", "true").lower() == "true"

def load_binance_client():
    if use_testnet:
        binance_url = "https://testnet.binance.vision"
        client = Client(api_key, api_secret)
        client.API_URL = binance_url
    else:
        client = Client(api_key, api_secret)
    return client

client = load_binance_client()

def get_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def get_balance(asset):
    try:
        balance = client.get_asset_balance(asset=asset)
        return float(balance["free"])
    except Exception as e:
        print(f"Error fetching balance for {asset}: {e}")
        return None

def place_market_order(symbol, side, quantity):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )
        return order
    except Exception as e:
        print(f"Order failed: {e}")
        return None
