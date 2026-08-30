import urllib.request
import json
from datetime import datetime

ts = datetime(2025, 7, 2, 8, 30, 0).isoformat()
stop = "20922"

print(f"--- Calling endpoints for {stop} at {ts} ---")

def fetch(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

try:
    res1 = fetch(f"http://localhost:8000/predict?stop_id={stop}&timestamp={ts}")
    res2 = fetch(f"http://localhost:8000/predict-ml?stop_id={stop}&timestamp={ts}&weather_intensity_mm=10.0")
    
    print("Heuristic (weather=fixed):")
    print(res1)
    
    print("\nML (weather=10.0):")
    print(res2)
    
    res3 = fetch(f"http://localhost:8000/predict-ml?stop_id={stop}&timestamp={ts}&weather_intensity_mm=0.0")
    print("\nML (weather=0.0):")
    print(res3)
    
except Exception as e:
    print(f"Error: {e}")
