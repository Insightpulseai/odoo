# DO Advisor Agent

**Unified DigitalOcean Infrastructure Advisor** - Azure Advisor-style intelligence for your DO + self-hosted stack.

## Overview

DO Advisor combines multiple specialized agents into a single intelligent advisor that provides:
- **Recommendations** - Cost, security, performance, reliability suggestions
- **Jobs & Automations Monitoring** - Track n8n workflows, cron jobs, scheduled tasks
- **Infrastructure Health** - DOKS, Droplets, Databases, App Platform status
- **Self-Hosted Stack Integration** - n8n, Mattermost, Superset, Odoo monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DO Advisor Agent                           │
├─────────────────────────────────────────────────────────────────┤
│  Unified Instructions (Azure Advisor-style)                     │
│  ├── Recommendations Engine                                     │
│  ├── Jobs & Automations Monitor                                 │
│  ├── Infrastructure Health Checker                              │
│  └── Self-Hosted Stack Connector                                │
├─────────────────────────────────────────────────────────────────┤
│  Connected Resources                                            │
│  ├── DigitalOcean API (DOKS, Droplets, Databases)              │
│  ├── n8n API (Workflows, Executions)                           │
│  ├── Mattermost API (Alerts, Notifications)                    │
│  ├── Superset API (Dashboards, Queries)                        │
│  └── Odoo JSON-RPC (Finance PPM, Expenses)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment

### DigitalOcean Agent Platform

1. Create new agent in Agent Platform
2. Copy instructions from `prompts/unified_advisor.md`
3. Configure endpoint access keys
4. Attach knowledge bases (optional)

### Self-Hosted (Docker)

```bash
docker-compose -f docker-compose.yml up -d
```

## Integration with fin-workspace

Add to your MCP config:
```json
{
  "mcpServers": {
    "do-advisor": {
      "url": "https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run",
      "apiKey": "${DO_ADVISOR_API_KEY}"
    }
  }
}
```

## UI Dashboard

The companion `do-advisor-ui` provides an Azure Advisor-style dashboard with:
- Recommendations panel (Cost, Security, Performance, Reliability)
- Jobs & Automations monitor
- Real-time metrics with ECharts
- Dark theme (Azure aesthetics)

See `/apps/do-advisor-ui/README.md` for setup.
