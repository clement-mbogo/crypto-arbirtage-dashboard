import json
from binance.client import Client

SETTINGS_FILE = "settings.json"

def load_settings():
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def load_binance_client():
    settings = load_settings()
    api_key = settings["binance"]["api_key"]
    api_secret = settings["binance"]["api_secret"]
    return Client(api_key, api_secret, testnet=settings["binance"].get("use_testnet", True))

def get_balance(client, asset="USDT"):
    try:
        balance_info = client.get_asset_balance(asset=asset)
        return float(balance_info["free"])
    except Exception as e:
        print("❌ Failed to get balance:", str(e))
        return 0.0

def place_market_order(client, symbol, side, quantity):
    try:
        order = client.order_market(
            symbol=symbol,
            side=side.upper(),
            quantity=quantity
        )
        return order
    except Exception as e:
        print("❌ Order failed:", str(e))
        return None
