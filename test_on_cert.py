import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

def test_model_on_cert_data():
    """
    Loads a pre-trained model and evaluates it on the prepared CERT dataset.
    This script adapts the CERT data columns to match what the model was trained on.
    """
    # --- 1. Load the Model and CERT Test Data ---
    model_filename = 'insider_threat_model.joblib'
    cert_data_filename = 'final_labeled_dataset-modified.csv'

    try:
        print(f"Loading pre-trained model from '{model_filename}'...")
        model = joblib.load(model_filename)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print(f"Error: Model file '{model_filename}' not found.")
        print("Please run your 'train.py' script first to train and save the model.")
        return

    try:
        print(f"Loading CERT test data from '{cert_data_filename}'...")
        df_cert = pd.read_csv(cert_data_filename, low_memory=False)
        print("CERT data loaded successfully.")
    except FileNotFoundError:
        print(f"Error: CERT data file '{cert_data_filename}' not found.")
        print("Please run the 'inject_anomaly.py' script first.")
        return

    # --- 2. Adapt CERT Data to Match Model's Expected Features ---
    print("\nAdapting CERT data to match the features the model was trained on...")
    
    # This list MUST match the categorical_cols from your train.py script
    expected_features = ["action_type", "resource_accessed", "success"]
    
    # --- Feature Mapping ---
    # a. Create 'action_type' from 'event_type'
    df_cert['action_type'] = df_cert['event_type']
    
    # b. Create 'resource_accessed' by combining 'url' and 'filename'
    #    We fill empty values from one with values from the other.
    df_cert['resource_accessed'] = df_cert['filename'].fillna(df_cert['url'])
    
    # c. Create a 'success' column since the model expects it.
    #    Since CERT data doesn't have this, we'll fill it with a consistent value.
    df_cert['success'] = 'success' # A placeholder value

    # Fill any remaining missing values in our new columns
    for col in expected_features:
        df_cert[col] = df_cert[col].fillna('missing')

    # Apply the same Label Encoding as in your training script
    for col in expected_features:
        encoder = LabelEncoder()
        df_cert[col] = encoder.fit_transform(df_cert[col].astype(str))
        
    print("Feature adaptation complete.")

    # --- 3. Make Predictions on the Adapted CERT Data ---
    X_cert_test = df_cert[expected_features]
    y_cert_true = df_cert['is_malicious']

    print("\nMaking predictions on the CERT dataset...")
    predictions = model.predict(X_cert_test)
    
    # Convert predictions (1 for normal, -1 for anomaly) to our label format (0, 1)
    predicted_labels = [1 if p == -1 else 0 for p in predictions]

    # --- 4. Evaluate Performance on CERT Data ---
    print("\n--- Final Model Performance on CERT Dataset ---")
    print(classification_report(y_cert_true, predicted_labels))
    
    print("Confusion Matrix:")
    tn, fp, fn, tp = confusion_matrix(y_cert_true, predicted_labels).ravel()
    print(f"Malicious Events Correctly Identified (True Positives): {tp}")
    print(f"Malicious Events Missed (False Negatives): {fn}")
    print(f"Normal Events Incorrectly Flagged (False Positives): {fp}")
    print(f"Normal Events Correctly Identified (True Negatives): {tn}")


if __name__ == '__main__':
    test_model_on_cert_data()