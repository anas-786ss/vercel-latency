from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
import json

app = FastAPI()

# Allow POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

class Query(BaseModel):
    regions: List[str]
    threshold_ms: float

def p95(arr):
    n = len(arr)
    if n == 0: return 0.0
    s = sorted(arr)
    pos = (n - 1) * 0.95
    low = int(pos)
    high = min(low + 1, n - 1)
    if low == high: return float(s[low])
    frac = pos - low
    return float(s[low] * (1 - frac) + s[high] * frac)

DATA_PATH = Path(__file__).parent.parent / "data" / "telemetry.json"
try:
    telemetry = json.loads(DATA_PATH.read_text())
except Exception:
    telemetry = []

@app.post("/api/analytics")
def analytics(q: Query) -> Dict[str, Any]:
    out = {}
    for region in q.regions:
        recs = [r for r in telemetry if r.get("region") == region]
        if not recs:
            out[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue
        lat = [float(r["latency_ms"]) for r in recs]
        up = [float(r["uptime_pct"]) for r in recs]
        avg_latency = sum(lat) / len(lat)
        p95_latency = p95(lat)
        avg_uptime = sum(up) / len(up)
        breaches = sum(1 for l in lat if l > q.threshold_ms)
        out[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": breaches,
        }
    return out
