from flask import Flask, render_template, jsonify
import requests
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# Cache to avoid CoinGecko rate limits
price_cache = {
    "data": {},
    "timestamp": 0,
    "ttl": 60  # cache time-to-live in seconds
}


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/prices')
def get_prices():
    current_time = time.time()

    # Use cache if data is recent
    if current_time - price_cache["timestamp"] < price_cache["ttl"]:
        return jsonify(price_cache["data"])

    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        prices = {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"]
        }

        # Store in cache
        price_cache["data"] = prices
        price_cache["timestamp"] = current_time

        return jsonify(prices)

    except Exception as e:
        print(f"Error fetching prices: {e}")
        return jsonify({"error": "Failed to fetch prices"}), 500


@app.route('/ping')
def ping():
    return jsonify({"status": "OK"})


if __name__ == '__main__':
    app.run(debug=True)
