# INTERNAL THREAT DETECTION USING USER BEHAVIOR ANALYTICS (UBA)

## 1. Project Overview
Guardian UBA is an AI-powered security service designed to detect insider threats in real-time. Insider threats are notoriously difficult to identify because they originate from trusted users with legitimate system access. This project tackles that challenge by implementing a User Behavior Analytics (UBA) system that learns a baseline of normal activity and flags suspicious deviations.

The system processes user activity logs from various sources, uses a sophisticated Autoencoder neural network to identify anomalous behavior, and presents live alerts on a dynamic web dashboard designed for a Security Operations Center (SOC) team. This project moves beyond simple offline analysis by implementing a full-stack solution: a data processing pipeline, a machine learning model served by a FastAPI backend, and a vanilla JavaScript frontend for visualization.

---

## 2. ✨ Key Features
- **Centralized Log Combination**: A script (`combined_cert_data.py`) consolidates disparate log files (logon, file access, HTTPS traffic, etc.) from the CERT Insider Threat Dataset into a master, time-sorted event log.  
- **Advanced AI Anomaly Detection**: Utilizes a TensorFlow/Keras Autoencoder model to learn the deep patterns of normal user behavior. Anomalies are detected when the model fails to accurately reconstruct an activity, resulting in a high "reconstruction error."  
- **Real-time API Backend**: A high-performance FastAPI server (`app.py`) exposes endpoints to process new log events (`/predict`) and serve live alerts and statistics to the frontend (`/api/dashboard`).  
- **Dynamic Web Dashboard**: A clean HTML, CSS, and JavaScript frontend (`index.html`, `style.css`, `app.js`) that automatically polls the backend every 10 seconds to display live alerts and high-risk user information without needing a page refresh.  
- **Scalable Architecture**: The clean separation of the frontend and backend allows for independent development, testing, and future scalability.  

---

## 3. ⚙ System Architecture
The project follows a modern, decoupled, three-tier architecture, which is standard for scalable web applications.

- **Data Layer (Offline Processing)**: The `combined_cert_data.py` script is run once to process raw CERT logs into a unified dataset. The `train_autoencoder.py` script then uses this data to build, train, and save the AI model (`final_autoencoder_model.h5`) and the data scaler (`data_scaler.joblib`).  
- **Backend Layer (`app.py`)**: The FastAPI server acts as the application's brain. It loads the trained model at startup and listens for new log events from the simulator at its `/predict` endpoint. It analyzes these logs in real-time, generates alerts for anomalous events, and makes them available at the `/api/dashboard` endpoint.  
- **Frontend Layer (`index.html` & `app.js`)**: The user's web browser runs the dashboard. The `app.js` script makes continuous asynchronous calls to the backend's `/api/dashboard` endpoint to fetch the latest alerts and statistics, dynamically updating the UI.  

---

## 4. 📂 File Descriptions
- **app.py**: The FastAPI backend server. It loads the model, defines all API endpoints, and contains the core prediction logic.  
- **combined_cert_data.py**: A utility script to parse and combine the various CERT log files into a single, unified CSV file for training.  
- **train_autoencoder.py**: The machine learning script used to train the Autoencoder model and the data scaler on the combined dataset.  
- **simulate.py**: A Python script that reads the combined log file and sends events one-by-one to the backend API, simulating a live stream of user activity.  
- **index.html**: The main HTML structure for the web dashboard.  
- **style.css**: Contains all the styling rules for the dashboard to ensure a clean and professional look.  
- **app.js**: The core of the frontend. This script handles all the logic for fetching data from the backend API and dynamically updating the HTML.  
- **final_autoencoder_model.h5**: The saved, pre-trained TensorFlow/Keras Autoencoder model.  

---

## 5. 🛠 Tech Stack
- **Data Processing**: Python, Pandas  
- **Machine Learning**: TensorFlow/Keras, Scikit-learn  
- **Backend**: FastAPI, Uvicorn  
- **Frontend**: HTML, CSS, Vanilla JavaScript  

---

## 6. 🚀 Getting Started

### Installation
Clone the repository:
```bash
git clone <your-repository-url>
cd <your-repository-name>

---


# Machine Learning Pipeline

# Install Python Dependencies
pip install pandas scikit-learn

# Load Dataset
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("processed_data.csv")
print(df.head())

# Preprocess Data
X = df.drop(columns=["user_id", "timestamp", "label"], errors="ignore")
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Train Model
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate Model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Make Predictions
sample = X_test[0].reshape(1, -1)
print("Predicted:", model.predict(sample))
print("Actual:", y_test.iloc[0])

# End
print("Pipeline execution completed successfully!")


✅ This is **everything in one continuous file** — overview → features → system architecture → files → stack → install → training → running → future work.  

Do you also want me to add a **small diagram (in Markdown with mermaid)** for the architecture (data → backend → frontend), so your README preview looks even cooler?
