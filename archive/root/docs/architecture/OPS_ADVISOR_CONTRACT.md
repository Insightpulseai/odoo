# Ops Advisor Engine — Contract Document

> **Status**: Planned — implementation tracked on branch `feat/taskbus-agent-orchestration`
> **Last updated**: 2026-03-01
> **Owner**: ipai platform team

---

## 1. Overview

The Ops Advisor Engine is an Azure-Advisor-style recommendation system that scans
InsightPulse AI's infrastructure, code repositories, and platform services and
surfaces prioritised findings across five Well-Architected pillars.

The engine is modelled on the **GitHub Well-Architected Framework (WAF)** for
developer-platform guidance and the **DigitalOcean monitoring / best-practice docs**
for infrastructure posture. It is intentionally *read-only at execution time*:
it collects facts, evaluates rulepacks, and writes findings — it does not make
changes on the user's behalf.

**Design goals:**

| Goal | Detail |
|------|--------|
| Actionable findings | Every finding has a `title`, `severity`, `description`, `recommendation`, and `citation_url`. |
| Evidence-first | Findings carry `evidence_json` (raw API/tool output) so humans can verify before acting. |
| Workbook-guided remediation | Complex remediations are broken into step-by-step workbooks rendered in the Ops Console. |
| No Enterprise dependency | Engine is compatible with Supabase Team + Vercel Pro; no Enterprise tier required. |
| SSOT-backed | Rulepacks and workbooks live in `ssot/advisor/` and are version-controlled. |

---

## 2. Five Pillars

| Pillar | DB value | Primary source |
|--------|----------|----------------|
| Security | `security` | GitHub WAF — Application Security |
| Cost | `cost` | DigitalOcean pricing, Vercel usage |
| Reliability | `reliability` | GitHub WAF — Architecture; DO monitoring |
| Ops Excellence | `ops_excellence` | GitHub WAF — Governance, Productivity, Collaboration |
| Performance | `performance` | GitHub WAF — Architecture; Vercel Analytics |

### 2.1 GitHub Well-Architected Pillar Mapping

The GitHub WAF defines five pillars. The mapping to OdooOps pillars is:

| GitHub WAF Pillar | OdooOps Pillar(s) | Notes |
|-------------------|-------------------|-------|
| Application Security | `security` | Secret scanning, dependency alerts, CODEOWNERS |
| Governance | `ops_excellence` | Rulesets, branch policies, org policy enforcement |
| Architecture | `reliability` + `performance` | Repo structure, CI architecture, deploy pipelines |
| Productivity | `ops_excellence` + `performance` | PR cycle time, automation coverage, workflow efficiency |
| Collaboration | `ops_excellence` | Code review practices, CODEOWNERS, discussion hygiene |

**Citation**: <https://wellarchitected.github.com/library/>

---

## 3. Knowledge Base (KB)

The knowledge base backs the advisor with authoritative documentation. It is
structured as a three-layer hierarchy:

```
work.kb_sources       ← registered documentation sources (URLs)
  └── work.kb_documents    ← individual pages fetched per source
        └── work.kb_chunks  ← content chunks with FTS index
```

### 3.1 `work.kb_sources`

Registered documentation sources. Each source has a `base_url`, optional `pillar`
affinity, and a `last_synced_at` timestamp updated after each scrape.

**Seed sources (planned):**

| Name | base_url | Pillar |
|------|----------|--------|
| GitHub WAF — Governance | `https://wellarchitected.github.com/library/governance/` | `ops_excellence` |
| GitHub WAF — Application Security | `https://wellarchitected.github.com/library/application-security/` | `security` |
| GitHub WAF — Architecture | `https://wellarchitected.github.com/library/architecture/` | `reliability` |
| DO Monitoring docs | `https://docs.digitalocean.com/products/monitoring/` | `reliability` |
| DO Droplet pricing | `https://docs.digitalocean.com/products/droplets/details/pricing/` | `cost` |
| Vercel observability | `https://vercel.com/docs/observability` | `performance` |

### 3.2 `work.kb_documents`

One row per page fetched from a source. Stores the raw `content` (Markdown or
plain text after HTML stripping), `title`, canonical `url`, and optional `tags`.

### 3.3 `work.kb_chunks`

