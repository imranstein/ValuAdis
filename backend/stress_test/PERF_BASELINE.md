# ValuAdis API — performance baseline (S12)

Reproducible concurrent baseline via `stress_test/quick_bench.py` (stdlib only,
no locust dependency). Run against a fresh PostGIS DB with seeded data.

```
python stress_test/quick_bench.py --host http://localhost:8020 \
  --email admin@valuadis.com --password password123 \
  --concurrency 20 --requests 200
```

## Baseline (2026-07-13, 20 concurrent, 200 req/endpoint, local dev, PostGIS)

| Endpoint | p50 ms | p95 ms | max ms | throughput rps | error % |
|---|---|---|---|---|---|
| GET /health | 5.7 | 6.3 | 6.4 | 3306 | 0 |
| GET /health/detailed | 82.7 | 292 | 300 | 167 | 0 |
| POST /auth/login | 3792 | 4177 | 5399 | 5.3 | 0 |
| GET /properties | 52.6 | 208 | 228 | 282 | 0 |
| GET /valuations/ | 50.4 | 102 | 112 | 335 | 0 |
| GET /analytics/dashboard | 102 | 138 | 152 | 189 | 0 |

## Findings

- **Read endpoints are healthy**: 50–100 ms p50, 180–335 rps, 0% errors under
  20-way concurrency. `/health` is ~3.3k rps.
- **`/auth/login` is CPU-bound on bcrypt** (~3.8 s p50 / 5 rps under 20
  concurrent logins). A single login is ~200 ms; the slowdown is bcrypt work
  serializing on available cores. This is expected for bcrypt but is the main
  scaling limit for auth: login throughput ≈ (cores) / (bcrypt cost seconds).
  Mitigations if login volume grows: run more API workers/cores, or tune the
  bcrypt cost factor. Not a correctness bug — token refresh (added earlier)
  already avoids re-login on every request, which keeps steady-state auth cheap.
- **`/health/detailed`** carries a small penalty (82 ms p50) because it reads
  the Alembic head from disk; acceptable for a deploy probe, not a hot path.

Re-run this after infra changes and compare the table.
