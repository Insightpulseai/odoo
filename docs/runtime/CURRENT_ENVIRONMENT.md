# Current Environment

## Environment type

Shared live sandbox / demo environment

## Not production

This environment does not contain canonical production business data and must not be treated as production.

> If it has no real production data, it is not production even if it is publicly reachable.

## Live endpoints

- erp.insightpulseai.com → Odoo
- plane.insightpulseai.com → Plane
- superset.insightpulseai.com → Superset
- shelf.insightpulseai.com → Shelf
- mcp.insightpulseai.com → MCP service

## Current purpose

- Integration testing
- UI validation
- Auth/mail checks
- Service connectivity
- Internal demos

## Current constraints

- Shared host/origin
- Mixed auth patterns
- Non-production data
- Incomplete health/SSO consistency

## Environment states (canonical)

| State | Meaning |
|-------|---------|
| **Local** | Developer machine, Docker Compose, localhost |
| **Shared Live Sandbox** | Current state — publicly reachable, non-production data |
| **Future Production** | Not yet established — requires real business data, SLAs, backups |

## Prohibited terminology for current environment

Do not use:

- prod / production
- production rollout / cutover / readiness
- enterprise live

Use instead:

- shared live sandbox
- demo environment
- integration environment
