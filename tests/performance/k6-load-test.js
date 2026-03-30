/**
 * K6 Load Test — ValuAdis API Performance Benchmarking
 *
 * Targets critical endpoints under 100 concurrent users.
 * Thresholds enforce p95 < 500ms and error rate < 1%.
 * Degradation threshold triggers if p95 exceeds baseline by >10%.
 *
 * Run: k6 run tests/performance/k6-load-test.js
 * With env vars: k6 run -e BASE_URL=http://localhost:8000 tests/performance/k6-load-test.js
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API_BASE = `${BASE_URL}/api/v1`;

// Baseline p95 values (ms) from baseline.json — used to detect >10% degradation
const BASELINES = {
  health_check: 50,
  login: 300,
  refresh: 200,
  list_valuations: 450,
  create_valuation: 480,
  get_valuation: 300,
  list_vehicles: 400,
};

// Degradation threshold: fail if p95 exceeds baseline by more than 10%
const DEGRADATION_FACTOR = 1.1;

// ---------------------------------------------------------------------------
// Custom Metrics
// ---------------------------------------------------------------------------

const errorRate = new Rate("custom_error_rate");
const loginDuration = new Trend("duration_login");
const listValuationsDuration = new Trend("duration_list_valuations");
const createValuationDuration = new Trend("duration_create_valuation");
const getValuationDuration = new Trend("duration_get_valuation");
const listVehiclesDuration = new Trend("duration_list_vehicles");
const healthDuration = new Trend("duration_health");
const refreshDuration = new Trend("duration_refresh");
const totalRequests = new Counter("total_requests");

// ---------------------------------------------------------------------------
// K6 Options — Load Profile
// ---------------------------------------------------------------------------

export const options = {
  stages: [
    // Ramp up to 100 concurrent users over 30s
    { duration: "30s", target: 100 },
    // Sustain 100 VUs for 60s (steady state)
    { duration: "60s", target: 100 },
    // Ramp down over 15s
    { duration: "15s", target: 0 },
  ],
  thresholds: {
    // Global HTTP error rate must stay below 1%
    http_req_failed: ["rate<0.01"],

    // Global p95 must be under 500ms (primary acceptance criterion)
    http_req_duration: ["p(95)<500", "p(99)<1000"],

    // Custom error tracking
    custom_error_rate: ["rate<0.01"],

    // Per-endpoint p95 thresholds with 10% degradation tolerance
    duration_health: [
      `p(95)<${Math.ceil(BASELINES.health_check * DEGRADATION_FACTOR)}`,
    ],
    duration_login: [
      `p(95)<${Math.ceil(BASELINES.login * DEGRADATION_FACTOR)}`,
    ],
    duration_refresh: [
      `p(95)<${Math.ceil(BASELINES.refresh * DEGRADATION_FACTOR)}`,
    ],
    duration_list_valuations: [
      `p(95)<${Math.ceil(BASELINES.list_valuations * DEGRADATION_FACTOR)}`,
    ],
    duration_create_valuation: [
      `p(95)<${Math.ceil(BASELINES.create_valuation * DEGRADATION_FACTOR)}`,
    ],
    duration_get_valuation: [
      `p(95)<${Math.ceil(BASELINES.get_valuation * DEGRADATION_FACTOR)}`,
    ],
    duration_list_vehicles: [
      `p(95)<${Math.ceil(BASELINES.list_vehicles * DEGRADATION_FACTOR)}`,
    ],
  },
};

// ---------------------------------------------------------------------------
// Shared Test Fixtures
// ---------------------------------------------------------------------------

// Generate a unique phone number per VU to avoid registration conflicts
function vuPhone() {
  // Ethiopian format: +251911XXXXXX (6-digit suffix padded)
  const suffix = String(__VU * 10 + __ITER).padStart(6, "0").slice(-6);
  return `+251911${suffix}`;
}

const commonHeaders = {
  "Content-Type": "application/json",
  Accept: "application/json",
};

// ---------------------------------------------------------------------------
// Setup: Obtain a shared auth token for read-heavy scenarios
// ---------------------------------------------------------------------------

export function setup() {
  // Use a dedicated load-test account; real deployments should seed this user
  const loginPayload = JSON.stringify({
    phone_number: __ENV.LT_PHONE || "+251911000001",
    password: __ENV.LT_PASSWORD || "LoadTest@123",
  });

  const res = http.post(`${API_BASE}/auth/login`, loginPayload, {
    headers: commonHeaders,
  });

  if (res.status !== 200) {
    console.warn(
      `Setup: login failed (${res.status}). Authenticated tests will be skipped.`
    );
    return { token: null, valuationId: null };
  }

  const body = JSON.parse(res.body);
  const token = body.access_token || body.token || null;

  // Pre-fetch an existing valuation ID for single-resource GET tests
  let valuationId = null;
  if (token) {
    const listRes = http.get(`${API_BASE}/valuations/`, {
      headers: { ...commonHeaders, Authorization: `Bearer ${token}` },
    });
    if (listRes.status === 200) {
      const listBody = JSON.parse(listRes.body);
      const items = listBody.items || listBody.valuations || listBody;
      if (Array.isArray(items) && items.length > 0) {
        valuationId = items[0].id;
      }
    }
  }

  return { token, valuationId };
}

// ---------------------------------------------------------------------------
// Main VU Scenario
// ---------------------------------------------------------------------------

export default function (data) {
  const { token, valuationId } = data;
  const authHeaders = token
    ? { ...commonHeaders, Authorization: `Bearer ${token}` }
    : commonHeaders;

  // 1. Health Check (unauthenticated — highest frequency)
  group("health_check", () => {
    const res = http.get(`${API_BASE}/health`, { headers: commonHeaders });
    healthDuration.add(res.timings.duration);
    totalRequests.add(1);

    const ok = check(res, {
      "health: status 200": (r) => r.status === 200,
      "health: response < 200ms": (r) => r.timings.duration < 200,
    });
    errorRate.add(!ok);
  });

  sleep(0.5);

  // 2. List Valuations (authenticated read — most common operation)
  group("list_valuations", () => {
    if (!token) return;
    const res = http.get(`${API_BASE}/valuations/`, { headers: authHeaders });
    listValuationsDuration.add(res.timings.duration);
    totalRequests.add(1);

    const ok = check(res, {
      "list_valuations: status 200": (r) => r.status === 200,
      "list_valuations: p95 < 500ms": (r) => r.timings.duration < 500,
    });
    errorRate.add(!ok);
  });

  sleep(0.3);

  // 3. Get Single Valuation (authenticated read)
  group("get_valuation", () => {
    if (!token || !valuationId) return;
    const res = http.get(`${API_BASE}/valuations/${valuationId}`, {
      headers: authHeaders,
    });
    getValuationDuration.add(res.timings.duration);
    totalRequests.add(1);

    const ok = check(res, {
      "get_valuation: status 200": (r) => r.status === 200,
      "get_valuation: has id field": (r) => {
        try {
          return JSON.parse(r.body).id !== undefined;
        } catch (_) {
          return false;
        }
      },
    });
    errorRate.add(!ok);
  });

  sleep(0.3);

  // 4. List Vehicles (authenticated read)
  group("list_vehicles", () => {
    if (!token) return;
    const res = http.get(`${API_BASE}/vehicles/`, { headers: authHeaders });
    listVehiclesDuration.add(res.timings.duration);
    totalRequests.add(1);

    const ok = check(res, {
      "list_vehicles: status 200": (r) => r.status === 200,
    });
    errorRate.add(!ok);
  });

  sleep(0.5);

  // 5. Token Refresh (every 5th iteration to simulate session maintenance)
  if (__ITER % 5 === 0) {
    group("token_refresh", () => {
      if (!token) return;
      const res = http.post(
        `${API_BASE}/auth/refresh`,
        JSON.stringify({}),
        { headers: authHeaders }
      );
      refreshDuration.add(res.timings.duration);
      totalRequests.add(1);

      const ok = check(res, {
        "refresh: status 200 or 201": (r) =>
          r.status === 200 || r.status === 201,
      });
      errorRate.add(!ok);
    });
  }

  // 6. Create Valuation (write operation — lower frequency, every 10th iteration)
  if (__ITER % 10 === 0) {
    group("create_valuation", () => {
      if (!token) return;
      const payload = JSON.stringify({
        property_type: "residential",
        location: "Addis Ababa",
        area_sqm: 100 + (__VU % 50),
        bedrooms: 2 + (__VU % 3),
      });
      const res = http.post(`${API_BASE}/valuations/`, payload, {
        headers: authHeaders,
      });
      createValuationDuration.add(res.timings.duration);
      totalRequests.add(1);

      const ok = check(res, {
        "create_valuation: status 200 or 201": (r) =>
          r.status === 200 || r.status === 201,
        "create_valuation: p95 < 500ms": (r) => r.timings.duration < 500,
      });
      errorRate.add(!ok);
    });
  }

  sleep(1);
}

// ---------------------------------------------------------------------------
// Teardown: Log summary
// ---------------------------------------------------------------------------

export function teardown(data) {
  console.log(`Load test complete. Total VUs: 100. Token acquired: ${!!data.token}`);
}

// ---------------------------------------------------------------------------
// Custom Summary Report
// ---------------------------------------------------------------------------

export function handleSummary(data) {
  const now = new Date().toISOString();

  // Build per-endpoint summary rows
  const endpointMetrics = [
    { name: "health_check", metric: "duration_health", baseline: BASELINES.health_check },
    { name: "login", metric: "duration_login", baseline: BASELINES.login },
    { name: "refresh", metric: "duration_refresh", baseline: BASELINES.refresh },
    { name: "list_valuations", metric: "duration_list_valuations", baseline: BASELINES.list_valuations },
    { name: "create_valuation", metric: "duration_create_valuation", baseline: BASELINES.create_valuation },
    { name: "get_valuation", metric: "duration_get_valuation", baseline: BASELINES.get_valuation },
    { name: "list_vehicles", metric: "duration_list_vehicles", baseline: BASELINES.list_vehicles },
  ].map((e) => {
    const m = data.metrics[e.metric];
    const p95 = m ? m.values["p(95)"] : null;
    const degraded =
      p95 !== null ? p95 > e.baseline * DEGRADATION_FACTOR : false;
    return {
      endpoint: e.name,
      p95_ms: p95 !== null ? Math.round(p95) : "N/A",
      baseline_ms: e.baseline,
      threshold_ms: Math.ceil(e.baseline * DEGRADATION_FACTOR),
      status: p95 === null ? "SKIPPED" : degraded ? "DEGRADED" : "PASS",
    };
  });

  const globalP95 = data.metrics["http_req_duration"]
    ? data.metrics["http_req_duration"].values["p(95)"]
    : null;
  const errorRateVal = data.metrics["http_req_failed"]
    ? data.metrics["http_req_failed"].values["rate"]
    : null;

  const report = {
    generated_at: now,
    summary: {
      global_p95_ms: globalP95 !== null ? Math.round(globalP95) : null,
      global_p95_threshold_ms: 500,
      global_p95_pass: globalP95 !== null ? globalP95 < 500 : null,
      error_rate_percent:
        errorRateVal !== null
          ? parseFloat((errorRateVal * 100).toFixed(3))
          : null,
      error_rate_threshold_percent: 1,
      error_rate_pass:
        errorRateVal !== null ? errorRateVal * 100 < 1 : null,
      max_concurrent_users: 100,
    },
    endpoint_breakdown: endpointMetrics,
    overall_status: endpointMetrics.some((e) => e.status === "DEGRADED")
      ? "DEGRADED"
      : "PASS",
  };

  return {
    // Write structured JSON report next to this script
    "tests/performance/load-test-results.json": JSON.stringify(report, null, 2),
    // Also emit human-readable text summary to stdout
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
