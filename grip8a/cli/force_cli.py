from grip8a.ble.manager import BLEManager, force
from grip8a.db.force_db import start_force_writer, stop_force_writer
from grip8a.utils.timers import complex_timer
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

        # -----------------------
        # Connect BLE + start DB writer
        # -----------------------
        if c == "1":
            print("Connecting...")
            try:
                start_force_writer()  # Start writer FIRST
                ble.start()           # Then BLE
                print("Connected (if available).")
            except Exception as e:
                print(f"Failed to connect: {e}")
                stop_force_writer()  # Ensure writer is stopped if BLE fails

        # -----------------------
        # Stream (save to DB)
        # -----------------------
        elif c == "2":
            hang = int(input("Hang time: "))
            rest = int(input("Rest: "))
            sets = int(input("Sets: "))
            print("Streaming. Ctrl+C to stop.")
            try:
                complex_timer(hang, rest, sets, 10, True)
            except KeyboardInterrupt:
                pass

        # -----------------------
        # Show live only
        # -----------------------
        elif c == "3":
            print("Live force. Ctrl+C to stop.")
            try:
                while True:
                    print("Force:", force)
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass

        # -----------------------
        # Disconnect + stop writer
        # -----------------------
        elif c == "4":
            print("Disconnecting...")
            ble.stop()
            stop_force_writer()
            print("Disconnected.")

        # -----------------------
        # Back to main menu
        # -----------------------
        elif c == "5":
            # Important: stop writer when leaving this menu
            stop_force_writer()
            break