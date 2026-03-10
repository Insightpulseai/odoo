# External Agent/Tool Capabilities (Stack Fit)

**Date**: 2026-01-24
**Goal**: Identify where external agentic tools (Jules, TestSprite, etc.) plug into the existing stack:
Odoo (OCA-first) + DigitalOcean + Supabase (system-of-record) + Vercel (optional retention) + n8n (automation fabric).

---

## 1) Jules (Google) — Code-change agent (repo ops)

**What it is**
- A developer agent designed to help with code changes and workflows, with documented interfaces and integrations.
- Integrations include common git hosting surfaces (review docs for your exact host + auth model).

**Best-fit roles in your stack**
- **Spec Kit enforcement assistant**: generate/update spec bundles, plans, tasks, drift checks.
- **Refactor assistant**: mechanical migrations (tree→list for Odoo 18+, view_mode changes, lint passes).
- **Docs agent**: maintain llms-full packs, runtime snapshot drift fixes, runbook refreshes.
- **CI hygiene**: propose fixes from failing pipelines (without bypassing gates).

**Guardrails**
- Must operate via PRs with CI gates; no direct-to-main.
- Output must be deterministic and repo-local: scripts, migrations, workflow YAML.

**Primary references**
- Jules docs: https://jules.google/docs

---

## 2) TestSprite — Autonomous AI test engineer (test generation → diagnosis)

**What it is (capability claims)**
- Positions itself as an autonomous AI test engineer handling testing end-to-end: case generation → execution → issue diagnosis.

**Best-fit roles in your stack**
- **Pre-merge quality gate**: generate regression suites for Odoo customizations, Supabase Edge Functions, and Next/Vercel frontends.
- **API contract regression**: pin OpenAPI + PostgREST behaviors; detect breaking changes early.
- **Agent workflow regression**: validate Pulser/n8n orchestrations using scenario-based tests.

**Guardrails**
- Treat as *quality amplifier*—do not let it "author architecture."
- Store its outputs as evidence artifacts: test plans, failures, repro steps, flake stats.

---

## 3) Stack Alignment (where each tool lands)

| Layer | System-of-record? | Primary tool | Optional tool | Evidence target |
|---|---:|---|---|---|
| Observability plane | Yes | Supabase (ops schema, run_events, artifacts) | Vercel Observability Plus | `docs/evidence/**` + `supabase/migrations/**` |
| Source control workflow | Yes | GitHub PR + CI gates | Jules (PR author) | PR checks + logs |
| Automation fabric | Yes | n8n (self-hosted) | SaaS connectors | workflow JSON exports + runs |
| ERP runtime | Yes | Odoo CE + OCA | none | runtime snapshot + health |
| Test/QA | Evidence-driven | CI test harness + linters | TestSprite | junit/log bundles |

---

## 4) Recommended "Agentic SDLC" loop (your workflow-first stance)

1. **Spec**: Spec Kit bundle + constraints (human-approved).
2. **Change**: Jules proposes PR (code + scripts + docs).
3. **Verify**: CI + TestSprite regression suite.
4. **Deploy**: DO + Vercel + Supabase migrations (idempotent).
5. **Observe**: Supabase ops plane stores run logs + evidence packs.

---

## 5) Integration Patterns

### Jules → GitHub → CI → Supabase

```
Jules (code agent)
    │
    ▼ Opens PR
GitHub PR
    │
    ▼ Triggers
CI Workflows (.github/workflows/)
    │
    ├── Lint/typecheck/test
    ├── Spec validation
    └── Deploy (on merge)
    │
    ▼ Records results
Supabase (observability.jobs)
```

### TestSprite → CI → Supabase

```
TestSprite (test agent)
    │
    ▼ Generates tests
CI Test Harness
    │
    ├── Run tests
    ├── Collect coverage
    └── Record failures
    │
    ▼ Stores artifacts
Supabase (observability.job_events)
    │
    ▼ Triggers on failure
n8n (alert workflow)
```

---

## 6) Evidence Artifacts (where to store outputs)

| Tool | Artifact Type | Storage Location |
|------|--------------|------------------|
| Jules | PR diff, commit SHA | GitHub + `docs/evidence/<date>/jules/` |
| TestSprite | Test plans, failure logs | `docs/evidence/<date>/testsprite/` |
| n8n | Workflow runs, execution logs | Supabase `observability.job_runs` |
| CI | Pipeline logs, test results | GitHub Actions artifacts |
| Odoo | Runtime health snapshots | `docs/evidence/<date>/odoo/` |

---

## 7) Constraints (non-negotiables)

1. **No agent bypasses CI gates** — all changes flow through PR + checks
2. **Supabase is the observability SSOT** — agents write evidence here
3. **n8n orchestrates, doesn't hold state** — stateless thin orchestrator
4. **Deterministic outputs only** — no "creative" architecture from agents
5. **Human approval on spec changes** — agents can propose, not approve
