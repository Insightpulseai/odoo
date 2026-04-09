# Performance Baseline: IPAI Odoo ERP

**Date**: 2026-04-05T02:00:00+08:00
**Target**: `https://erp.insightpulseai.com`
**Infrastructure**: Odoo CE 18 on Azure Container Apps, behind Azure Front Door
**Test origin**: macOS client (Southeast Asia)

---

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Tool | `curl` with timing (sequential requests) |
| Health endpoint | `/web/health` (20 requests) |
| Login endpoint | `/web/login` (20 requests) |
| Asset endpoint | `/web/assets/web.assets_frontend/bundle.min.css` (10 requests) |
| Concurrency | 1 (sequential baseline) |
| k6 script | Created at `scripts/perf/k6_odoo_baseline.js` for future concurrent testing |

---

## Key Metrics: `/web/health` (20 requests)

| Metric | Value |
|--------|-------|
| Error rate | **0%** (20/20 HTTP 200) |
| Min | 215ms |
| P50 (median) | 278ms |
| P95 | 324ms |
| P99 | 330ms |
| Max | 330ms |
| Mean | 272ms |
| Avg connect | 31ms |
| Response size | 18 bytes |

## Key Metrics: `/web/login` (20 requests)

| Metric | Value |
|--------|-------|
| Error rate | **0%** (20/20 HTTP 200) |
| Min | 203ms |
| P50 (median) | 259ms |
| P95 | 339ms |
| P99 | 391ms |
| Max | 391ms |
| Mean | 264ms |
| Avg connect | 32ms |
| Response size | 4,567 bytes |
| Login form present | YES (`oe_login_form` confirmed) |

## Key Metrics: `/web/assets/.../bundle.min.css` (10 requests)

| Metric | Value |
|--------|-------|
| Error rate | **100%** (10/10 HTTP 404) |
| Note | Expected: Odoo uses content-hashed asset URLs, not this static path |
| Mean response | 274ms |

---

## Summary

| Threshold | Target | Actual | Status |
|-----------|--------|--------|--------|
| Health P95 < 2000ms | 2000ms | **324ms** | PASS |
| Login P95 < 2000ms | 2000ms | **339ms** | PASS |
| Error rate < 10% | 10% | **0%** (health, login) | PASS |
| Throughput | n/a | ~2 req/s (sequential) | Baseline |

---

## Assessment

1. **All thresholds pass** for sequential single-client load.
2. Health endpoint responds consistently in 215-330ms (low variance, ~115ms spread).
3. Login page responds in 203-391ms with correct HTML content.
4. Connection time averages 31ms (expected for Southeast Asia to Southeast Asia via Azure Front Door).
5. TTFB closely tracks total time, indicating minimal transfer overhead (small payloads).

## Limitations

- This is a **single-client sequential baseline**, not a concurrent load test.
- No authenticated session testing (no POST login, no backend page loads).
- Asset bundle URL was not resolved to the actual hashed URL.
- k6 is now installed and the script at `scripts/perf/k6_odoo_baseline.js` is ready for concurrent testing (5-10 VUs, 3.5 min ramp profile).

## Recommendations for Next Iteration

1. Run `k6 run scripts/perf/k6_odoo_baseline.js` for concurrent VU testing.
2. Add authenticated session tests (login POST + backend page loads).
3. Resolve actual asset bundle URL from login page HTML for static asset benchmarking.
4. Set up recurring performance regression testing in CI.

---

## Raw Data

- Raw output: `docs/evidence/20260405-0200/blocker-closure/k6_baseline_output.txt`
- k6 script: `scripts/perf/k6_odoo_baseline.js`
