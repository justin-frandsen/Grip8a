import time

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