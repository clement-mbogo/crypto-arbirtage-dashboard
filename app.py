import os
import sqlite3
import random
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.permanent_session_lifetime = timedelta(minutes=30)

DB_FILE = 'database/performance.db'
USERS_FILE = os.path.join(os.path.dirname(__file__), 'templates', 'users.json')

# Auto-create database and seed test data if needed
def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            capital REAL,
            profit REAL,
            trade_count INTEGER
        )
    ''')
    # Seed test data if table is empty
    cursor.execute("SELECT COUNT(*) FROM performance")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            ("2025-03", 1000, 0, 0),
            ("2025-04", 1200, 200, 5),
            ("2025-05", 1400, 400, 8),
            ("2025-06", 1300, 300, 6),
            ("2025-07", 1500, 500, 10),
        ]
        cursor.executemany(
            "INSERT INTO performance (timestamp, capital, profit, trade_count) VALUES (?, ?, ?, ?)",
            seed_data
        )
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# Load user data from file
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

# Save session-level OTP
def generate_otp():
    return str(random.randint(100000, 999999))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['otp'] = generate_otp()
            session['2fa_verified'] = False
            flash(f"Your OTP is: {session['otp']}", "info")
            return redirect(url_for('two_fa'))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/2fa", methods=['GET'])
def two_fa():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("2fa.html")

@app.route("/verify_2fa", methods=['POST'])
def verify_2fa():
    entered_code = request.form['otp']
    if 'otp' in session and entered_code == session['otp']:
        session['2fa_verified'] = True
        return redirect(url_for('dashboard'))
    flash("Incorrect OTP", "danger")
    return redirect(url_for('two_fa'))

@app.route("/dashboard")
def dashboard():
    if not session.get('username') or not session.get('2fa_verified'):
        return redirect(url_for('login'))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/binance_balance")
def binance_balance():
    balance = {
        "USDT": 10000,
        "BTC": 1,
        "ETH": 1
    }
    return jsonify(balance)

@app.route("/real_growth")
def real_growth():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, capital, profit, trade_count FROM performance")
    rows = cursor.fetchall()
    conn.close()
    data = {
        "timestamps": [r[0] for r in rows],
        "capital": [r[1] for r in rows],
        "profit": [r[2] for r in rows],
        "trade_count": [r[3] for r in rows]
    }
    return jsonify(data)

@app.route("/backtest_growth")
def backtest_growth():
    fake_data = {
        "timestamps": ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05"],
        "capital": [1000, 1100, 1250, 1150, 1350],
        "profit": [0, 100, 250, 150, 350],
        "trade_count": [0, 2, 4, 3, 5]
    }
    return jsonify(fake_data)

if __name__ == "__main__":
    app.run(debug=True)
