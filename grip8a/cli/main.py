from grip8a.db.maxhang_db import init_maxhang_db
from grip8a.db.force_db import init_force_db
from grip8a.cli.maxhang_cli import maxhang_menu
from grip8a.cli.force_cli import force_menu
from grip8a.db.user_db import init_user_db, user_exists, add_user, update_user

def main():
    init_maxhang_db()
    init_force_db()
    init_user_db()

    username = input("Username: ").strip()
    weight = float(input("Bodyweight (lbs): ").strip())
    
    if not user_exists(username):
        print("New user detected. Please provide additional information.")
        gender = input("Gender: ").strip()
        age = int(input("Age: ").strip())
        max_grade = input("Max climbing grade (e.g., 5.10a, V5): ").strip()
        add_user(username, gender, age, max_grade)

    while True:
        print(f"""
=== GRIP8A SYSTEM ===
User: {username} ({weight} lbs)

1. Max Hang Tools
2. Force Sensor Tools
3. Update User Info
4. Switch User
5. Exit
""")
        c = input("Choose: ")

        if c == "1":
            maxhang_menu(username, weight)
        elif c == "2":
            force_menu()
        elif c == "3":
            print("Update User Info: ")
            gender = input("Gender: ").strip()
            age = int(input("Age: ").strip())
            max_grade = input("Max climbing grade (e.g., 5.10a, V5): ").strip()
            update_user(username, gender, age, max_grade)
        elif c == "4":
            username = input("New username: ")
            weight = float(input("Bodyweight: "))
        elif c == "5":
            break
