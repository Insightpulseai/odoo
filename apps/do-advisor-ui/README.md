# DO Advisor UI

**Azure Advisor-style Dashboard** for DigitalOcean + Self-Hosted Stack monitoring.

## Features

- **Recommendations Panel** - Cost, Security, Performance, Reliability, Operational Excellence
- **Jobs & Automations Monitor** - n8n workflows, cron jobs, scheduled tasks
- **Real-time Metrics** - ECharts visualizations
- **Dark Theme** - Azure Portal aesthetics
- **Responsive Design** - Desktop and tablet optimized

## Screenshot

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DO Advisor                                        🔔 Alerts  ⚙️ Settings    │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│ │ 🔴 Critical: 2  │ │ 🟠 Warning: 5   │ │ 🟢 Healthy: 23  │ │ Score: 78   │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ Recommendations                          │ Jobs & Automations               │
│ ┌─────────────────────────────────────┐ │ ┌─────────────────────────────┐  │
│ │ [COST] Idle Droplet detected        │ │ │ ● W001_CLOSE    Running 5m  │  │
│ │ [SECURITY] SSL expiring in 14d      │ │ │ ○ W002_BACKUP   Scheduled   │  │
│ │ [PERF] High latency on /api/v1      │ │ │ ⚠ W003_SYNC     Stale 3d    │  │
│ └─────────────────────────────────────┘ │ │ ✗ W004_EMAIL    Failed      │  │
│                                          │ └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Metrics                                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │          [ECharts: Resource Usage, Job Success Rate, Cost Trends]       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Static Files (Nginx/Caddy)

```bash
# Copy to web server
cp -r public/* /var/www/do-advisor/

# Configure nginx
server {
    listen 443 ssl;
    server_name advisor.example.com;
    root /var/www/do-advisor;
    index index.html;
}
```

### Option 2: Docker

```bash
docker build -t do-advisor-ui .
docker run -p 8080:80 do-advisor-ui
```

### Option 3: DigitalOcean App Platform

```bash
doctl apps create --spec app-spec.yaml
```

## Configuration

Edit `public/config.js`:

```javascript
window.DO_ADVISOR_CONFIG = {
  // Agent endpoint
  agentEndpoint: 'https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run',
  agentApiKey: 'your-api-key',

  // Self-hosted stack
  n8nEndpoint: 'https://n8n.example.com',
  n8nApiKey: 'your-n8n-key',

  mattermostEndpoint: 'https://mattermost.example.com',
  supersetEndpoint: 'https://superset.example.com',
  odooEndpoint: 'https://odoo.example.com',

  // Refresh intervals (ms)
  refreshInterval: 30000,
  metricsInterval: 60000,
};
```

## Tech Stack

- **Vanilla JS** - No framework dependencies
- **ECharts 5.x** - Data visualization
- **CSS Variables** - Theming support
- **Fetch API** - Data fetching

## Integration with DO Advisor Agent

The UI communicates with the DO Advisor agent via REST API:

```javascript
// Query recommendations
POST /api/chat
{
  "messages": [
    {"role": "user", "content": "Show all recommendations in JSON format"}
  ]
}

// Response parsed into UI components
```

## File Structure

```
do-advisor-ui/
├── public/
│   ├── index.html        # Main dashboard
│   ├── config.js         # Configuration
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── recommendations.js
│   │   ├── jobs-monitor.js
│   │   ├── metrics-charts.js
│   │   └── nav-sidebar.js
│   ├── views/
│   │   ├── dashboard.js
│   │   ├── cost.js
│   │   ├── security.js
│   │   └── jobs.js
│   ├── assets/
│   │   └── styles/
│   │       ├── azure-dark.css
│   │       └── components.css
│   └── app.js
├── Dockerfile
├── app-spec.yaml         # DO App Platform spec
└── README.md
```
