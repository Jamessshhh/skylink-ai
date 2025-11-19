# src/ml_engine.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

DELAY_MODEL_PATH = "models/delay_model.pkl"
PRICE_MODEL_PATH = "models/price_model.pkl"
ENCODER_PATH = "models/airline_encoder.pkl"
DATA_PATH = "data/real_flight_prices.csv"

def preprocess_data(df):
    """
    Cleans the real dataset to make it ready for AI.
    """
    # 1. Handle Dates
    # Ensure it's string first to handle Excel auto-formatting
    df["Date_of_Journey"] = df["Date_of_Journey"].astype(str)
    df["Journey_Day"] = pd.to_datetime(df["Date_of_Journey"], dayfirst=True).dt.day
    df["Journey_Month"] = pd.to_datetime(df["Date_of_Journey"], dayfirst=True).dt.month

    # 2. Clean Duration
    def duration_to_minutes(duration):
        h, m = 0, 0
        parts = str(duration).split()
        for part in parts:
            if 'h' in part: h = int(part.replace('h', ''))
            if 'm' in part: m = int(part.replace('m', ''))
        return h * 60 + m

    df["Duration_Mins"] = df["Duration"].apply(duration_to_minutes)
    
    # 3. Encode Categorical Data (Airline Name -> Numbers)
    le_airline = LabelEncoder()
    df["Airline_Encoded"] = le_airline.fit_transform(df["Airline"].astype(str))
    joblib.dump(le_airline, ENCODER_PATH)

    # 4. Create 'Stops' as integer
    df["Total_Stops"] = df["Total_Stops"].replace({"non-stop": 0, "1 stop": 1, "2 stops": 2, "3 stops": 3, "4 stops": 4})
    df["Total_Stops"] = df["Total_Stops"].fillna(0).astype(int)

    return df

def train_models():
    print("🧠 Training AI Models on REAL Data...")
    os.makedirs("models", exist_ok=True)
    
    if not os.path.exists(DATA_PATH):
        print(f"⚠️ File {DATA_PATH} not found!")
        return

    # --- FIX: Smart Loader (Excel vs CSV) ---
    try:
        # First, try reading as Excel (Since Kaggle data is usually XLSX)
        raw_df = pd.read_excel(DATA_PATH, engine='openpyxl')
    except:
        # If that fails, try reading as standard CSV
        try:
            raw_df = pd.read_csv(DATA_PATH)
        except Exception as e:
            print(f"❌ Could not read file. Error: {e}")
            return
    # ----------------------------------------

    df = preprocess_data(raw_df)

    # Features & Targets
    X = df[["Duration_Mins", "Total_Stops", "Airline_Encoded"]]
    y_price = df["Price"]
    
    # Train Price Model
    print("   -> Training Price Predictor...")
    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X, y_price)
    joblib.dump(reg, PRICE_MODEL_PATH)
    
    # Train Delay Model (Simulated for now)
    if not os.path.exists(DELAY_MODEL_PATH):
        print("   -> Training Delay Predictor (Simulated)...")
        np.random.seed(42)
        n_samples = 5000
        dists = np.random.randint(200, 15000, n_samples)
        weather = np.random.randint(0, 10, n_samples)
        is_legacy = np.random.randint(0, 2, n_samples)
        delay_prob = (weather / 15) + (dists / 30000) + (is_legacy * -0.1)
        labels = [1 if p > 0.5 else 0 for p in delay_prob]
        
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(pd.DataFrame({"Distance": dists, "Weather": weather, "AirlineType": is_legacy}), labels)
        joblib.dump(clf, DELAY_MODEL_PATH)
    
    print("✅ All Models Saved.")

def predict_price(duration_mins, stops, airline_name):
    # SAFETY CHECK: Ensure BOTH model and encoder exist
    if not os.path.exists(PRICE_MODEL_PATH) or not os.path.exists(ENCODER_PATH): 
        print("⚠️ Model or Encoder missing. Retraining systems...")
        train_models()
        
    reg = joblib.load(PRICE_MODEL_PATH)
    le_airline = joblib.load(ENCODER_PATH)
    
    try:
        airline_enc = le_airline.transform([airline_name])[0]
    except:
        # Fallback if airline is unknown to the model
        airline_enc = le_airline.transform([le_airline.classes_[0]])[0]
        
    price = reg.predict([[duration_mins, stops, airline_enc]])[0]
    
    # Convert INR to USD
    return round(price * 0.012, 2)

def predict_delay(distance, weather_condition, airline_name):
    if not os.path.exists(DELAY_MODEL_PATH): train_models()
    clf = joblib.load(DELAY_MODEL_PATH)
    
    weather_map = {"clear": 0, "clouds": 3, "rain": 6, "snow": 8, "storm": 10}
    w_score = 0
    for k, v in weather_map.items():
        if k in weather_condition.lower(): w_score = v
            
    is_legacy = 1 if any(x in airline_name.lower() for x in ["qantas", "singapore", "emirates", "lufthansa"]) else 0
    return clf.predict_proba([[distance, w_score, is_legacy]])[0][1]