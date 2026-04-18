# FinOps Hub -- Constitution

> Non-negotiable invariants for the IPAI FinOps cost observability plane.

---

## Purpose

**FinOps Hub** is the canonical Azure cost observability, allocation, and
optimization surface for the InsightPulseAI platform. It ingests Cost
Management exports, normalizes them to the FOCUS schema, mirrors them through
the lakehouse, and serves cost intelligence via Power BI and the Pulser
finance copilot.

It is not a billing system, not a generic BI layer, not a replacement for the
Databricks lakehouse.

---

## Core Invariants

### 1. Upstream-First, Delta-Thin

Follows Engineering Execution Doctrine. The FinOps Hub deploys from the
upstream `microsoft/finops-toolkit` (MIT) Bicep modules pinned at a known
release. IPAI-specific logic lives in a thin `ipai_finops_overlay/` delta. No
forks of upstream; Config → OCA-equivalent (upstream Bicep) → Delta.

### 2. FOCUS Schema Is Canonical

All cost data normalized to the FinOps Open Cost and Usage Specification
(FOCUS). Downstream consumers (Power BI, Pulser, Databricks) bind to FOCUS
columns only, never to raw Cost Management export schema. Upstream schema
changes are absorbed at the ingest boundary.

### 3. Power BI Is the Business-Facing Surface

Per platform Invariant #12, Power BI is the primary mandatory business BI
surface. FinOps Hub Power BI starter kits are the canonical cost dashboards.
Workbooks remain for Azure-admin operational views only.

### 4. Fabric Mirror for Agent Grounding

Hub data lands in `stipaidevlake` (canonical lake) and mirrors to OneLake via
Databricks Unity Catalog → Fabric mirror. Pulser finance copilot grounds cost
Q&A on the mirrored FOCUS tables through the MCP Knowledge/Retrieval layer,
not direct Cost Management API calls.

### 5. Sponsored Subscription Is Scope Zero

First deployment target is Azure subscription `eba824fb-332d-4623-9dfb-2c9f7ee83f4e`
(Microsoft Azure Sponsorship). Covers all 63 resources currently in inventory.
Multi-sub expansion happens only after scope-zero is stable.

### 6. Azure DevOps Is Deploy Authority

Per platform authority matrix (2026-04-16 revision), all Bicep deploys go
through Azure Pipelines. No GitHub Actions deploy path for FinOps Hub
infrastructure. Pre-merge validation (what-if, lint) may run on GHA under the
scoped exception.

### 7. No Export-Based Sprawl

Exactly one Cost Management export per scope, writing to exactly one
`stdevipai` container. No ad-hoc CSV exports, no parallel cost pipelines, no
bespoke scraping of Azure pricing APIs.

### 8. Managed Identity Only

Hub managed identity (`id-ipai-dev-data` or dedicated sibling) authenticates
all reads/writes. No connection strings, no SAS tokens, no service principal
secrets in hub configuration.

---

## Success Criteria

- Daily cost per resource group and per tag visible in Power BI within 24h of
  Azure billing close
- Pulser finance copilot answers "what did W9 Studio spend this month?" with
  grounded data
- Alerts fire within 4h on budget overrun and idle-resource detection
- Zero secrets committed to repo; all credentials in `kv-ipai-dev-sea`

---

## Non-Goals

- Replacing Databricks engineering plane for non-cost analytics
- Becoming the Odoo transactional finance ledger
- Ingesting non-Azure cost data in scope zero (multi-cloud is phase 3+)
