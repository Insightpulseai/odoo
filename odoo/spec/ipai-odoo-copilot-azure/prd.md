# PRD — ipai-odoo-copilot-azure

## Problem

InsightPulse AI needs an AI copilot integrated into Odoo for operational assistance (ask, author, livechat, transaction). Azure Foundry hosts the agent runtime; Odoo needs a configuration and policy surface to control it.

## Solution

A thin Odoo addon (`ipai_odoo_copilot`) that:
1. Provides admin settings UI for Azure Foundry connection parameters
2. Persists non-secret config in `ir.config_parameter`
3. Exposes bounded test/sync/portal actions
4. Enforces safety posture (read-only, draft-only, memory-off defaults)
5. Runs nightly healthcheck cron

## Architecture

### Physical Agent
- **Name**: `ipai-odoo-copilot-azure`
- **Project**: `data-intel-ph` (resource: `data-intel-ph-resource`, rg: `rg-data-intel-ph`)
- **Region**: East US 2
- **Model**: `gpt-4.1`
- **Version**: 1

### Logical Agents (modes of the same physical agent)
| Mode | Purpose | Tools | Write Access |
|------|---------|-------|-------------|
| Ask Agent | Answer questions about Odoo data/processes | None (retrieval only) | None |
| Authoring Agent | Draft documents, reports, emails | None | Draft-only |
| Livechat Agent | Handle website visitor questions | None | None |
| Transaction Agent | Assist with bounded CRUD operations | Bounded (future) | Draft → approve |

### Ownership Split
| Concern | Owner |
|---------|-------|
| Configuration, policy, audit | Odoo (`ipai_odoo_copilot`) |
| Model runtime, instructions | Azure Foundry |
| Knowledge retrieval | Azure AI Search |
| Traces, monitoring, evaluation | Azure Foundry |
| Auth credentials | Azure Key Vault → env vars |

## Settings Fields

| Field | Type | Default | Stored In |
|-------|------|---------|-----------|
| Foundry Enabled | Boolean | False | `ir.config_parameter` |
| Foundry Endpoint | Char | (empty) | `ir.config_parameter` |
| Foundry Project | Char | (empty) | `ir.config_parameter` |
| Agent Name | Char | `ipai-odoo-copilot-azure` | `ir.config_parameter` |
| Model Deployment | Char | `gpt-4.1` | `ir.config_parameter` |
| Search Connection | Char | (empty) | `ir.config_parameter` |
| Search Index | Char | (empty) | `ir.config_parameter` |
| Memory Enabled | Boolean | False | `ir.config_parameter` |
| Read-Only Mode | Boolean | True | `ir.config_parameter` |

## v1 Acceptance Criteria

1. Addon installs cleanly on Odoo 19 CE with `--stop-after-init`
2. Settings UI renders under Administration → IPAI Copilot
3. Test Connection validates config completeness
4. Ensure Agent logs intent without remote calls
5. Open Portal opens endpoint URL in new tab
6. Nightly healthcheck cron fires without error
7. No Azure secrets stored in Odoo DB
8. Memory defaults to off, read-only defaults to on
9. SSOT AI manifests pass integrity validation
10. Foundry evaluation runs demonstrate grounded responses

## OCA Baseline (Recommended, Not Hard Dependencies)

- `disable_odoo_online` — removes Odoo.com/Enterprise nags
- `remove_odoo_enterprise` — cleans Enterprise menu items
- `mail_debrand` — removes Odoo branding from emails
- `auditlog` — audit trail for config changes
- `password_security` — password policy enforcement
- `queue_job` — async job processing (if needed later)
- `base_name_search_improved` — better search UX
- `web_environment_ribbon` — environment indicator
- `web_responsive` — mobile-friendly backend
