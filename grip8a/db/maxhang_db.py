from grip8a.db.config import DB_MAXHANG
import sqlite3

DB = DB_MAXHANG

def init_maxhang_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS hangs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            user TEXT,
            current_weight REAL,
            weight_percent REAL,
            exercise_type TEXT,
            side TEXT,
            edge_size_mm INTEGER,
            added_weight REAL,
            hang_duration_sec INTEGER,
            rpe INTEGER,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()
