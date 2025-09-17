import pandas as pd
import requests
import time
import json
import numpy as np

def simulate_real_time_activity():
    filename = 'final_labeled_dataset-modified.csv'
    df = pd.read_csv(filename)
    # Shuffle the data to make the simulation more interesting
    records = df.sample(frac=1).to_dict(orient='records')
    url = 'http://127.0.0.1:8000/predict'
    
    print("Starting simulation... press Ctrl+C to stop.")
    
    for record in records:
        try:
            # Clean data for JSON serialization
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    record[key] = float(value)
                elif pd.isna(value):
                    record[key] = None
            
            requests.post(url, json=record)
            print(f"Sent event for user: {record.get('user_id', 'N/A')}")
            time.sleep(0.1) # Speed up simulation
        except requests.exceptions.RequestException as e:
            print(f"\nCannot connect to the server. Is app.py running? Error: {e}")
            break
        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")
            break

if __name__ == '__main__':
    simulate_real_time_activity()