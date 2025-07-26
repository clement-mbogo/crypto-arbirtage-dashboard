from flask import Flask, jsonify, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import Trade
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="templates")

# Set up database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///arbitrage.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route("/")
def home():
    return "✅ Crypto Arbitrage Dashboard is running!"

    # OR if using HTML template:
    # return render_template("index.html")

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})

@app.route("/api/trades")
def get_all_trades():
    session = Session()
    trades = session.query(Trade).order_by(Trade.timestamp.desc()).limit(100).all()
    result = [
        {
            "id": t.id,
            "timestamp": t.timestamp.isoformat(),
            "symbol": t.symbol,
            "buy_exchange": t.buy_exchange,
            "sell_exchange": t.sell_exchange,
            "buy_price": t.buy_price,
            "sell_price": t.sell_price,
            "profit_percent": t.profit_percent,
            "volume": t.volume,
            "trade_type": t.trade_type
        }
        for t in trades
    ]
    session.close()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
