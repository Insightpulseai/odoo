import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },   // warmup
    { duration: '4m', target: 50 },   // ramp to 50 VUs
    { duration: '5m', target: 50 },   // sustain
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],     // <1% errors
    http_req_duration: ['p(95)<2000'],  // 95% < 2s
  },
};

const BASE_URL = __ENV.ODOO_BASE_URL || 'https://erp.insightpulseai.net';
const LOGIN = __ENV.ODOO_LOGIN || 'admin';
const PASSWORD = __ENV.ODOO_PASSWORD || 'admin';

export default function () {
  // 1. GET login page
  let res = http.get(`${BASE_URL}/web/login`);
  check(res, {
    'login page 200': (r) => r.status === 200,
  });

  // 2. POST login
  const loginRes = http.post(
    `${BASE_URL}/web/login`,
    {
      login: LOGIN,
      password: PASSWORD,
      redirect: '/',
    },
    {
      redirects: 0,
    },
  );

  check(loginRes, {
    'login redirect': (r) => r.status === 303 || r.status === 302,
  });

  const cookies = loginRes.cookies;

  // 3. Hit some key menus (web backend)
  const opts = { cookies };
  let homeRes = http.get(`${BASE_URL}/web`, opts);
  check(homeRes, {
    'home 200': (r) => r.status === 200,
  });

  // Example: expenses menu (adjust menu/action)
  let expenseRes = http.get(`${BASE_URL}/web#menu_id=1&action=`, opts);
  check(expenseRes, {
    'expense page 200': (r) => r.status === 200,
  });

  sleep(1);
}
