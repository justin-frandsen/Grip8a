import time
from grip8a.ble.manager import force
from grip8a.db.force_db import queue_force_reading

# ----------------------
# Timer Logic
# ----------------------

def countdown(seconds, label="", record_force=False):
    seconds = int(seconds)
    start = time.time()
    last_print_second = seconds

    print()  # clean line

    while True:
        elapsed = time.time() - start
        remaining = max(0, seconds - int(elapsed))

        # Print label + countdown
        if remaining != last_print_second:
            print(f"\r{label} {remaining:2d}s   ", end="")
            last_print_second = remaining

        # Record if enabled
        if record_force:
            queue_force_reading(force)
            print(f"\r{label} {remaining:2d}s   | Force: {force} | Recording Now!", end="")
        else:
            print(f"\r{label} {remaining:2d}s", end="")
        
        # End when time runs out
        if elapsed >= seconds:
            break

        time.sleep(0.1)   # smooth 10 Hz updates

    print(f"\r{label} Done!                                                               ")  # clear line

def complex_timer(hang_time, rest_time, sets, setup_time=10, record_force=False):
    print("\nStarting complex hang timer!\n")
    for i in range(1, sets + 1):
        print(f"\n--- Set {i}/{sets} ---")
        countdown(setup_time, label="GET READY:")
        countdown(hang_time, label="HANG:", record_force=record_force)
        if i < sets:
            countdown(rest_time, label="REST:")
    print("\nWorkout complete!\n")