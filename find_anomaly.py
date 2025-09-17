import pandas as pd

def find_and_label_anomalies():
    """
    This algorithm automatically hunts for suspicious patterns in the CERT data
    and labels them as anomalies to create a realistic test set.
    """
    input_filename = 'combined_log-final.csv'
    output_filename = 'final_labeled_dataset-modified.csv'
    
    print(f"--- Starting Anomaly Hunting for '{input_filename}' ---")
    
    try:
        df = pd.read_csv(input_filename, low_memory=False)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filename}'. Please run the combine script first.")
        return

    # --- 1. Prepare Data for Analysis ---
    df['date'] = pd.to_datetime(df['timestamp']).dt.date

    # --- 2. Define Anomaly Rules and Keywords ---
    job_search_keywords = ['job', 'career', 'resume', 'hiring']
    leak_site_keywords = ['wikileaks']

    # --- 3. Calculate Daily Activity Metrics for Each User ---
    print("Analyzing daily user activities...")
    
    # Calculate file copies per user per day
    daily_file_copies = df[df['event_type'] == 'file'].groupby(['user_id', 'date']).size().reset_index(name='file_copy_count')

    # Find days with any USB device connection
    daily_device_usage = df[df['event_type'] == 'device'].groupby(['user_id', 'date']).size().reset_index(name='device_connections')
    daily_device_usage['used_usb'] = 1

    # Find days with job search activity
    df_http = df[df['event_type'] == 'http'].copy()
    df_http['is_job_search'] = df_http['url'].str.contains('|'.join(job_search_keywords), na=False)
    daily_job_searches = df_http[df_http['is_job_search']].groupby(['user_id', 'date']).size().reset_index(name='job_search_count')
    daily_job_searches['searched_for_jobs'] = 1

    # --- 4. Combine Metrics and Calculate a Daily Risk Score ---
    print("Calculating daily risk scores for each user...")
    
    # Merge all daily metrics together
    user_daily_summary = pd.merge(daily_file_copies, daily_device_usage[['user_id', 'date', 'used_usb']], on=['user_id', 'date'], how='left')
    user_daily_summary = pd.merge(user_daily_summary, daily_job_searches[['user_id', 'date', 'searched_for_jobs']], on=['user_id', 'date'], how='left')
    user_daily_summary.fillna(0, inplace=True)
    
    # Simple risk score: High file copies are suspicious, other actions add to the risk.
    # We define "high" as more than the average user's busiest day.
    file_copy_threshold = user_daily_summary['file_copy_count'].quantile(0.95) # Top 5%
    
    user_daily_summary['risk_score'] = 0
    # Rule 1: High volume file copy is a major indicator
    user_daily_summary.loc[user_daily_summary['file_copy_count'] > file_copy_threshold, 'risk_score'] += 5
    # Rule 2: Using a USB adds to suspicion
    user_daily_summary.loc[user_daily_summary['used_usb'] == 1, 'risk_score'] += 2
    # Rule 3: Searching for jobs adds to suspicion
    user_daily_summary.loc[user_daily_summary['searched_for_jobs'] == 1, 'risk_score'] += 3

    # --- 5. Identify High-Risk Days and Label the Data ---
    # Find the days where the risk score is very high (e.g., score >= 8 means file copies + job search)
    anomalous_days = user_daily_summary[user_daily_summary['risk_score'] >= 8][['user_id', 'date']]
    
    if anomalous_days.empty:
        print("\nWarning: No days with highly suspicious combined activity were found.")
        print("The test dataset will not have any labeled anomalies.")
    else:
        print(f"\nFound {len(anomalous_days)} potentially anomalous user-days to label.")

    # Merge these anomaly flags back into the main dataframe
    df = pd.merge(df, anomalous_days, on=['user_id', 'date'], how='left', indicator=True)
    
    # Create the final label column
    df['is_malicious'] = (df['_merge'] == 'both').astype(int)
    df.drop(columns=['_merge'], inplace=True)

    # --- 6. Save the Final Labeled Dataset ---
    print(f"Saving the new labeled test data to '{output_filename}'...")
    df.to_csv(output_filename, index=False)
    
    print("\nProcess complete!")
    print(f"Total events labeled as malicious: {df['is_malicious'].sum()}")
    print(f"Your final test file is ready: '{output_filename}'")

if __name__ == '__main__':
    find_and_label_anomalies()