Documents are split into chunks (typically 512–1024 tokens each). Each chunk has:

- `chunk_no` — sequential position within the parent document
- `content` — raw text of this chunk
- `search_vector` — `GENERATED ALWAYS AS (to_tsvector('english', content)) STORED`

The GIN index `kb_chunks_search_vector_idx` enables fast FTS queries used by the
advisor to attach citation context to findings.

**Day 1: FTS only.** Vector embeddings (pgvector) and OTel tracing are deferred to
a subsequent migration once the KB pipeline is proven in production.

---

## 4. Advisor Runtime Tables

```
ops.advisor_scans        ← one row per scan run
  └── ops.advisor_findings  ← findings produced by the scan

ops.workbooks            ← curated remediation guides
  └── ops.workbook_steps   ← ordered steps within a workbook
```

### 4.1 `ops.advisor_scans`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `provider` | TEXT | `digitalocean` \| `vercel` \| `supabase` \| `github` |
| `started_at` | TIMESTAMPTZ | Set when scan row is inserted |
| `finished_at` | TIMESTAMPTZ | Set on `completed` or `failed` |
| `status` | TEXT | `running` → `completed` \| `failed` |
| `summary_json` | JSONB | Provider snapshot (droplet list, repo list, etc.) |

### 4.2 `ops.advisor_findings`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `scan_id` | UUID | FK → `ops.advisor_scans` |
| `pillar` | TEXT | Well-Architected pillar |
| `severity` | TEXT | `critical` \| `high` \| `medium` \| `low` \| `info` |
| `title` | TEXT | Short human-readable title |
| `description` | TEXT | Extended description |
| `resource_ref` | TEXT | e.g. `droplet:ocr-service-droplet`, `repo:Insightpulseai/odoo` |
| `evidence_json` | JSONB | Raw API/tool output |
| `recommendation` | TEXT | Human-readable remediation guidance |
| `citation_url` | TEXT | Authoritative source link |
| `status` | TEXT | `open` → `dismissed` \| `resolved` |

### 4.3 `ops.workbooks` + `ops.workbook_steps`

Workbooks are referenced by rulepacks via the `remediation_workbook` field.
When a finding is created that has a `remediation_workbook`, the Ops Console
can render the associated workbook steps interactively.

Steps with `evidence_required=true` block workbook completion until the operator
captures proof (e.g. pastes `df -h` output, links to a PR, etc.).

Steps with a non-null `automation_ref` can be executed automatically by the
Ops Console by triggering the referenced script in the taskbus.

---

## 5. Scan Adapters (Planned)

Each adapter is a stateless function that:

1. Accepts a `scan_id` (UUID).
2. Collects facts from the provider API.
3. Evaluates applicable rulepacks against those facts.
4. Writes `ops.advisor_findings` rows.
5. Updates `ops.advisor_scans.status` + `finished_at`.

| Adapter | Provider | Initial rulepacks |
|---------|----------|-------------------|
| `github` | GitHub REST/GraphQL API | `github_governance` |
| `digitalocean` | DO API v2 | `do_monitoring_posture` |
| `vercel` | Vercel REST API | _(planned: vercel_edge_posture)_ |
| `supabase` | Supabase Management API | _(planned: supabase_rls_posture)_ |

Adapter source location: `apps/ops-console/app/api/advisor/scan/[provider]/route.ts`

---

## 6. Run Scan Flow

```
Trigger (manual / scheduled / taskbus event)
    │
    ▼
POST /api/advisor/scan/{provider}
    │
    ├─ INSERT ops.advisor_scans → scan_id
    ├─ Insert ops.run row (taskbus wiring, see §7)
    │
    ├─ Adapter: collect facts from provider API
    │
    ├─ Evaluate rulepacks (ssot/advisor/rulepacks/*.yaml)
    │   for each rule:
    │     if rule fails → INSERT ops.advisor_findings
    │
    ├─ Attach workbooks to findings where remediation_workbook is set
    │
    └─ UPDATE ops.advisor_scans SET status='completed', finished_at=now()
```

On any unhandled exception: `UPDATE ops.advisor_scans SET status='failed', finished_at=now()`

---

## 7. Taskbus Wiring

