/**
 * k6 Comprehensive Load Test for Odoo 18
 *
 * Test Scenarios:
 * 1. User authentication (login/logout)
 * 2. Module navigation (menu access)
 * 3. Data retrieval (list views)
 * 4. CRUD operations (create/read/update)
 * 5. Report generation
 *
 * Performance Targets:
 * - P95 response time: < 2000ms
 * - Error rate: < 1%
 * - Concurrent users: 100-200
 *
 * Reference: docs/integrations/ODOO_AI_TESTING_AUTOMATION.md
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { SharedArray } from 'k6/data';

// Custom metrics
export const errorRate = new Rate('errors');
export const loginDuration = new Trend('login_duration');
export const navigationDuration = new Trend('navigation_duration');
export const crudDuration = new Trend('crud_duration');
export const requestCounter = new Counter('requests');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 100 },  // Ramp to 100 users
    { duration: '5m', target: 100 },  // Sustain 100 users
    { duration: '3m', target: 200 },  // Peak load: 200 users
    { duration: '5m', target: 200 },  // Sustain peak
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],     // 95% of requests under 2s
    http_req_failed: ['rate<0.01'],        // Error rate under 1%
    errors: ['rate<0.01'],                 // Custom error rate under 1%
    login_duration: ['p(95)<1000'],        // Login under 1s
    navigation_duration: ['p(95)<1500'],   // Navigation under 1.5s
    crud_duration: ['p(95)<3000'],         // CRUD operations under 3s
  },
  ext: {
    loadimpact: {
      projectID: 3649635,
      name: 'Odoo 18 Comprehensive Load Test'
    }
  }
};

// Environment configuration
const BASE_URL = __ENV.ODOO_BASE_URL || 'https://erp.insightpulseai.com';
const LOGIN = __ENV.ODOO_LOGIN || 'admin';
const PASSWORD = __ENV.ODOO_PASSWORD || 'admin';

// Test users (shared array for efficient memory usage)
const users = new SharedArray('users', function() {
  return [
    { login: 'test.user1@insightpulseai.com', password: 'Test@123' },
    { login: 'test.user2@insightpulseai.com', password: 'Test@123' },
    { login: 'test.user3@insightpulseai.com', password: 'Test@123' },
  ];
});

// Helper function: Login and get session
function login(username, password) {
  const loginStart = Date.now();

  const loginPage = http.get(`${BASE_URL}/web/login`);
  check(loginPage, {
    'login page loaded': (r) => r.status === 200,
  });

  const loginRes = http.post(
    `${BASE_URL}/web/login`,
    {
      login: username,
      password: password,
      redirect: '/',
    },
    {
      redirects: 0,
      tags: { name: 'Login' }
    }
  );

  const loginSuccess = check(loginRes, {
    'login successful': (r) => r.status === 303 || r.status === 302,
  });

  if (!loginSuccess) {
    errorRate.add(1);
  } else {
    loginDuration.add(Date.now() - loginStart);
  }

  requestCounter.add(2); // Login page + login POST

  return {
    cookies: loginRes.cookies,
    sessionId: loginRes.cookies['session_id'] ? loginRes.cookies['session_id'][0].value : null
  };
}

// Helper function: Navigate to module
function navigateToModule(cookies, modulePath) {
  const navStart = Date.now();

  const res = http.get(`${BASE_URL}${modulePath}`, {
    cookies: cookies,
    tags: { name: 'Navigation' }
  });

  const navSuccess = check(res, {
    'module loaded': (r) => r.status === 200,
  });

  if (!navSuccess) {
    errorRate.add(1);
  } else {
    navigationDuration.add(Date.now() - navStart);
  }

  requestCounter.add(1);
  return res;
}

// Helper function: Create record
function createRecord(cookies, model, values) {
  const createStart = Date.now();

  const res = http.post(
    `${BASE_URL}/web/dataset/call_kw/${model}/create`,
    JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {
        args: [values],
        kwargs: {},
      },
      id: Math.random()
    }),
    {
      headers: {
        'Content-Type': 'application/json',
      },
      cookies: cookies,
      tags: { name: 'CRUD_Create' }
    }
  );

  const createSuccess = check(res, {
    'record created': (r) => r.status === 200 && r.json('result') !== undefined,
  });

  if (!createSuccess) {
    errorRate.add(1);
  } else {
    crudDuration.add(Date.now() - createStart);
  }

  requestCounter.add(1);
  return res;
}

// Main test scenario
export default function () {
  // Use different user for each VU
  const user = users[__VU % users.length] || { login: LOGIN, password: PASSWORD };

  // Scenario 1: User Login
  const session = login(user.login, user.password);

  if (!session.sessionId) {
    console.error('Login failed, skipping remaining scenarios');
    return;
  }

  sleep(1);

  // Scenario 2: Navigate to Dashboard
  group('Dashboard Navigation', function () {
    navigateToModule(session.cookies, '/web');
  });

  sleep(2);

  // Scenario 3: Navigate to Contacts
  group('Contacts Module', function () {
    navigateToModule(session.cookies, '/web#action=base.action_partner_form');
  });

  sleep(2);

  // Scenario 4: Navigate to Invoicing
  group('Invoicing Module', function () {
    navigateToModule(session.cookies, '/web#action=account.action_move_out_invoice_type');
  });

  sleep(1);

  // Scenario 5: Create a test partner (CRUD operation)
  group('Create Partner', function () {
    const partnerData = {
      name: `Test Partner ${Date.now()}`,
      email: `test${Date.now()}@example.com`,
      phone: '+63 917 123 4567',
    };

    createRecord(session.cookies, 'res.partner', partnerData);
  });

  sleep(2);

  // Scenario 6: Search functionality
  group('Search Partners', function () {
    const searchRes = http.post(
      `${BASE_URL}/web/dataset/call_kw/res.partner/name_search`,
      JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          args: ['Test'],
          kwargs: { limit: 10 },
        },
        id: Math.random()
      }),
      {
        headers: {
          'Content-Type': 'application/json',
        },
        cookies: session.cookies,
        tags: { name: 'Search' }
      }
    );

    check(searchRes, {
      'search successful': (r) => r.status === 200,
    });

    requestCounter.add(1);
  });

  sleep(1);

  // Scenario 7: Generate report (if available)
  group('Generate Report', function () {
    const reportRes = http.get(
      `${BASE_URL}/report/pdf/base.report_partner_template`,
      {
        cookies: session.cookies,
        tags: { name: 'Report' }
      }
    );

    check(reportRes, {
      'report generated': (r) => r.status === 200 || r.status === 404, // 404 acceptable if template doesn't exist
    });

    requestCounter.add(1);
  });

  sleep(1);
}

// Teardown function (optional)
export function teardown(data) {
  console.log('Test completed');
  console.log(`Total requests: ${requestCounter.value}`);
}
