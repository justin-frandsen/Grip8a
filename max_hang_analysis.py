import sqlite3
import pandas as pd

DB_PATH = "max_hang_logs.db"

def load_user_data(username):
    conn = sqlite3.connect(DB_PATH)
    #select selects the columns specified (* means all columns)
    #from selects the table
    #where 
    query = "SELECT * FROM hangs WHERE user=? ORDER BY date ASC"
    df = pd.read_sql_query(query, conn, params=(username,))
    conn.close()

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    return df

def get_user_values(df):
    # Sort newest → oldest
    df_sorted = df.sort_values("date", ascending=False)

    # Take last 10 sessions
    last10 = df_sorted.head(10)

    # Find the row where added_weight is max
    max_row = last10.loc[last10["added_weight"].idxmax()]

    # Return both fields
    return max_row["added_weight"], max_row["current_weight"]

import pandas as pd

def build_progression_table(current_max, bodyweight, roi=0.05, total_weeks=8):
    total_weeks = int(total_weeks)  # ensure integer
    
    # Clamp ROI so it never goes below 0
    roi_low = max(0, roi - 0.03)
    roi_base = roi
    roi_high = roi + 0.03

    labels = [
        f"{roi_low*100:.1f}%_increase",
        f"{roi_base*100:.1f}%_increase",
        f"{roi_high*100:.1f}%_increase"
    ]

    weeks = list(range(0, total_weeks + 1))

    # Calculate weekly increment
    def linear_progression(roi_value):
        increment = (current_max * roi_value) / total_weeks
        return [current_max + increment * w for w in weeks]

    row_low = linear_progression(roi_low)
    row_base = linear_progression(roi_base)
    row_high = linear_progression(roi_high)

    # Build DataFrame
    to_pull_df = pd.DataFrame({
        "progression": labels,
        **{f"week_{w}": [row_low[w], row_base[w], row_high[w]] for w in weeks}
    })
    
    # --- Bodyweight percent DataFrame ---
    bodyweight_percent_df = pd.DataFrame({
        "progression": labels,
        **{
            f"week_{w}": [
                round((row_low[w] / (bodyweight / 2)) * 100),
                round((row_base[w] / (bodyweight / 2)) * 100),
                round((row_high[w] / (bodyweight / 2)) * 100),
            ]
            for w in weeks
        }
    })

    return to_pull_df, bodyweight_percent_df
    
if __name__ == "__main__":
    user = input("Enter username for analysis: ").strip()
    df = load_user_data(user)

    if df.empty:
        print(f"No data found for user {user}")
    else:
        current_max, bodyweight = get_user_values(df)
        print(f"Current max (from last 10 sessions): {current_max:.1f} lbs")

        # ROI input loop
        while True:
            roi_input = input("Enter Rate of Improvement (ROI) - between 0 and 1: ").strip()

            try:
                roi = float(roi_input)
            except ValueError:
                print("Invalid input. Please enter a decimal between 0 and 1.")
                continue

            if 0 <= roi <= 1:
                break
            else:
                print("ROI must be between 0 and 1. Try again.")

        progression_df, progression_df_bodyweight = build_progression_table(current_max, bodyweight, roi, total_weeks=8)
        print("\n8-week progression forecast:")
        print(progression_df)
        print("\n8-week progression forecast:")
        print(progression_df_bodyweight)


