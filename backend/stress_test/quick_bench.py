"""
Lightweight concurrent perf baseline (S12) — no external load-test dependency.

Fires N concurrent requests per endpoint against a running backend and reports
p50/p95/max latency and throughput. Not a substitute for a full locust soak,
but a reproducible baseline that runs anywhere with the stdlib + a token.

Usage:
    python stress_test/quick_bench.py --host http://localhost:8020 \
        --email admin@valuadis.com --password password123 \
        --concurrency 20 --requests 200
"""

import argparse
import json
import statistics
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor


def _request(method, url, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    start = time.perf_counter()
    status = 0
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception:
        status = -1
    return status, (time.perf_counter() - start) * 1000.0


def bench(name, method, url, token, total, concurrency):
    latencies = []
    statuses = []
    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_request, method, url, token) for _ in range(total)]
        for f in futures:
            s, ms = f.result()
            statuses.append(s)
            latencies.append(ms)
    wall = time.perf_counter() - wall_start
    ok = sum(1 for s in statuses if 200 <= s < 400)
    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    return {
        "endpoint": name,
        "requests": total,
        "ok": ok,
        "error_rate_pct": round((total - ok) / total * 100, 2),
        "p50_ms": round(p50, 1),
        "p95_ms": round(p95, 1),
        "max_ms": round(max(latencies), 1),
        "throughput_rps": round(total / wall, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:8020")
    ap.add_argument("--email", default="admin@valuadis.com")
    ap.add_argument("--password", default="password123")
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--requests", type=int, default=200)
    args = ap.parse_args()

    api = f"{args.host}/api/v1"
    status, _ = _request("POST", f"{api}/auth/login", body={"email": args.email, "password": args.password})
    token = None
    if status == 200:
        # re-fetch to capture the body (bench _request discards it)
        req = urllib.request.Request(
            f"{api}/auth/login",
            data=json.dumps({"email": args.email, "password": args.password}).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            token = json.loads(resp.read())["data"]["access_token"]

    plan = [
        ("GET /health", "GET", f"{api}/health", None),
        ("GET /health/detailed", "GET", f"{api}/health/detailed", None),
        ("POST /auth/login", "POST", f"{api}/auth/login", None),  # includes bcrypt cost
        ("GET /properties", "GET", f"{api}/properties", token),
        ("GET /valuations/", "GET", f"{api}/valuations/", token),
        ("GET /analytics/dashboard", "GET", f"{api}/analytics/dashboard", token),
    ]
    results = []
    for name, method, url, tok in plan:
        # login benchmark needs a body; special-case it
        if name == "POST /auth/login":
            latencies = []
            statuses = []
            wall_start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
                futs = [pool.submit(_request, "POST", url, None,
                                    {"email": args.email, "password": args.password})
                        for _ in range(args.requests)]
                for f in futs:
                    s, ms = f.result()
                    statuses.append(s); latencies.append(ms)
            wall = time.perf_counter() - wall_start
            latencies.sort()
            results.append({
                "endpoint": name, "requests": args.requests,
                "ok": sum(1 for s in statuses if 200 <= s < 400),
                "error_rate_pct": round(sum(1 for s in statuses if not (200 <= s < 400)) / args.requests * 100, 2),
                "p50_ms": round(statistics.median(latencies), 1),
                "p95_ms": round(latencies[int(len(latencies) * 0.95) - 1], 1),
                "max_ms": round(max(latencies), 1),
                "throughput_rps": round(args.requests / wall, 1),
            })
        else:
            results.append(bench(name, method, url, tok, args.requests, args.concurrency))

    print(json.dumps({"host": args.host, "concurrency": args.concurrency,
                      "requests_per_endpoint": args.requests, "results": results}, indent=2))


if __name__ == "__main__":
    main()
