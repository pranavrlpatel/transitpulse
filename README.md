# TransitPulse

Public transport crowding prediction and route recommendation system.

## Features

- **Crowding Prediction** — Heuristic formula-based predictions using synthetic historical data
- **Cascade Propagation** — Disruptions at one stop ripple to downstream neighbors with BFS decay
- **Route Recommendation** — Finds best route + departure time with naive-vs-optimized comparison
- **Live Dashboard** — React frontend with auto-polling, disruption injection, and real-time updates

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python data/generate_data.py
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Architecture

```
transitpulse/
├── backend/
│   ├── data/
│   │   ├── generate_data.py      # Synthetic data generator
│   │   └── transit_history.db    # SQLite database (generated)
│   └── app/
│       ├── main.py               # FastAPI endpoints
│       ├── network.py            # Route/stop topology
│       ├── prediction.py         # Crowding/delay heuristics
│       ├── propagation.py        # Cascade decay (BFS)
│       ├── recommendation.py     # Route scoring engine
│       ├── state.py              # In-memory anomaly store
│       └── schemas.py            # Pydantic models
└── frontend/
    └── src/
        ├── App.jsx               # Dashboard layout
        ├── api.js                # Backend API client
        └── components/
            ├── TripSearch.jsx    # Origin/dest search
            ├── ComparisonCard.jsx # Naive vs recommended
            ├── StopCrowdingList.jsx # Per-stop crowding
            ├── AnomalyButton.jsx # Disruption simulator
            └── RouteMap.jsx      # Schematic route visualization
```

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Pandas, NumPy, SQLite
- **Frontend:** React (Vite), Recharts, plain fetch
