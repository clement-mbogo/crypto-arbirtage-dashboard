from flask import Flask, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import Trade
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///arbitrage.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route("/")
def index():
    return jsonify({"message": "Crypto Arbitrage Dashboard API is live"}), 200

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

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
