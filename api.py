from flask import Flask, request, jsonify, render_template
from arbitrage import check_arbitrage_opportunities
from binance_utils import load_binance_client, get_balance, place_market_order
from database import fetch_performance_data, fetch_all_trades
from backtest_control import is_backtest_enabled, toggle_backtest
from alerts import send_telegram_alert
from flask_swagger_ui import get_swaggerui_blueprint
import os
import json

app = Flask(__name__)

# Swagger documentation
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Crypto Arbitrage API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Frontend dashboard
@app.route('/')
def dashboard():
    return render_template('index.html')

# Toggle backtest mode
@app.route('/api/toggle_backtest', methods=['POST'])
def toggle_backtest_api():
    try:
        data = request.get_json()
        if data is None or 'enabled' not in data:
            return jsonify({"error": "'enabled' field is required"}), 400
        enabled = data.get('enabled')
        toggle_backtest(enabled)
        return jsonify({"message": "Backtest mode toggled", "enabled": enabled})
    except Exception as e:
        return jsonify({"error": "Failed to toggle backtest mode", "details": str(e)}), 500

# Check backtest status
@app.route('/api/check_backtest')
def check_backtest_status():
    try:
        status = is_backtest_enabled()
        return jsonify({"backtest_enabled": status})
    except Exception as e:
        return jsonify({"error": "Failed to check backtest status", "details": str(e)}), 500

# Fetch performance metrics
@app.route('/api/performance')
def get_performance():
    try:
        data = fetch_performance_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Failed to fetch performance data", "details": str(e)}), 500

# Fetch all trades
@app.route('/api/trades')
def get_trades():
    try:
        data = fetch_all_trades()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Failed to fetch trades", "details": str(e)}), 500

# Send Telegram alert manually
@app.route('/api/alerts', methods=['POST'])
def send_alert():
    try:
        data = request.get_json()
        if not data or 'message' not in data or not data['message']:
            return jsonify({"error": "Message is required"}), 400
        message = data['message']
        send_telegram_alert(message)
        return jsonify({"status": "Alert sent"})
    except Exception as e:
        return jsonify({"error": "Failed to send alert", "details": str(e)}), 500

# Execute real Binance trade
@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request JSON required"}), 400

        symbol = data.get('symbol')
        side = data.get('side')
        quantity = data.get('quantity')

        # Validate required fields
        if not symbol or not side or not quantity:
            return jsonify({"error": "Missing required parameters: symbol, side, quantity"}), 400

        client = load_binance_client()
        response = place_market_order(client, symbol, side, quantity)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "Failed to execute trade", "details": str(e)}), 500

# Run arbitrage opportunity check
@app.route('/api/arbitrage')
def check_arbitrage():
    try:
        symbols = request.args.getlist("symbols") or ["BTCUSDT", "ETHUSDT"]
        capital_str = request.args.get("capital", "100")
        try:
            capital = float(capital_str)
        except ValueError:
            return jsonify({"error": "Invalid capital value"}), 400

        opportunities = check_arbitrage_opportunities(symbols, capital)
        return jsonify(opportunities)
    except Exception as e:
        return jsonify({"error": "Failed to check arbitrage opportunities", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
