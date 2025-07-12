import sqlite3
import datetime
import random

# Connect (or create) performance.db
conn = sqlite3.connect("performance.db")
cursor = conn.cursor()

# Create performance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    capital REAL,
    profit REAL,
    trade_count INTEGER,
    source TEXT
)
""")

# Generate fake rows for 'real' and 'backtest'
def insert_fake_data(source):
    capital = 10000
    profit = 0
    for i in range(10):
        capital += random.uniform(20, 150)
        profit = capital - 10000
        trade_count = i + 1
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=10 - i)).isoformat()
        cursor.execute("""
            INSERT INTO performance (timestamp, capital, profit, trade_count, source)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, capital, profit, trade_count, source))

# Insert both sources
insert_fake_data("real")
insert_fake_data("backtest")

conn.commit()
conn.close()

print("✅ Seeded performance.db with test data.")
