# PRD — PPM Clarity (Notion Replacement)

## Problem Statement
IPAI uses Notion as its PPM + knowledge base. This creates:
- External dependency (SaaS cost, outage risk)
- Manual status updates (no ops data integration)
- Siloed search (Notion ≠ specs, CI runs, failure modes)

## Goal
Replace Notion's PPM layer with a native IPAI stack:
- Portfolio register in `ssot/ppm/portfolio.yaml` (repo-SSOT)
- Status rollups computed from ops data automatically
- Weekly reports as `ops.artifacts(kind=ppm_report)`
- Unified search across specs, ops events, failure modes

## Functional Requirements

### FR1 — Portfolio Register
- `ssot/ppm/portfolio.yaml` is the single list of initiatives
- Fields: `id`, `name`, `owner`, `status`, `spec_slug`, `github_label`, `start_date`, `target_date`
- `ops.ppm_initiatives` mirrors this YAML (upserted by `ops-ppm-rollup`)

### FR2 — Status Rollups
- `ops.ppm_status_rollups` computed from `ops.convergence_findings` (blocking_findings)
- `merged_prs_30d` computed from `ops.runs` WHERE kind = 'agent' AND status = 'completed'
- Rollup runs on schedule (weekly) and on-demand via Edge Function

### FR3 — Weekly Report
- `ops-ppm-rollup` Edge Function writes `ops.artifacts(kind=ppm_report)`
- Report embedded as Markdown in `metadata.report_md`
- Report available via Ops Console `/tools/ppm`

### FR4 — Unified Search
- `ops-search-query` Edge Function: POST `{query: string}` → results
- Sources: `ops.ppm_initiatives`, `ops.runs`, `ops.convergence_findings`
- Search via PostgreSQL `tsvector` FTS
- Ops Console `/tools/search` exposes this

### FR5 — Ops Console Pages
- `/tools/ppm`: Portfolio table with status badges + blocking count
- `/tools/search`: Free-text search across ops data
- Both pages live under existing `apps/ops-console` app

## Non-Requirements
- **No Notion API**: Zero dependency on notion.so
- **No rich documents**: Markdown in YAML/Supabase is sufficient
- **No AI summarisation**: Plain FTS, no LLM calls in search path
