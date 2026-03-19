# PRD: Supabase Platform Kit Observability

## Overview

Build a unified observability platform using Supabase Platform Kit as the foundation, extending it with custom tabs for agent orchestration, job bus management, service health monitoring, and ecosystem topology visualization.

## Problem Statement

Current infrastructure has fragmented observability:
- `control-room-api` manages jobs in `runtime.cr_*` tables
- `agent_coordination` schema handles agent registry separately
- Health checks scattered across multiple scripts
- No unified "bird's eye view" of the ecosystem

## Solution

Integrate Supabase Platform Kit dialog with custom extensions:

1. **Jobs Tab** - Real-time job queue visualization, status FSM, retry controls
2. **Agents Tab** - Agent registry, capabilities discovery, heartbeat monitoring
3. **Health Tab** - Service health aggregation, connectivity matrix, alerts
4. **Topology Tab** - Ecosystem graph showing services, agents, data flows

## User Stories

### US-1: View Job Queue
As an operator, I want to see all jobs across the ecosystem in one view so I can monitor processing and identify bottlenecks.

**Acceptance Criteria:**
- List jobs with filters (source, type, status, priority)
- Show job details (payload, context, runs, events)
- Retry failed jobs with one click
- View dead letter queue separately

### US-2: Monitor Agent Fleet
As a platform admin, I want to see all registered agents and their health so I can ensure the AI fleet is operational.

**Acceptance Criteria:**
- List agents with capabilities, status, last heartbeat
- Filter by capabilities, tags, tools
- View agent metrics (queue depth, resource usage)
- Manually mark agents as maintenance mode

### US-3: Check Service Health
As an SRE, I want a unified health dashboard so I can quickly identify degraded services.

**Acceptance Criteria:**
- Aggregate health from all services (Odoo, n8n, MCP, Supabase)
- Show connectivity matrix (which services can reach which)
- Display historical uptime metrics
- Configure alert thresholds

### US-4: Visualize Ecosystem Topology
As an architect, I want to see how services, agents, and data flows connect so I can understand the system structure.

**Acceptance Criteria:**
- Graph view with nodes (services, agents, databases)
- Edges show data flow and dependencies
- Filter by domain (AI, Finance, Platform)
- Highlight critical paths

### US-5: Execute AI-Powered SQL Queries
As a data analyst, I want to ask questions in natural language and get SQL so I can explore the observability data.

**Acceptance Criteria:**
- Input field for natural language prompts
- AI generates SQL against observability schema
- Execute query and display results
- Save queries for reuse

## Technical Requirements

### Database Schema

New schema: `observability`
- `jobs` - Unified job queue (supersedes `runtime.cr_jobs`)
- `job_runs` - Execution history per attempt
- `job_events` - Granular event log (started, progress, completed, failed)
- `dead_letter_queue` - Failed jobs after max retries
- `services` - Service registry with health status
- `service_health` - Historical health samples
- `ecosystem_edges` - Service/agent dependency graph

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/observability/jobs` | List jobs |
| GET | `/api/observability/jobs/[id]` | Job details |
| POST | `/api/observability/jobs/[id]/retry` | Retry job |
| GET | `/api/observability/agents` | List agents |
| GET | `/api/observability/health` | Aggregate health |
| GET | `/api/observability/topology` | Ecosystem graph |
| POST | `/api/ai/sql` | Generate SQL from prompt |

### Frontend Components

| Component | Purpose |
|-----------|---------|
| `ObservabilityManager` | Platform Kit dialog with custom tabs |
| `JobsTab` | Job queue table with filters |
| `AgentsTab` | Agent registry with capabilities |
| `HealthTab` | Service health dashboard |
| `TopologyTab` | Ecosystem graph visualization |
| `AIQueryPanel` | Natural language SQL interface |

## Non-Functional Requirements

- **Latency**: Health check aggregation < 2s
- **Refresh**: Real-time updates via Supabase Realtime subscriptions
- **Mobile**: Responsive drawer on mobile screens
- **Scale**: Support 10,000+ jobs, 100+ agents, 20+ services

## Success Metrics

| Metric | Target |
|--------|--------|
| Mean time to detect (MTTD) degradation | < 30 seconds |
| Mean time to recovery (MTTR) | < 5 minutes |
| Job visibility coverage | 100% (all sources) |
| Agent uptime | > 99.5% |

## Out of Scope

- Alerting integrations (PagerDuty, Slack) - future phase
- Cost attribution - future phase
- Multi-tenant isolation - future phase
