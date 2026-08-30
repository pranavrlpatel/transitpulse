# TransitPulse 🚇

**TransitPulse** is an intelligent public transport crowding prediction and dynamic route recommendation system. It uses Machine Learning and real-time network state propagation to help commuters find the fastest, least crowded routes, even during unexpected delays or weather disruptions.

## 🚀 Key Features

- **AI Crowding Prediction:** Leverages a trained Machine Learning model (Random Forest) combined with historical synthetic data to accurately predict crowding levels based on time of day, day of week, and current weather conditions.
- **Dynamic Cascade Propagation:** When a disruption occurs (e.g., breakdown, heavy rain), the delay ripples to downstream stops using a BFS-decay algorithm. The impact dynamically decays over time and distance, ensuring hyper-realistic network states.
- **Smart Route Recommendation:** Evaluates available routes, transfers, and future departure windows. It scores paths based on a weighted combination of wait time, crowding, and predicted delay to instantly reroute users away from disaster zones.
- **Live Weather Integration:** Pulls real-time localized weather data (via Open-Meteo API) to adjust baseline crowding and predict system-wide transit impacts automatically.
- **Interactive Disruption Simulator:** A React dashboard that allows users to instantly inject anomalies (protests, storms, breakdowns) into the network and watch the AI dynamically reroute passengers in real-time.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Scikit-Learn (ML), Pandas, NumPy, SQLite
- **Frontend:** React.js, Vite, Recharts, Custom Glassmorphism CSS

## ⚡ Quick Start

### 1. Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt

# (Optional) Regenerate synthetic transit data and retrain ML models:
python data/generate_data.py
python data/train_model.py

# Start the API server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser.

## 📁 Architecture Overview

```text
transitpulse/
├── backend/
│   ├── data/
│   │   ├── train_model.py        # ML training script
│   │   ├── crowding_model.joblib # Serialized Random Forest model
│   │   └── generate_data.py      # Synthetic data generator
│   ├── app/
│   │   ├── main.py               # FastAPI endpoints
│   │   ├── network.py            # Route/stop topology graph
│   │   ├── weather.py            # Live weather API integration
│   │   ├── prediction.py         # ML crowding & delay predictions
│   │   ├── propagation.py        # Anomaly cascade & time-decay logic
│   │   ├── recommendation.py     # Smart route scoring engine
│   │   └── state.py              # In-memory network state
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main Dashboard
│   │   ├── api.js                # API client
│   │   ├── components/
│   │   │   ├── TripSearch.jsx    # Route selector
│   │   │   ├── ComparisonCard.jsx# Naive vs Smart AI routing comparison
│   │   │   ├── AnomalyButton.jsx # Real-time disruption simulator
│   │   │   ├── StopCrowdingList.jsx # Live stop data view
│   │   │   └── RouteMap.jsx      # Network visualization
```
