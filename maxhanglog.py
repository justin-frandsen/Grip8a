import time
import sqlite3
from datetime import datetime

DB_PATH = "max_hang_logs.db"

# ----------------------
# Database Setup
# ----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table if not exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS hangs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        user TEXT,
        exercise_type TEXT,
        side TEXT,
        edge_size_mm INTEGER,
        added_weight REAL,
        hang_duration_sec INTEGER,
        rpe INTEGER,
        notes TEXT
    )
    """)

    # Check columns and add if missing (for old DBs)
    c.execute("PRAGMA table_info(hangs)")
    cols = [row[1] for row in c.fetchall()]
    if "user" not in cols:
        c.execute("ALTER TABLE hangs ADD COLUMN user TEXT;")
    if "side" not in cols:
        c.execute("ALTER TABLE hangs ADD COLUMN side TEXT;")

    conn.commit()
    conn.close()

# ----------------------
# Timer Logic
# ----------------------
def countdown(seconds, label=""):
    seconds = int(seconds)
    for remaining in range(seconds, 0, -1):
        print(f"\r{label} {remaining:2d}s   ", end="")
        time.sleep(1)
    print(f"\r{label} Done!         ")

def complex_timer(hang_time, rest_time, sets, setup_time=10):
    print("\nStarting complex hang timer!\n")
    for i in range(1, sets + 1):
        print(f"\n--- Set {i}/{sets} ---")
        countdown(setup_time, label="GET READY:")
        countdown(hang_time, label="HANG:")
        if i < sets:
            countdown(rest_time, label="REST:")
    print("\nWorkout complete!\n")

# ----------------------
# Logging Max Hangs
# ----------------------
def log_max_hang(username):
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
        weight = float(input("Added weight (+) or assistance (-): "))
    else:
        weight = float(input("Weight picked up (total): "))
        
    side = input("Which side? (L/R or Both): ").strip().upper()
    duration = int(input("Hang duration (sec): "))
    rpe = int(input("RPE (1–10): "))
    notes = input("Notes: ")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO hangs (date, user, exercise_type, side, edge_size_mm, added_weight, hang_duration_sec, rpe, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M"),
          username, exercise_type, side, edge, weight, duration, rpe, notes))

    conn.commit()
    conn.close()
    print("\nSaved!\n")

# ----------------------
# Viewing Logs
# ----------------------
def view_logs(username):
    conn = sqlite3.connect(DB_PATH)
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
Type: {row[3]}
Side: {row[4]}
Edge Size: {row[5]} mm
Weight: {row[6]} lbs
Duration: {row[7]} sec
RPE: {row[8]}
Notes: {row[9]}
-------------------------
""")

# ----------------------
# Menu
# ----------------------
def main_menu():
    init_db()

    print("======= MAX HANG APP =======")
    username = input("Enter your username: ").strip()

    while True:
        print(f"""
===== Logged in as: {username} =====
1. Start a complex timer
2. Log a max hang
3. View logs
4. Switch user
5. Exit
""")
        choice = input("Choose an option: ")

        if choice == "1":
            hang = int(input("Hang time (sec): "))
            rest = int(input("Rest time (sec): "))
            sets = int(input("Number of sets: "))
            complex_timer(hang, rest, sets)

        elif choice == "2":
            log_max_hang(username)

        elif choice == "3":
            view_logs(username)

        elif choice == "4":
            username = input("Enter new username: ").strip()

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid selection.\n")

if __name__ == "__main__":
    main_menu()
