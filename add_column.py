import sqlite3

db_path = "trades.db"  # adjust path if needed

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE performance ADD COLUMN profit_percent REAL DEFAULT 0")
    conn.commit()
    print("Column 'profit_percent' added.")
except sqlite3.OperationalError as e:
    print("Error:", e)

conn.close()
