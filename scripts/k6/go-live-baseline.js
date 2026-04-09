// k6 Go-Live Baseline — HA + Front Door path
// Usage: k6 run scripts/k6/go-live-baseline.js --out json=results.json
//
// Scenarios:
//   1. Health check (direct HA + AFD)
//   2. Login page load (AFD only — production path)
//   3. Authenticated session (AFD only)
//
// Thresholds:
//   - Health: p95 < 500ms, error rate < 1%
//   - Login page: p95 < 2000ms, error rate < 1%
//   - Session: p95 < 3000ms, error rate < 5%

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const healthErrors = new Rate('health_errors');
const loginErrors = new Rate('login_errors');
const healthDuration = new Trend('health_duration', true);
const loginDuration = new Trend('login_duration', true);

// Endpoints
const AFD_BASE = 'https://erp.insightpulseai.com';
const HA_DIRECT = 'https://ipai-odoo-ha-web.grayhill-34461e89.southeastasia.azurecontainerapps.io';

export const options = {
  scenarios: {
    // Scenario 1: Health check — sustained load
    health_afd: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'healthCheckAFD',
      tags: { scenario: 'health_afd' },
    },
    health_direct: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'healthCheckDirect',
      tags: { scenario: 'health_direct' },
    },
    // Scenario 2: Login page — simulates user arrival
    login_page: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 5 },
        { duration: '20s', target: 10 },
        { duration: '10s', target: 0 },
      ],
      exec: 'loginPage',
      tags: { scenario: 'login_page' },
    },
    // Scenario 3: Authenticated session probe
    session_probe: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'sessionProbe',
      tags: { scenario: 'session_probe' },
    },
  },
  thresholds: {
    'http_req_duration{scenario:health_afd}': ['p(95)<500'],
    'http_req_duration{scenario:health_direct}': ['p(95)<500'],
    'http_req_duration{scenario:login_page}': ['p(95)<2000'],
    'http_req_duration{scenario:session_probe}': ['p(95)<3000'],
    'http_req_failed{scenario:health_afd}': ['rate<0.01'],
    'http_req_failed{scenario:health_direct}': ['rate<0.01'],
    'http_req_failed{scenario:login_page}': ['rate<0.01'],
    'http_req_failed{scenario:session_probe}': ['rate<0.05'],
  },
};

export function healthCheckAFD() {
  const res = http.get(`${AFD_BASE}/web/health`);
  const ok = check(res, {
    'health AFD status 200': (r) => r.status === 200,
    'health AFD < 500ms': (r) => r.timings.duration < 500,
  });
  healthErrors.add(!ok);
  healthDuration.add(res.timings.duration);
  sleep(1);
}

export function healthCheckDirect() {
  const res = http.get(`${HA_DIRECT}/web/health`, {
    headers: { Host: 'erp.insightpulseai.com' },
  });
  const ok = check(res, {
    'health direct status 200': (r) => r.status === 200,
    'health direct < 500ms': (r) => r.timings.duration < 500,
  });
  healthErrors.add(!ok);
  healthDuration.add(res.timings.duration);
  sleep(1);
}

export function loginPage() {
  const res = http.get(`${AFD_BASE}/web/login`);
  const ok = check(res, {
    'login page status 200': (r) => r.status === 200,
    'login page has form': (r) => r.body && r.body.includes('oe_login_form'),
    'login page < 2s': (r) => r.timings.duration < 2000,
  });
  loginErrors.add(!ok);
  loginDuration.add(res.timings.duration);
  sleep(2);
}

export function sessionProbe() {
  // Attempt to access /web which requires auth — should redirect to login
  const res = http.get(`${AFD_BASE}/web`, { redirects: 0 });
  check(res, {
    'web redirect or ok': (r) => r.status === 200 || r.status === 303,
    'session probe < 3s': (r) => r.timings.duration < 3000,
  });

  // Also test version info endpoint (lightweight authenticated-style check)
  const vres = http.post(`${AFD_BASE}/web/webclient/version_info`, '{}', {
    headers: { 'Content-Type': 'application/json' },
  });
  check(vres, {
    'version info responds': (r) => r.status === 200,
  });
  sleep(2);
}
