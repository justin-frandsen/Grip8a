from grip8a.db.config import DB_MAXHANG
import sqlite3
from datetime import datetime

DB = DB_MAXHANG

def init_user_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_created TEXT,
            user TEXT,
            gender TEXT,
            age INTEGER,
            max_grade TEXT
        )
    """)
    conn.commit()
    conn.close()
    
def add_user(username, gender, age, max_grade):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    date_created = datetime.utcnow().isoformat()
    c.execute("""
        INSERT INTO user_table (date_created, user, gender, age, max_grade)
        VALUES (?, ?, ?, ?, ?)
    """, (date_created, username, gender, age, max_grade))
    conn.commit()
    conn.close()
    print("User {username} added successfully.")
    
def user_exists(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT 1 FROM user_table WHERE user = ? LIMIT 1", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None  # True if exists, False if not

    
def update_user(username, gender, age, max_grade):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE user_table
        SET gender = ?, age = ?, max_grade = ?
        WHERE username = ?;
    """, (gender, age, max_grade, username))

    conn.commit()
    conn.close()