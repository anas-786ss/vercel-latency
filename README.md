# Vercel Latency Analytics API

Serverless FastAPI endpoint deployed on Vercel.

POST `/api/analytics` with JSON body:

```json
{"regions":["apac","emea"],"threshold_ms":161}
```

Returns metrics per region (avg_latency, p95_latency, avg_uptime, breaches).
