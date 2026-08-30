import sys
import os
from unittest.mock import patch
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app import prediction, propagation

def main():
    # Force load the model
    prediction._load_ml_model()
    
    stop_id = "20922"
    ts = datetime(2025, 7, 2, 8, 30, 0)
    weather = 5.0
    
    print("Testing Monotonicity of disruption_multiplier_at_time...")
    print(f"Fixed inputs: hour=8.5, day=2, weather={weather}mm\n")
    
    multipliers = [1.0, 1.3, 1.6, 1.9]
    for mult in multipliers:
        with patch('backend.app.propagation.get_disruption_multiplier', return_value=mult):
            pred = prediction.predict_crowding_ml(stop_id, ts, weather)
            print(f"Disruption Multiplier: {mult:.1f}  =>  Predicted Crowding: {pred:.4f}")

if __name__ == "__main__":
    main()
