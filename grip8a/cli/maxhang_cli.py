from grip8a.utils.timers import complex_timer
from grip8a.db.maxhang_db import init_maxhang_db, log_max_hang, view_logs

def maxhang_menu(username, weight):
    while True:
        print("""
=== MAX HANG MENU ===
1. Start timer
2. Log max hang
3. View logs
4. Back
""")
        c = input("Choose: ")

        if c == "1":
            hang = int(input("Hang time: "))
            rest = int(input("Rest: "))
            sets = int(input("Sets: "))
            complex_timer(hang, rest, sets)

        elif c == "2":
            log_max_hang(username, weight)

        elif c == "3":
            view_logs(username)

        elif c == "4":
            break
