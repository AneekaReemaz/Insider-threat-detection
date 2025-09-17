import pandas as pd
import random

def inject_and_label():
    """
    This script loads the combined CERT data, injects a synthetic anomaly
    for a random user, and creates the final labeled test dataset. This method
    is robust for small data samples.
    """
    input_filename = 'combined_log-final.csv'
    output_filename = 'final_labeled_dataset-modified.csv'
    
    print(f"--- Starting Anomaly Injection for '{input_filename}' ---")
    
    try:
        df = pd.read_csv(input_filename)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filename}'. Please run the combine script first.")
        return

    # --- 1. Select a Target for the Anomaly ---
    # We choose a user who has performed at least one 'file' activity.
    file_users = df[df['event_type'] == 'file']['user_id'].unique()
    
    if len(file_users) == 0:
        print("Error: Could not find any users with 'file' activity to create an anomaly.")
        print("Please check your 'file-modified.csv' to ensure it contains data.")
        return
        
    target_user = random.choice(file_users)
    print(f"Selected random user '{target_user}' to be our insider threat.")

    # --- 2. Create the Anomaly (Mass Data Download) ---
    # Find a day where this user had some file activity.
    user_file_activity = df[(df['user_id'] == target_user) & (df['event_type'] == 'file')].copy()
    user_file_activity['date'] = pd.to_datetime(user_file_activity['timestamp']).dt.date
    
    # Pick a specific day to be the "attack day"
    attack_date = user_file_activity['date'].iloc[0]
    print(f"The anomaly (mass file copy) will occur on: {attack_date}")

    # --- 3. Label the Data ---
    # Initialize the label column to 0 (normal)
    df['is_malicious'] = 0
    
    # Find all file events for our target user on the attack day
    anomaly_mask = (
        (df['user_id'] == target_user) &
        (df['event_type'] == 'file') &
        (pd.to_datetime(df['timestamp']).dt.date == attack_date)
    )
    
    # Mark these specific events as malicious (1)
    df.loc[anomaly_mask, 'is_malicious'] = 1
    
    num_anomalies = anomaly_mask.sum()
    print(f"Successfully labeled {num_anomalies} file-copy events as malicious for user '{target_user}'.")

    # --- 4. Save the Final Labeled Dataset ---
    print(f"\nSaving the new labeled test data to '{output_filename}'...")
    df.to_csv(output_filename, index=False)
    
    print("\nProcess complete!")
    print(f"Your final test file is ready: '{output_filename}'")


if __name__ == '__main__':
    inject_and_label()