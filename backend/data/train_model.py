import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import state, propagation

def _is_active(a: dict, dt: datetime) -> bool:
    start_dt = datetime.fromisoformat(a["started_at"])
    end_dt = datetime.fromisoformat(a["expires_at"])
    return start_dt <= dt < end_dt

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'transit_history.db')
    if not os.path.exists(db_path):
        print("Database not found! Run generate_data.py first.")
        return
        
    print("Loading data from SQLite...")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM history", conn)
    conn.close()

    print(f"Data loaded: {len(df)} rows. Building features...")
    
    # Feature 1 & 2: hour, day_of_week
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Target
    df['target_crowding'] = df['ridership'] / df['capacity']
    
    # We now read disruption_multiplier_at_time directly from the DB!
    # generate_data.py computed it using propagation.py during generation.
    
    features = ['hour', 'day_of_week', 'weather_intensity_mm', 'disruption_multiplier_at_time']
    X = df[features]
    y = df['target_crowding']
    
    # 80/20 train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"\nData split:")
    print(f"  Training set: {len(X_train):,} rows")
    print(f"  Testing set:  {len(X_test):,} rows")
    
    print("\nTraining XGBRegressor...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    print("Evaluating on held-out TEST set...")
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"  TEST MAE: {mae:.4f}")
    print(f"  TEST R²:  {r2:.4f}")
    
    model_path = os.path.join(os.path.dirname(__file__), 'crowding_model.joblib')
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
    
    print("\nFeature Importances:")
    importances = model.feature_importances_
    for name, imp in zip(features, importances):
        print(f"  {name}: {imp:.4f}")

if __name__ == "__main__":
    main()
