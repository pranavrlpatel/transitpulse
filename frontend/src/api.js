/**
 * api.js — Thin fetch wrappers for every backend endpoint.
 *
 * All functions return parsed JSON or throw on non-200.
 */

const API_BASE = 'http://localhost:8000';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

/** GET /stops — list of all stops */
export function fetchStops() {
  return request('/stops');
}

/** GET /reachable-stops — list of stops reachable from origin */
export function fetchReachableStops(origin) {
  return request(`/reachable-stops?origin=${encodeURIComponent(origin)}`);
}

/** GET /routes — list all routes with ordered stop lists */
export function fetchRoutes() {
  return request('/routes');
}

/** GET /predict?stop_id=...&timestamp=... — single-stop prediction */
export function fetchPredict(stopId, timestamp) {
  const ts = timestamp || new Date().toISOString();
  return request(`/predict?stop_id=${encodeURIComponent(stopId)}&timestamp=${encodeURIComponent(ts)}`);
}

/** GET /route-crowding?route_id=...&timestamp=... — per-stop crowding for a route */
export function fetchRouteCrowding(routeId, timestamp) {
  let url = `/route-crowding?route_id=${encodeURIComponent(routeId)}`;
  if (timestamp) url += `&timestamp=${encodeURIComponent(timestamp)}`;
  return request(url);
}

/** POST /recommend — trip recommendation */
export function fetchRecommend(origin, destination, targetTime) {
  return request('/recommend', {
    method: 'POST',
    body: JSON.stringify({
      origin,
      destination,
      target_time: targetTime || new Date().toISOString(),
    }),
  });
}

/** POST /inject-anomaly — inject a disruption */
export function injectAnomaly(stopId, severity = 0.8, type = "general") {
  return request('/inject-anomaly', {
    method: 'POST',
    body: JSON.stringify({ stop_id: stopId, severity, anomaly_type: type }),
  });
}

/** POST /clear-anomalies — clear all anomalies */
export function clearAnomalies() {
  return request('/clear-anomalies', { method: 'POST' });
}

/** GET /weather — get live weather data from backend */
export function fetchWeather() {
  return request('/weather');
}
