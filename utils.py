import requests

EXCHANGES = [
    {"name": "Binance", "url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"},
    {"name": "Coinbase", "url": "https://api.coinbase.com/v2/prices/spot?currency=USD"},
    {"name": "Kraken", "url": "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"},
]

def fetch_prices():
    prices = []
    for exchange in EXCHANGES:
        try:
            if exchange["name"] == "Binance":
                response = requests.get(exchange["url"])
                data = response.json()
                price = float(data["price"])
            elif exchange["name"] == "Coinbase":
                response = requests.get(exchange["url"])
                data = response.json()
                price = float(data["data"]["amount"])
            elif exchange["name"] == "Kraken":
                response = requests.get(exchange["url"])
                data = response.json()
                price = float(data["result"]["XXBTZUSD"]["c"][0])
            else:
                continue

            prices.append({
                "exchange": exchange["name"],
                "price": price
            })
        except Exception as e:
            print(f"[ERROR] Failed to fetch from {exchange['name']}: {e}")
    return prices
