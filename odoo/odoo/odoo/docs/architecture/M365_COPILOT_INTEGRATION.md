# M365 Copilot Integration — Architecture Reference

**Status**: Planned
**SSOT**: `ssot/integrations/m365_copilot.yaml`
**Reviewed**: 2026-03-01
**Owner**: IPAI Platform Team

---

## Overview

Microsoft 365 Copilot is the primary interaction plane for knowledge workers who need
to access IPAI Ops data — advisor findings, agentic run audit trails, and Odoo KPIs —
without leaving their M365 environment.

The integration surfaces a **declarative agent** named `insightpulseai_ops_advisor`
inside M365 Copilot. When a user asks a question that Copilot routes to this agent,
the agent calls a Supabase Edge Function broker. All data stays on IPAI infrastructure
(DigitalOcean SG1 / Supabase) — nothing is synced to Microsoft.

This document covers architecture and governance. For manifest authoring, see
`docs/architecture/M365_DECLARATIVE_AGENT_MANIFEST.md`.

---

## Architecture Diagram

```
Knowledge Worker (M365)
        |
        | natural language query
        v
+---------------------+
|   M365 Copilot      |  <-- Microsoft-hosted, routes to registered agents
|   (Copilot Studio)  |
+---------------------+
        |
        | routes to declarative agent
        v
+-------------------------------------+
| insightpulseai_ops_advisor          |
| (declarative agent manifest)        |  <-- registered in Copilot Studio
| actions: query_advisor_findings     |      manifest.json governed by SSOT
|          query_ops_runs             |
|          trigger_advisor_scan       |
|          acknowledge_finding        |
+-------------------------------------+
        |
        | HTTPS (JWT, federated connector)
        v
+-------------------------------------+
| Supabase Edge Function              |
| m365-copilot-broker                 |  <-- planned: supabase/functions/
|                                     |      m365-copilot-broker/index.ts
| - validates M365 user identity      |
| - logs call to ops.runs             |
| - dispatches to RPC operation       |
+-------------------------------------+
        |
        +--------+--------+
        |                 |
        v                 v
+---------------+  +------------------+
| Supabase DB   |  | DigitalOcean     |
| ops.runs      |  | Droplet (SG1)    |
| ops.run_events|  | Odoo CE 19.0     |
| advisor tables|  | PostgreSQL 16    |
+---------------+  +------------------+
```

---

## Declarative Agent vs Plugin vs Connector

Three extensibility models exist in M365 Copilot. IPAI uses **declarative agent**.

| Model | Description | Why IPAI chose / rejected |
|-------|-------------|--------------------------|
| **Declarative agent** | JSON manifest declares capabilities and actions. Copilot routes queries to the agent. Agent calls an external API. | **Chosen.** Minimal surface area. No code runs inside Microsoft. Actions are explicit and allowlisted in SSOT. |
| **Copilot plugin** (API plugin) | Similar to declarative agent but the OpenAPI spec is served live. Copilot calls the API directly. | Not chosen. Equivalent capability; declarative agent format is simpler for SSOT governance. |
| **Microsoft Graph connector** | Syncs external data into Microsoft's semantic index. Copilot uses indexed data. | **Rejected.** Requires data egress to Microsoft. Violates data residency requirement (data must stay in SG1). |

---

## Federated Connector Pattern

IPAI uses a **federated connector**: Copilot calls IPAI on demand rather than syncing
data to Microsoft.

```
User query
  -> Copilot routing
    -> declarative agent action
      -> HTTPS call to m365-copilot-broker (Supabase Edge Fn)
        -> live DB query / Odoo RPC
          -> structured JSON response
            -> Copilot renders response
```

Benefits of federated over Graph sync:

- **Data residency**: All data stays in DigitalOcean SG1 / Supabase. No copy in
  Microsoft's tenant.
- **Real-time freshness**: Advisor findings and run audit are always current; no
  sync lag.
- **Access control**: IPAI controls authorization (Supabase JWT + M365 identity
  claim). Microsoft cannot query data outside of an authenticated user action.
- **Audit trail**: Every call is logged to `ops.runs` before the data query executes.
- **Simpler compliance scope**: Graph connectors require indexing PII/operational data
  in Microsoft's tenant, which expands the compliance boundary.

---

## Action Broker

The `m365-copilot-broker` Supabase Edge Function is the single entry point for all
M365 Copilot -> IPAI calls.

**Planned path**: `supabase/functions/m365-copilot-broker/index.ts`
**Status**: Not yet implemented (separate PR).

### RPC Operations

| Operation | Type | Description |
|-----------|------|-------------|
| `query_advisor_findings` | query | Open findings filtered by pillar / severity |
| `query_ops_runs` | query | Recent agentic run audit entries |
| `trigger_advisor_scan` | action | Async scan trigger, returns `job_id` |
| `acknowledge_finding` | action | Acknowledge / dismiss a finding |

### Query / Action Pattern

All operations follow a uniform request envelope:

