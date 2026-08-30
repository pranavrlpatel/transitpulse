import json
import urllib.request
from datetime import datetime, timedelta
import threading

_cached_weather = None
_last_fetch_time = None
_cache_lock = threading.Lock()

# Bangalore coordinates
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,cloud_cover,wind_speed_10m&timezone=Asia%2FKolkata"

def get_live_weather():
    """
    Fetches live weather from Open-Meteo API using standard library.
    Caches the result for 5 minutes to avoid rate limits.
    Returns a dict with weather data.
    """
    global _cached_weather, _last_fetch_time
    
    with _cache_lock:
        now = datetime.now()
        if _cached_weather is not None and _last_fetch_time is not None:
            if now - _last_fetch_time < timedelta(minutes=5):
                return _cached_weather
                
        try:
            # Short timeout so we don't block the API
            req = urllib.request.Request(WEATHER_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    _cached_weather = data.get("current", {})
                    _last_fetch_time = now
                    return _cached_weather
        except Exception as e:
            print(f"Failed to fetch live weather: {e}")
            
    return _cached_weather or {}

def get_live_precipitation_mm() -> float:
    """Returns current precipitation in mm, defaults to 0.0 if unavailable."""
    weather = get_live_weather()
    return float(weather.get("precipitation", 0.0))

def is_raining() -> bool:
    """Returns True if it's currently raining based on the weather API."""
    weather = get_live_weather()
    code = weather.get("weather_code", 0)
    precip = weather.get("precipitation", 0.0)
    return code >= 50 or precip > 0.0
