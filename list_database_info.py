import sqlite3
from grip8a.db.config import DB_FORCE

DB = DB_FORCE

DB_PATH = DB

def get_all_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()
    return tables


def get_columns(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]  # row[1] = column name

    conn.close()
    return columns


def get_rows(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    conn.close()
    return rows

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT user FROM user_table;")
    users = [row[0] for row in cursor.fetchall()]

    conn.close()
    return users


if __name__ == "__main__":
    tables = get_all_tables()
    print("TABLES FOUND:", tables)
    print()

    for table in tables:
        print(f"=== TABLE: {table} ===")
        cols = get_columns(table)
        print("Columns:", cols)
        
        users = get_all_users()
        print(users)

        # Uncomment if you want row data:
        # rows = get_rows(table)
        # print("Rows:", rows)

        print()

