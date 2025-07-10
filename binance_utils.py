from binance.client import Client
from binance.enums import *
import json

def load_binance_client(settings_path="settings.json"):
    with open(settings_path) as f:
        config = json.load(f)

    api_key = config.get("api_key")
    api_secret = config.get("api_secret")
    use_testnet = config.get("use_testnet", True)

    client = Client(api_key, api_secret)
    if use_testnet:
        client.API_URL = 'https://testnet.binance.vision/api'
    return client

def get_balance(client, asset='USDT'):
    try:
        balance = client.get_asset_balance(asset=asset)
        return float(balance['free']) if balance else 0.0
    except Exception as e:
        print("Error fetching balance:", e)
        return 0.0

def place_market_order(client, symbol, side, quantity):
    try:
        return client.create_order(
            symbol=symbol,
            side=SIDE_BUY if side.lower() == 'buy' else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
    except Exception as e:
        print("Error placing order:", e)
        return None
