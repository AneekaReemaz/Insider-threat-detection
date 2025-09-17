import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def create_and_save_autoencoder():
    """
    This script builds, trains, and saves the final Autoencoder model
    and the data scaler needed for the dashboard application.
    """
    # --- 1. Load and Prepare Data ---
    cert_data_filename = 'final_labeled_dataset-modified.csv'
    
    try:
        df = pd.read_csv(cert_data_filename, low_memory=False)
    except FileNotFoundError:
        print(f"Error: CERT data file '{cert_data_filename}' not found.")
        return

    print("Starting Autoencoder training and saving process...")
    
    # --- Feature Engineering ---
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['logon_hour'] = df['timestamp'].dt.hour
    daily_activity = df.groupby(['user_id', 'date']).size().reset_index(name='user_daily_activity_count')
    df = pd.merge(df, daily_activity, on=['user_id', 'date'], how='left')

    feature_columns = ["event_type", "logon_hour", "user_daily_activity_count"]
    
    for col in ["event_type"]:
        df[col] = df[col].fillna('missing')
        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(df[col].astype(str))
        
    X = df[feature_columns]
    y_true = df['is_malicious']

    # --- 2. Data Scaling for Neural Networks ---
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # --- 3. Separate Data for Training ---
    X_train_normal = X_scaled[y_true == 0]
    print(f"Training the Autoencoder on {len(X_train_normal)} 'normal' events.")

    # --- 4. Build and Train the Autoencoder Model ---
    input_dim = X_train_normal.shape[1]
    input_layer = Input(shape=(input_dim,))
    encoder_layer = Dense(2, activation="relu")(input_layer)
    decoder_layer = Dense(input_dim, activation='sigmoid')(encoder_layer)
    autoencoder = Model(inputs=input_layer, outputs=decoder_layer)

    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    
    print("Training the Autoencoder...")
    autoencoder.fit(X_train_normal, X_train_normal,
                    epochs=20,
                    batch_size=32,
                    shuffle=True,
                    verbose=0) # Set verbose to 0 to keep the output clean
    
    print("Training complete.")
    
    # --- 5. SAVE THE FINAL MODEL AND SCALER ---
    print("Saving the final Autoencoder model as 'final_autoencoder_model.h5'...")
    autoencoder.save('final_autoencoder_model.h5')
    
    print("Saving the data scaler as 'data_scaler.joblib'...")
    joblib.dump(scaler, 'data_scaler.joblib')
    
    print("\nModel and scaler saved successfully!")
    print("You are now ready to build the dashboard.")


if __name__ == '__main__':
    create_and_save_autoencoder()