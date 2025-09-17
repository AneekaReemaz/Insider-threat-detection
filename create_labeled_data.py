import pandas as pd
import os

def label_cert_data():
    """
    This function reads the combined log file and the answers file
    to create a final, labeled dataset for testing.
    """
    # --- Configuration ---
    # Input file from the previous step.
    combined_log_filename = 'combined_log-final.csv'
    
    # The 'answer key' file you just created.
    answers_filename = 'answers.csv'
    
    # The final output file for testing.
    output_filename = 'final_labeled_dataset-modified.csv'

    # --- Main Script ---
    # Check if input files exist
    if not os.path.exists(combined_log_filename) or not os.path.exists(answers_filename):
        print(f"Error: Make sure both '{combined_log_filename}' and '{answers_filename}' exist in your folder.")
        return

    print(f"Loading combined log data from '{combined_log_filename}'...")
    df_logs = pd.read_csv(combined_log_filename)
    
    print(f"Loading insider threat answers from '{answers_filename}'...")
    df_answers = pd.read_csv(answers_filename)

    # Convert date columns to datetime objects for accurate comparison
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
    df_answers['start'] = pd.to_datetime(df_answers['start'])
    df_answers['end'] = pd.to_datetime(df_answers['end'])

    # Initialize the new 'is_malicious' label column to 0 (normal)
    print("Creating 'is_malicious' label column...")
    df_logs['is_malicious'] = 0

    # Iterate through each malicious scenario to label the events
    print("Tagging malicious events based on the answers file...")
    for index, row in df_answers.iterrows():
        user = row['user_id']
        start_time = row['start']
        end_time = row['end']
        
        # Find all log entries that match the user AND fall within the malicious time window
        malicious_events_mask = (
            (df_logs['user_id'] == user) &
            (df_logs['timestamp'] >= start_time) &
            (df_logs['timestamp'] <= end_time)
        )
        
        # Set the 'is_malicious' label for these events to 1
        df_logs.loc[malicious_events_mask, 'is_malicious'] = 1
        print(f"  - Labeled {malicious_events_mask.sum()} events for user '{user}'.")

    # Save the final labeled dataset
    print(f"\nSaving the fully labeled test data to '{output_filename}'...")
    df_logs.to_csv(output_filename, index=False)
    
    print("\nProcess complete!")
    print(f"Your final test file is ready: '{output_filename}'")

if __name__ == '__main__':
    label_cert_data()
    