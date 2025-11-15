from grip8a.db.config import DB_MAXHANG
import sqlite3
from datetime import datetime

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

def log_max_hang(username, current_weight):
    print("\nSelect Exercise Type:")
    print("1. Hangboard Max Hang")
    print("2. One-arm Weight Pickup")
    choice = input("Choose (1 or 2): ")

    if choice not in ["1", "2"]:
        print("Invalid selection.\n")
        return

    exercise_type = "hangboard" if choice == "1" else "pickup"
    print(f"\nLogging: {exercise_type.upper()}")

    # Ask for edge size for both
    edge = int(input("Edge size (mm): "))

    if exercise_type == "hangboard":
        weight = float(input("Added weight (lbs): "))
    else:
        weight = float(input("Weight picked up (total): "))
        
    side = input("Which side? (L/R or Both): ").strip().upper()
    duration = int(input("Hang duration (sec): "))
    rpe = int(input("RPE (1–10): "))
    notes = input("Notes: ")

    percent_body_weight = (weight / current_weight) * 100 if exercise_type == "hangboard" else (weight / (current_weight / 2)) * 100
    print(f"\nYou hung for {duration} sec with {weight} lbs ({percent_body_weight:.1f}% body weight) on a {edge} mm edge.")
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO hangs (date, user, current_weight, weight_percent, exercise_type, side, edge_size_mm, added_weight, hang_duration_sec, rpe, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M"),
          username, current_weight, percent_body_weight, exercise_type, side, edge, weight, duration, rpe, notes))

    conn.commit()
    conn.close()
    print("\nSaved!\n")

def view_logs(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM hangs WHERE user=? ORDER BY date DESC", (username,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("\nNo logs yet!\n")
        return

    print(f"\n--- Max Hang Log for {username} ---")
    for row in rows:
        print(f"""
ID: {row[0]}
Date: {row[1]}
User: {row[2]}
Current Weight: {row[3]} lbs
Weight Percent: {row[4]:.1f}%
Exercise Type: {row[5]}
Side: {row[6]}
Edge Size: {row[7]} mm
Added Weight: {row[8]} lbs
Hang Duration: {row[9]} sec
RPE: {row[10]}
Notes: {row[11]}
-------------------------
""")
