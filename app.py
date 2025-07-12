from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = 'performance.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_data(source):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT timestamp, capital, profit, trade_count 
        FROM performance 
        WHERE source = ? 
        ORDER BY timestamp ASC
    """
    cursor.execute(query, (source,))
    data = cursor.fetchall()
    conn.close()
    return [dict(row) for row in data]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/real_growth')
def real_growth():
    return jsonify(fetch_data('real'))

@app.route('/backtest_growth')
def backtest_growth():
    return jsonify(fetch_data('backtest'))

@app.route('/start_bot', methods=['POST'])
def start_bot():
    data = request.get_json()
    print("Starting bot with settings:", data)
    return jsonify({"status": "started"})

@app.route('/pause_bot', methods=['POST'])
def pause_bot():
    print("Bot paused")
    return jsonify({"status": "paused"})

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    print("Bot stopped")
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print("⚠️ Database not found. Please run seed_db.py to generate test data.")
    app.run(debug=True)
