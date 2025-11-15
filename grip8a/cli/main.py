from grip8a.db.maxhang_db import init_maxhang_db
from grip8a.db.force_db import init_force_db
from grip8a.cli.maxhang_cli import maxhang_menu
from grip8a.cli.force_cli import force_menu

def main():
    init_maxhang_db()
    init_force_db()

    username = input("Username: ").strip()
    weight = float(input("Bodyweight (lbs): "))

    while True:
        print(f"""
=== GRIP8A SYSTEM ===
User: {username} ({weight} lbs)

1. Max Hang Tools
2. Force Sensor Tools
3. Switch User
4. Exit
""")
        c = input("Choose: ")

        if c == "1":
            maxhang_menu(username, weight)
        elif c == "2":
            force_menu()
        elif c == "3":
            username = input("New username: ")
            weight = float(input("Bodyweight: "))
        elif c == "4":
            break
