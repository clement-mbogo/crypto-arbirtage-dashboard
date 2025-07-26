from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
from dotenv import load_dotenv
import os

from database import Trade, Performance
from schema import openapi_schema

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///arbitrage.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


@app.route("/")
def index():
    return jsonify({"message": "Crypto Arbitrage Dashboard API is live"}), 200


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})


@app.route("/api/trades")
def get_trades():
    session = Session()
    trades = session.query(Trade).order_by(desc(Trade.timestamp)).limit(100).all()
    result = [
        {
            "id": t.id,
            "timestamp": t.timestamp.isoformat(),
            "pair": t.pair,
            "action": t.action,
            "price": t.price,
            "quantity": t.quantity,
            "profit": t.profit,
        }
        for t in trades
    ]
    session.close()
    return jsonify(result)


@app.route("/api/performance")
def get_performance():
    session = Session()
    records = session.query(Performance).order_by(desc(Performance.timestamp)).limit(50).all()
    result = [
        {
            "timestamp": r.timestamp.isoformat(),
            "capital": r.capital,
            "profit": r.profit,
            "trade_count": r.trade_count,
        }
        for r in records
    ]
    session.close()
    return jsonify(result)


@app.route("/api/alerts")
def get_alerts():
    alerts_file = "alerts.json"
    if os.path.exists(alerts_file):
        with open(alerts_file) as f:
            alerts = f.read()
        return app.response_class(alerts, mimetype="application/json")
    else:
        return jsonify([])


@app.route("/openapi.json")
def openapi_json():
    return jsonify(openapi_schema)


@app.route("/docs")
def serve_docs():
    return send_from_directory(app.static_folder, "docs.html")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
