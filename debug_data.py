import pandas as pd

def debug_cert_data():
    """
    This script investigates the combined log file to understand why
    the labeling process is not finding malicious events.
    """
    log_filename = 'combined_log-final.csv'
    
    print(f"--- Starting Debug for '{log_filename}' ---")
    
    try:
        df = pd.read_csv(log_filename)
    except FileNotFoundError:
        print(f"Error: Could not find '{log_filename}'.")
        return

    # Clue 1: Check the User ID format
    print("\n[Clue 1] Checking User IDs...")
    malicious_user_1 = 'CDE1846'
    is_user_present = malicious_user_1 in df['user_id'].unique()
    print(f"Is the user '{malicious_user_1}' present in the data? -> {is_user_present}")
    if not is_user_present:
        print("  - Reason: The user ID was not found. Check for typos or formatting differences.")
        # Optional: print all unique users to see the format
        # print(df['user_id'].unique())

    # Clue 2: Check the Timestamp format and date range
    print("\n[Clue 2] Checking Timestamps for the user...")
    if is_user_present:
        # Filter for only the malicious user's activity
        user_df = df[df['user_id'] == malicious_user_1].copy()
        
        # Convert timestamp column to datetime objects
        user_df['timestamp'] = pd.to_datetime(user_df['timestamp'])
        
        # Find the first and last time we see this user
        min_date = user_df['timestamp'].min()
        max_date = user_df['timestamp'].max()
        
        print(f"  - Earliest activity found for this user: {min_date}")
        print(f"  - Latest activity found for this user:   {max_date}")
        
        # The known malicious date range for this user
        malicious_start = pd.to_datetime('2010-12-13')
        malicious_end = pd.to_datetime('2010-12-17')
        
        print(f"  - We are looking for activity between:  {malicious_start.date()} and {malicious_end.date()}")

        # Check if the ranges overlap
        if max_date < malicious_start or min_date > malicious_end:
            print("\n[Conclusion] The user exists, but there is NO ACTIVITY for them in the malicious date range.")
            print("This is the reason no events were labeled. The data version you have may be different.")
        else:
            print("\n[Conclusion] The user exists and their activity OVERLAPS with the malicious date range.")
            print("If you are still seeing 0 events labeled, there might be a subtle formatting issue.")
    
    print("\n--- Debug Finished ---")


if __name__ == '__main__':
    debug_cert_data()