```json
{
  "operation": "query_advisor_findings",
  "caller_identity": "<M365 user UPN from JWT claim>",
  "parameters": {
    "pillar": "security",
    "severity": "high",
    "limit": 10
  }
}
```

The broker:
1. Validates the JWT (Supabase anon key + M365 identity claim).
2. Writes a `pending` row to `ops.runs` with `caller_identity` and `operation`.
3. Executes the RPC (DB query or Odoo call).
4. Updates the `ops.runs` row with outcome and response summary.
5. Returns structured JSON to Copilot.

### Audit Trail

Every call is logged to `ops.runs` before the operation executes. Fields logged:

- `caller_identity` — M365 user UPN
- `operation` — RPC operation name
- `parameters_hash` — SHA-256 of sanitized parameters (no PII values)
- `outcome` — `success` / `error`
- `duration_ms`
- `created_at`

This satisfies SOC 2 CC6.1 (logical access) and CC7.2 (system monitoring) controls.

---

## SSOT Governance

The declarative agent manifest is **generated** from SSOT YAML sources. Direct edits
to `dist/m365/agents/insightpulseai_ops_advisor/manifest.json` are forbidden.

```
SSOT sources (edit these):
  ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml
  ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml

Generator script:
  scripts/m365/generate_actions_manifest.py

Generated output (never hand-edit):
  dist/m365/agents/insightpulseai_ops_advisor/manifest.json

Drift check (CI):
  scripts/ci/check_m365_manifest_drift.py
```

CI fails the build if `manifest.json` does not match what the generator would produce
from the current SSOT YAML. See `M365_DECLARATIVE_AGENT_MANIFEST.md` for full workflow.

Allowed action IDs are declared in `actions.yaml` under `allowed_action_ids`. The drift
check also fails if the manifest contains action IDs not on this allowlist.

---

## Authentication

### M365 to Broker (Edge Function)

M365 Copilot calls the broker using an HTTPS request with a JWT. The JWT carries:

- The M365 user's UPN (user principal name) as a custom claim.
- An Azure AD app client ID (`M365_COPILOT_CLIENT_ID`) identifying the Copilot agent.

The Edge Function validates the JWT signature against the Azure AD JWKS endpoint.
The Supabase anon key is used only for internal DB access; it is never exposed to
M365.

### Required Secrets

| Secret name | Store | Purpose |
|-------------|-------|---------|
| `M365_COPILOT_TENANT_ID` | GitHub Actions Secrets | Azure AD tenant for JWT validation |
| `M365_COPILOT_CLIENT_ID` | GitHub Actions Secrets | Azure AD app client ID |
| `M365_COPILOT_CLIENT_SECRET` | Supabase Vault (`M365_COPILOT_CLIENT_SECRET`) | Azure AD app credential for token exchange |

Secrets are never hardcoded. See `ssot/secrets/registry.yaml` (when created) and
`docs/runbooks/SECRETS_SSOT.md` for the full secrets workflow.

---

## Data Residency

All IPAI data queried by M365 Copilot remains in:

- **DigitalOcean SG1** — production Odoo droplet (`178.128.112.214`)
- **Supabase** — project `spdtwktxdalcfigzeqrz` (hosted on AWS ap-southeast-1)

Microsoft receives only the structured JSON response returned by the broker. No raw
database records, no file contents, and no PII fields beyond what the user explicitly
requested are included in broker responses.

Data flows:

```
Microsoft tenant  <-->  m365-copilot-broker  <-->  Supabase / DO SG1
(Copilot response)       (Edge Function)           (source of truth)
```

Nothing flows into Microsoft's Graph, SharePoint, or Semantic Index.

---

## Scope of This Deliverable

This PR (SSOT + docs track) establishes governance artifacts. Implementation is split
into separate PRs to allow independent review and deployment:

| Track | What | PR |
|-------|------|----|
| **This PR** | SSOT YAML, architecture docs, generator + drift-check scripts | — |
| **Edge Function PR** | `supabase/functions/m365-copilot-broker/index.ts` | Separate |
| **Manifest registration PR** | Copilot Studio registration of `manifest.json` | Separate (manual step) |
| **ops.runs schema PR** | Migration adding M365 audit columns | Separate |

The generator script (`scripts/m365/generate_actions_manifest.py`) can be run today to
produce `dist/m365/agents/insightpulseai_ops_advisor/manifest.json`. The Edge Function
must exist before the manifest is registered in Copilot Studio.

---

## References

- M365 Copilot declarative agent documentation:
  `https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/declarative-agent-overview`
- M365 Copilot extensibility comparison:
  `https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/decision-guide`
- Supabase Edge Functions:
  `https://supabase.com/docs/guides/functions`
- IPAI manifest SSOT governance:
  `docs/architecture/M365_DECLARATIVE_AGENT_MANIFEST.md`
- IPAI integration SSOT:
  `ssot/integrations/m365_copilot.yaml`
- Ops audit schema:
  `ops.runs` / `ops.run_events` tables in Supabase project `spdtwktxdalcfigzeqrz`
