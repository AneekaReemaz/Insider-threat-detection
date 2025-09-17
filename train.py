import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

def train_and_save_model():
    """
    This function loads your synthetic data, trains an unsupervised 
    Isolation Forest model, evaluates it, and saves the trained model.
    """
    # --- 1. Load Your Synthetic Dataset ---
    try:
        df = pd.read_excel(r"C:\Users\ASUS\.vscode\vscodeprojects\uba_threat\processed_data.xlsx")
        print("Successfully loaded processed_data.xlsx.")
    except FileNotFoundError:
        print("Error: 'processed_data.xlsx' not found. Please check the file path.")
        return

    # --- 2. Prepare Data (Based on your original code) ---
    
    # IMPORTANT: Define your label and feature columns
    label_column = 'label'
    
    # Use the same categorical columns you had before
    categorical_cols = ["action_type", "resource_accessed", "success"]
    
    # Keep track of all feature columns (categorical + any numerical ones you have)
    # Make sure to add any other feature columns you might have.
    feature_columns = categorical_cols # Add numerical columns here if you have them

    # Check if columns exist
    if label_column not in df.columns or not all(col in df.columns for col in feature_columns):
        print("\nError: One or more specified columns were not found in the Excel file.")
        print(f"Available columns are: {df.columns.tolist()}")
        return

    # Encode your categorical features into numbers
    for col in categorical_cols:
        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(df[col].astype(str))

    # Separate features (X) and the true label (y)
    X = df[feature_columns]
    y_true = df[label_column]

    # --- 3. Separate Data for Unsupervised Training ---
    # The model must ONLY be trained on normal data (where label is 0)
    X_normal = X[y_true == 0]
    print(f"Training will use {len(X_normal)} 'normal' events.")

    # --- 4. Define and Train the Anomaly Detection Model ---
    # We use Isolation Forest as required by the project
    model = IsolationForest(contamination='auto', random_state=42, n_jobs=-1)
    
    print("Training the Isolation Forest model...")
    model.fit(X_normal)
    print("Training complete.")

    # --- 5. Save the Trained Model ---
    model_filename = 'insider_threat_model.joblib'
    print(f"Saving the trained model to {model_filename}...")
    joblib.dump(model, model_filename)
    print("Model saved successfully.")

    # --- 6. (Optional) Evaluate on Your Test Data ---
    # You can now see how well your model performed on your own data
    print("\n--- Evaluating model on your full synthetic dataset ---")
    predictions = model.predict(X)
    predicted_labels = [1 if p == -1 else 0 for p in predictions]

    print("\nClassification Report:")
    print(classification_report(y_true, predicted_labels))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, predicted_labels))


if __name__ == '__main__':
    train_and_save_model()