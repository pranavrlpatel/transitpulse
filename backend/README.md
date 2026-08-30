# TransitPulse Backend

FastAPI-based crowding prediction and route recommendation API.

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Generate Data

```bash
python data/generate_data.py
```

This creates `data/transit_history.db` with ~115,000 rows of synthetic ridership data.

## Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at http://localhost:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/stops` | List all stops |
| GET | `/routes` | List all routes |
| GET | `/predict` | Single-stop crowding/delay prediction |
| GET | `/route-crowding` | Predictions for all stops on a route |
| POST | `/recommend` | Trip recommendation (naive + optimized) |
| POST | `/inject-anomaly` | Inject a demo disruption |
| POST | `/clear-anomalies` | Clear all active anomalies |
