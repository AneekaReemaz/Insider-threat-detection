import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

def run_advanced_analysis_on_cert():
    """
    This script uses advanced feature engineering to build a more intelligent
    and balanced UBA model.
    """
    cert_data_filename = 'final_labeled_dataset-modified.csv'
    
    try:
        df = pd.read_csv(cert_data_filename, low_memory=False)
    except FileNotFoundError:
        print(f"Error: CERT data file '{cert_data_filename}' not found.")
        return

    # --- ADVANCED FEATURE ENGINEERING ---
    print("Starting advanced feature engineering...")
    
    # Convert timestamp to datetime objects to extract more features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date

    # Feature 1: Logon Hour
    df['logon_hour'] = df['timestamp'].dt.hour
    
    # Feature 2: Count of a user's total activities per day
    daily_activity = df.groupby(['user_id', 'date']).size().reset_index(name='user_daily_activity_count')
    df = pd.merge(df, daily_activity, on=['user_id', 'date'], how='left')

    print("New features 'logon_hour' and 'user_daily_activity_count' created.")
    
    # --- Basic Feature Preparation ---
    # We now include our new, more powerful features in the model
    feature_columns = ["event_type", "logon_hour", "user_daily_activity_count"]
    
    # Fill any missing values and encode categorical features
    for col in ["event_type"]:
        df[col] = df[col].fillna('missing')
        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(df[col].astype(str))
        
    X = df[feature_columns]
    y_true = df['is_malicious']

    # --- Training ---
    X_train_normal = X[y_true == 0]
    model = IsolationForest(contamination='auto', random_state=42, n_jobs=-1)
    
    print("Training the ADVANCED model on CERT data...")
    model.fit(X_train_normal)
    
    # --- Save the Advanced Model ---
    model_filename = 'final_cert_model_advanced.joblib'
    joblib.dump(model, model_filename)
    print(f"Advanced model saved to '{model_filename}'.")

    # --- Testing and Evaluation ---
    predictions = model.predict(X)
    predicted_labels = [1 if p == -1 else 0 for p in predictions]

    print("\n--- ADVANCED Model Performance on CERT Dataset ---")
    print(classification_report(y_true, predicted_labels, digits=3))
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, predicted_labels))

if __name__ == '__main__':
    run_advanced_analysis_on_cert()