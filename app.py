import json

# Sample: Load historical price data from JSON file (you can replace with your data source)
def load_historical_prices():
    # For example, JSON structure: [{"timestamp": "...", "BTC": price, "ETH": price}, ...]
    with open('historical_prices.json', 'r') as f:
        return json.load(f)

@app.route('/backtest', methods=['POST'])
def backtest():
    settings = load_settings()
    target_profit = settings.get('target_profit', 5)
    stake = settings.get('stake', 5)
    pair = settings.get('pair', 'BTC')

    prices = load_historical_prices()
    trades = []
    total_profit = 0

    for price_point in prices:
        price = price_point.get(pair)
        if not price:
            continue

        # Simulate random spread (you could improve by actual historical spreads if available)
        spread = round(random.uniform(0.5, 2.5), 2)

        if spread >= target_profit:
            profit = round((spread / 100) * stake, 2)
            trades.append({
                'timestamp': price_point['timestamp'],
                'pair': pair,
                'buy_price': round(price * (1 - spread / 200), 2),
                'sell_price': round(price * (1 + spread / 200), 2),
                'profit': profit
            })
            total_profit += profit

    result = {
        'total_trades': len(trades),
        'total_profit': round(total_profit, 2),
        'average_profit_per_trade': round(total_profit / len(trades), 2) if trades else 0,
        'trades': trades
    }

    return jsonify({'status': 'ok', 'result': result})
