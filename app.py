from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf

# --- 1. Initialize FastAPI App ---
app = FastAPI(
    title="Guardian UBA API",
    description="API for Real-time Insider Threat Detection"
)
templates = Jinja2Templates(directory="templates")

# --- Enable CORS for frontend JS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Load Your BEST Model (The Autoencoder) ---
print("Loading the Autoencoder model and components...")
try:
    autoencoder_model = load_model('final_autoencoder_model.h5')
    scaler = joblib.load('data_scaler.joblib')
    # Pre-fit an encoder on the full dataset to handle all possible categories
    df_full = pd.read_csv('final_labeled_dataset-modified.csv', low_memory=False)
    event_type_encoder = {
        label: index
        for index, label in enumerate(pd.factorize(df_full['event_type'].fillna('missing'))[1])
    }
    print("✅ Autoencoder model loaded successfully.")
except FileNotFoundError as e:
    print(f"🚨 Error loading model files: {e}")
    exit()

# --- In-Memory Storage ---
alerts = []

# --- Helper function for data preparation ---
def prepare_features(df_new):
    df_new['timestamp'] = pd.to_datetime(df_new['timestamp'])
    df_new['logon_hour'] = df_new['timestamp'].dt.hour
    df_new['user_daily_activity_count'] = 1  # Placeholder for real-time
    df_new['event_type_encoded'] = (
        df_new['event_type']
        .fillna('missing')
        .map(event_type_encoder)
        .fillna(-1)
        .astype(int)
    )
    return df_new

# --- API Endpoints ---
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/predict")
async def predict(request: Request):
    data = await request.json()
    df_new = pd.DataFrame([data])
    df_features = prepare_features(df_new)

    # Use the same feature set as in training
    feature_columns = ['event_type_encoded', 'logon_hour', 'user_daily_activity_count']
    X_new = df_features[feature_columns]
    X_scaled = scaler.transform(X_new)

    # Make prediction using the Autoencoder
    reconstruction = autoencoder_model.predict(X_scaled)
    loss = tf.keras.losses.mse(reconstruction, X_scaled)

    # This threshold was determined during model evaluation
    if loss[0] > 0.01:
        alert = {
            "timestamp": data.get("timestamp"),
            "user_id": data.get("user_id"),
            "activity": f"{data.get('event_type')}: {data.get('url') or data.get('filename', 'N/A')}"
        }
        alerts.append(alert)

    return {"status": "processed"}

@app.get("/get_alerts")
def get_alerts():
    return alerts

@app.get("/api/dashboard")
def get_dashboard():
    # Example stats (can later compute dynamically)
    stats = {
        "User Logins": 2847,
        "File Access Events": 18392,
        "Command Executions": 5421,
        "Risk Score Avg": 42,
    }

    # Convert alerts to frontend-friendly format
    formatted_alerts = []
    for a in alerts[-10:]:  # last 10 alerts only
        formatted_alerts.append({
            "level": "medium",  # TODO: compute severity from loss score
            "user": a["user_id"],
            "message": a["activity"],
        })

    # Dummy high-risk users (replace with real logic later)
    high_risk_users = [
        {"name": "John Doe", "department": "Marketing", "score": 87},
        {"name": "Sarah Smith", "department": "Finance", "score": 73},
    ]

    return {
        "stats": stats,
        "alerts": formatted_alerts,
        "high_risk_users": high_risk_users,
    }
