from grip8a.db.config import DB_FORCE
import sqlite3, time
from datetime import datetime

DB = DB_FORCE

def init_force_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_ms INTEGER,
            timestamp_iso TEXT,
            force REAL
        )
    """)
    conn.commit()
    conn.close()


def save_force_reading(force_value):
    ts = time.time()
    ts_ms = int(ts * 1000)
    ts_iso = datetime.utcfromtimestamp(ts).isoformat()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO readings (timestamp_ms, timestamp_iso, force)
        VALUES (?, ?, ?)
    """, (ts_ms, ts_iso, force_value))
    conn.commit()
    conn.close()