The advisor integrates with the existing ops taskbus (`ops.runs` / `ops.task_queue`).

| Event | Taskbus action |
|-------|----------------|
| Scan triggered | `ops.run` row created with `type='advisor_scan'` + `payload={provider,scan_id}` |
| Scan completed | `ops.run` status updated to `completed` |
| Finding created | Optional: emit `ops.platform_events` row for Slack/n8n fanout |

Scheduled scans are registered in `ssot/runtime/schedules.yaml` and executed
by the n8n automation runner via the `ops_taskbus_schedules` workflow.

---

## 8. Initial Rulepacks

Two rulepacks ship on day 1:

| Rulepack ID | File | Pillar | Source |
|-------------|------|--------|--------|
| `github_governance` | `ssot/advisor/rulepacks/github_governance.yaml` | `ops_excellence` | GitHub WAF — Governance |
| `do_monitoring_posture` | `ssot/advisor/rulepacks/do_monitoring_posture.yaml` | `reliability` | DO Monitoring docs |

**Rulepack schema**: `ssot.advisor.rulepack.v1`

Each rule within a rulepack defines:

| Field | Purpose |
|-------|---------|
| `id` | Unique rule identifier (snake_case) |
| `title` | Short human-readable title |
| `severity` | `critical` \| `high` \| `medium` \| `low` \| `info` |
| `check` | Human-readable description of what the adapter checks |
| `citation_url` | Link to the authoritative doc section |
| `finding_template` | Template string used to populate `ops.advisor_findings.title` |
| `remediation_workbook` | (optional) ID of the workbook to attach when this rule fails |

---

## 9. Initial Workbooks

| Workbook ID | File | Pillar | Trigger rule |
|-------------|------|--------|-------------|
| `ocr_disk_saturation_remediation` | `ssot/advisor/workbooks/ocr_disk_saturation.yaml` | `reliability` | `do_monitoring_posture.ocr_disk_saturation` |

---

## 10. Evidence Requirements

Every finding **must** include a `citation_url` pointing to the authoritative
source document that explains:

1. **Why** the finding matters (risk / impact).
2. **What** the correct posture is.
3. **How** to remediate.

Findings without a `citation_url` are blocked at the rulepack validation layer
(CI check: `scripts/ci/validate_advisor_rulepacks.py` — planned).

`evidence_json` carries raw API/tool output so that:

- Operators can independently verify the finding without re-running the scan.
- The Ops Console can render provider-specific evidence (e.g. droplet metrics,
  GitHub API response excerpts).

---

## 11. Baseline Plan Compatibility

The Ops Advisor Engine is designed to run on the current InsightPulse AI
baseline plans without requiring Enterprise tier upgrades:

| Platform | Required plan | Notes |
|----------|--------------|-------|
| Supabase | Team | Vault, Edge Functions, pgvector available |
| Vercel | Pro | Observability + Analytics API available |
| DigitalOcean | Pay-as-you-go | Monitoring API available on all plans |
| GitHub | Free / Team | WAF guidance applies; secret scanning on public repos free; GHAS optional |

GitHub Advanced Security (GHAS) features (advanced secret scanning, code scanning)
are noted in findings as `info` severity when not available, with a note that they
are available on GitHub Enterprise or via 3rd-party tools.

---

## 12. File Locations (SSOT)

| Artifact | Path |
|----------|------|
| Migration | `supabase/migrations/20260301000010_ops_advisor.sql` |
| Contract doc | `docs/architecture/OPS_ADVISOR_CONTRACT.md` (this file) |
| Rulepacks | `ssot/advisor/rulepacks/*.yaml` |
| Workbooks | `ssot/advisor/workbooks/*.yaml` |
| Scan adapter API routes | `apps/ops-console/app/api/advisor/scan/[provider]/route.ts` |
| Rulepack schema definition | `ssot/advisor/schema/rulepack.v1.yaml` _(planned)_ |
| Workbook schema definition | `ssot/advisor/schema/workbook.v1.yaml` _(planned)_ |
| Rulepack CI validator | `scripts/ci/validate_advisor_rulepacks.py` _(planned)_ |

---

*This document is the authoritative contract for the Ops Advisor Engine.*
*Changes to table schemas, rulepack formats, or adapter contracts must update this doc.*
