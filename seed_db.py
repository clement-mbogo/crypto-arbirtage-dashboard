import sqlite3

conn = sqlite3.connect("performance.db")
cursor = conn.cursor()

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

cursor.executemany("""
INSERT INTO performance (timestamp, capital, profit, trade_count, source)
VALUES (?, ?, ?, ?, ?)
""", [
    ("2025-06-01", 10000, 0, 0, "real"),
    ("2025-06-02", 10100, 100, 3, "real"),
    ("2025-06-03", 9800, -300, 5, "real"),
    ("2025-06-01", 10000, 0, 0, "backtest"),
    ("2025-06-02", 10200, 200, 2, "backtest"),
    ("2025-06-03", 10350, 150, 4, "backtest")
])

conn.commit()
conn.close()

print("✅ performance.db created")
