from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/prices')
def get_prices():
    try:
        # Example with CoinGecko API (no key required)
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd", timeout=10)
        response.raise_for_status()
        data = response.json()

        prices = {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"]
        }
        return jsonify(prices)

    except Exception as e:
        print(f"Error fetching prices: {e}")
        return jsonify({"error": "Failed to fetch prices"}), 500


# Optional test route
@app.route('/ping')
def ping():
    return jsonify({"status": "OK"})


if __name__ == '__main__':
    app.run(debug=True)
