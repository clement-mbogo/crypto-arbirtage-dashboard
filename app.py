from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# --- Initialize Database ---
def init_db():
    conn = sqlite3.connect('trades.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            timestamp TEXT,
            capital REAL,
            profit REAL,
            trade_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# --- Optional: Seed with Sample Data ---
def seed_sample_data():
    conn = sqlite3.connect('trades.db')
    cursor = conn.cursor()

    # Check if there's already data
    cursor.execute("SELECT COUNT(*) FROM performance")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded

    start = datetime.now() - timedelta(hours=10)
    for i in range(20):
        ts = (start + timedelta(minutes=30 * i)).strftime('%H:%M')
        cap = 1000 + i * 5
        prof = i * 2
        trades = i
        cursor.execute("INSERT INTO performance VALUES (?, ?, ?, ?)", (ts, cap, prof, trades))

    conn.commit()
    conn.close()

# --- Chart Data Endpoint ---
@app.route('/get_chart_data')
def get_chart_data():
    conn = sqlite3.connect('trades.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, capital, profit, trade_count FROM performance ORDER BY timestamp")
    rows = cursor.fetchall()
    conn.close()

    chart_data = {
        'labels': [row[0] for row in rows],
        'capital': [row[1] for row in rows],
        'profit': [row[2] for row in rows],
        'trades': [row[3] for row in rows]
    }

    return jsonify(chart_data)

# --- Main Entrypoint ---
if __name__ == '__main__':
    init_db()
    seed_sample_data()  # Comment this out if using real bot data
    app.run(debug=True, port=5000)
