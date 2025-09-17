import pandas as pd
import os

def combine_modified_cert_logs():
    """
    This function loads individual CERT log files that have been renamed
    with a '-modified' suffix, combines them, and saves the result.
    """
    # --- Configuration ---
    # The script now looks for files with the "-modified.csv" suffix.
    files_to_combine = [
        'logon-modified.csv',
        'device-modified.csv',
        'file-modified.csv',
        'https-modified.csv'
    ]

    # The final output file name.
    output_filename = 'combined_log-final.csv'

    all_dataframes = []
    
    print("Starting the data combination process...")
    print("Looking for files with '-modified' names...")

    for filename in files_to_combine:
        if not os.path.exists(filename):
            print(f"Error: The file '{filename}' was not found.")
            print("Please make sure you have renamed your files correctly before running this script.")
            return # Stop the script if a file is missing
            
        print(f"Loading and processing {filename}...")
        
        df = pd.read_csv(filename)
        
        # We can still get the base event type from the filename
        event_type = filename.replace('-modified.csv', '')
        df['event_type'] = event_type
        
        df.rename(columns={
            'date': 'timestamp',
            'user': 'user_id',
            'pc': 'hostname'
        }, inplace=True)

        all_dataframes.append(df)

    if not all_dataframes:
        print("Error: No data was loaded.")
        return

    print("\nCombining all dataframes...")
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
    
    print("Sorting all events by date and time...")
    combined_df.sort_values(by=['timestamp', 'user_id'], inplace=True)
    
    print(f"Saving the combined data to '{output_filename}'...")
    combined_df.to_csv(output_filename, index=False)
    
    print(f"\nProcess complete! Master log file saved as '{output_filename}'.")
    print(f"Total events combined: {len(combined_df)}")


if __name__ == '__main__':
    combine_modified_cert_logs()