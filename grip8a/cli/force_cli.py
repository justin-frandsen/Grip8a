from grip8a.ble.manager import BLEManager, force
from grip8a.db.force_db import save_force_reading
import time

def force_menu():
    ble = BLEManager()

    while True:
        print("""
=== FORCE SENSOR ===
1. Connect
2. Stream force (save to DB)
3. Show live force
4. Disconnect
5. Back
""")
        c = input("Choose: ")

        if c == "1":
            ble.start()
            print("Connecting...")

        elif c == "2":
            print("Streaming. Ctrl+C to stop.")
            try:
                while True:
                    print("Force:", force)
                    save_force_reading(force)
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass

        elif c == "3":
            print("Live force. Ctrl+C to stop.")
            try:
                while True:
                    print("Force:", force)
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass

        elif c == "4":
            ble.stop()

        elif c == "5":
            break
