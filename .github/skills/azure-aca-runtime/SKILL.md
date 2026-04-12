---
name: azure-aca-runtime
description: Validate ACA runtime configuration for Odoo and agent workloads covering scaling, health probes, managed identity, and Front Door integration
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [aca, runtime, networking, observability]
---

# azure-aca-runtime

**Impact tier**: P1 -- Operational Readiness

## Purpose

Validate Azure Container Apps runtime configuration for Odoo and agent
workloads — covering scaling rules, health probes, managed identity bindings,
revision management strategy, ingress configuration, and Azure Front Door
integration. Ensures the `ca-ipai-dev` environment and its container apps
are configured to production-grade ACA patterns before go-live.

## When to Use

- Before promoting any ACA container app from dev to staging or production.
- When a container app restarts unexpectedly or fails health checks.
- When scaling behavior is incorrect under load (over- or under-scaling).
- When Front Door reports unhealthy origin or routing mismatches.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `docs/architecture/runtime-container-contract.md` | Canonical container runtime requirements: probes, scaling floors/ceilings |
| `docs/architecture/azure/AZURE_ODOOSH_EQUIVALENT.md` | Odoo.sh parity mapping to ACA runtime configuration |
| `ssot/azure/runtime_topology.yaml` | App names, revision modes, ingress settings, min/max replicas |
| `ssot/azure/stamp_topology.yaml` | Environment/stamp layout, Front Door origin group configuration |
| `infra/azure/` | Bicep/IaC modules for ACA environment and app definitions |
| `docker/` | Dockerfiles — EXPOSE declarations, HEALTHCHECK instructions |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure Container Apps scaling rules HTTP KEDA")`
   -- retrieves HTTP scaling rule syntax, KEDA custom scalers, min/max replica config.
2. `microsoft_docs_search("Azure Container Apps health probes liveness readiness startup")`
   -- retrieves probe types, recommended timeouts and thresholds for web apps.
3. `microsoft_docs_search("Azure Container Apps managed identity Key Vault secret")`
   -- retrieves system-assigned vs user-assigned MI, Key Vault secret binding.
4. `microsoft_docs_search("Azure Container Apps revision management blue green traffic split")`
   -- retrieves single/multiple revision modes, traffic weight, revision suffixes.
5. `microsoft_docs_search("Azure Front Door Container Apps origin private link")`
   -- retrieves Front Door Premium + ACA private link origin, health probe settings.

Optional:

6. `microsoft_code_sample_search("bicep container app health probe managed identity", language="bicep")`
7. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/container-apps/scale-app")`

## Workflow

1. **Inspect repo** -- Read `ssot/azure/runtime_topology.yaml` and the Bicep
   modules in `infra/azure/`. Record: revision mode, min/max replicas, probe
   definitions, ingress targetPort, managed identity reference, and Front Door
   origin configuration.
2. **Query MCP** -- Run queries 1-5. Capture recommended min replicas for
   production (>= 2 for HA), probe timeout recommendations for Odoo startup
   (startup probe: 300s timeout, 60s period for slow initialization), and
   MI binding pattern for Key Vault secrets.
3. **Compare** -- Identify: (a) apps with `minReplicas: 0` in production
   (cold-start risk for ERP), (b) missing liveness/readiness probes,
   (c) MI not configured on apps accessing Key Vault, (d) revision mode
   `Single` on apps that need zero-downtime deploys.
4. **Patch** -- Update Bicep to add probes, set `minReplicas: 1` for Odoo
   app, configure managed identity, set revision mode to `Multiple` with
   traffic split for zero-downtime. Update `ssot/azure/runtime_topology.yaml`
   to reflect the target state.
5. **Verify** -- `az bicep build` lints clean. SSOT YAML updated. Diff confirms
   no app in production has `minReplicas: 0` and all apps have at least a
   liveness probe.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/container-app.bicep` | Probes, scaling rules, managed identity, revision mode |
| `infra/azure/modules/aca-environment.bicep` | Front Door origin, ingress config |
| `ssot/azure/runtime_topology.yaml` | minReplicas, probes, revision mode per app |
| `ssot/azure/stamp_topology.yaml` | Front Door origin group health probe settings |
| `docs/evidence/<stamp>/azure-aca-runtime/` | Bicep diffs, MCP excerpts, probe config |

## Completion Criteria

- [ ] Odoo container app has `minReplicas >= 1` in all non-ephemeral environments.
- [ ] All container apps have a liveness probe and a readiness probe defined.
- [ ] Startup probe timeout covers Odoo initialization (>= 120s for dev, >= 300s for prod).
- [ ] All apps accessing Key Vault have managed identity (system or user-assigned) configured.
- [ ] Odoo app revision mode is `Multiple` with explicit traffic weight rules.
- [ ] Front Door origin health probe path returns HTTP 200 (e.g. `/web/health`).
- [ ] SSOT `runtime_topology.yaml` reflects the deployed state for all apps.
- [ ] Evidence directory contains Bicep diffs and MCP excerpts.
