import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // ramp up to 5 VUs
    { duration: '1m', target: 5 },     // hold at 5 VUs
    { duration: '30s', target: 10 },   // ramp to 10
    { duration: '1m', target: 10 },    // hold at 10
    { duration: '30s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // P95 under 2s
    errors: ['rate<0.1'],               // error rate under 10%
  },
};

const BASE_URL = 'https://erp.insightpulseai.com';

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/web/health`);
  check(healthRes, {
    'health status 200': (r) => r.status === 200,
  });
  errorRate.add(healthRes.status !== 200);

  // Login page load
  const loginStart = Date.now();
  const loginRes = http.get(`${BASE_URL}/web/login`);
  loginDuration.add(Date.now() - loginStart);
  check(loginRes, {
    'login page status 200': (r) => r.status === 200,
    'login page has form': (r) => r.body.includes('oe_login_form'),
  });
  errorRate.add(loginRes.status !== 200);

  // Static assets (CSS/JS bundle)
  const assetRes = http.get(`${BASE_URL}/web/assets/web.assets_frontend/bundle.min.css`);
  check(assetRes, {
    'assets loadable': (r) => r.status === 200 || r.status === 304,
  });

  sleep(1);
}
