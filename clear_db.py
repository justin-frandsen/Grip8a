import sqlite3

DB_PATH = "force_readings.db"

def clear_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all table names (except SQLite internal tables)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    tables = [row[0] for row in cursor.fetchall()]

    print("Clearing tables:", tables)

    # Delete all rows from each table
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
        print(f"Cleared table: {table}")

    # Reset autoincrement counters
    cursor.execute("DELETE FROM sqlite_sequence;")

    conn.commit()
    conn.close()
    print("Database cleared successfully.")

if __name__ == "__main__":
    clear_database()
