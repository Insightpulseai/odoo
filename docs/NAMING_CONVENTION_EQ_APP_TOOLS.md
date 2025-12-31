# Naming Convention - Equivalent APP TOOLS

## Goals
- One monorepo: fin-workspace
- Deterministic names across DO Apps, DO Agents, droplets, domains, env, services, queues, DB objects
- Names encode: {platform}.{product}.{component}.{env}.{region}.{purpose}

## Environments
- dev | stg | prod
- region: sgp1 | blr1 | fra1 (match DO regions)

## Canonical prefixes
- repo: fin-workspace
- app (DO App Platform): fin-{product}-{app}-{env}
- agent (DO Agents): fin-{product}-agt-{name}-{env}
- droplet: fin-{product}-dro-{role}-{env}-{region}
- service (container/service name): fin_{product}_{svc}_{env}
- package/lib: @ipai/{pkg}
- event topic: fin.{product}.{domain}.{event}.v{n}
- queue: fin_{product}_{domain}_{queue}_v{n}
- db schema: fin_{product}
- db table: {schema}.{domain}_{entity}
- edge fn: fin-{product}-{fn}-{env}
- secrets/env vars: FIN_{PRODUCT}_{NAME}

## Products (examples)
- core, erp, ocr, mcp, superset, agents, orchestration

## Components
- api, web, worker, scheduler, gateway, n8n, rag, odoo, superset, mcp

## Domains / hosts
- {component}.{env}.insightpulseai.net   (preferred if you add env routing)
- {component}.insightpulseai.net        (prod default, current)

Examples:
- erp.insightpulseai.net
- superset.insightpulseai.net
- mcp.insightpulseai.net
- ocr.insightpulseai.net (recommended)
- agents.insightpulseai.net (recommended)

## DO App Platform naming examples
- fin-erp-odoo-saas-prod
- fin-ocr-ocr-service-prod
- fin-mcp-coordinator-prod
- fin-analytics-superset-prod

## DO Agent naming examples
- fin-agents-agt-kubernetes-genius-prod
- fin-agents-agt-agent-prod

## Droplet naming examples
- fin-erp-dro-odoo-prod-sgp1
- fin-ocr-dro-ocr-prod-sgp1

## K8s (if/when DOKS)
- namespace: fin-{product}-{env}
- service: fin-{svc}
- deployment: fin-{svc}
- ingress: fin-{product}-{env}
