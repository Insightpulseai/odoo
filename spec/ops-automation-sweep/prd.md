# PRD: ops-automation-sweep

**Spec**: ops-automation-sweep
**Version**: 1.0.0
**Status**: ACTIVE

---

## Problem Statement

The monorepo has grown to 28+ n8n workflow JSONs distributed across multiple directories (`automations/n8n/`, `n8n/workflows/`), 7 n8n-related scripts, 4 GitHub Actions, and 11 MCP servers — with no single tool to audit the full automation surface, detect stale references, or deploy idempotently. Operational burden is high; duplication and drift are undetected.

---

## Goals

1. **Repo-wide discovery** of all n8n workflow artifacts and references — canonical and stray.
2. **Identify stale/orphaned automation surfaces** — scripts, cron jobs, GH workflows, duplicate runners.
3. **Produce actionable backlog** (ranked P0/P1/P2) with ROI + risk tags for each opportunity.
4. **Optional apply**: deploy all eligible n8n workflows via GitOps script or n8n API — idempotently, diff-based.
5. **Output artifacts** under `out/automation_sweep/`:
   - `inventory.json` — full structured inventory
   - `report.md` — human-readable summary
   - `backlog.md` — ranked opportunities
   - `patches/*.diff` — suggested moves/fixes

---

## Requirements

### R1: Discovery (Mandatory)
- Scan all n8n workflow JSONs in `automations/n8n/**` and any stray locations.
- Classify each workflow: `canonical | stray | duplicate | stale_reference | unreferenced`.
- Scan all files for n8n references: `.github/workflows/`, `scripts/`, `docs/`, `infra/`, `platform/`, `web/`.
- Include SHA256 hash per workflow JSON for deduplication.

### R2: Staleness Detection (Mandatory)
- Flag references to deprecated domains (`.net`), old paths (`n8n/` root if moved, `mcp/` root), stale endpoints.
- Flag GitHub Actions not referenced by any dispatcher workflow.
- Flag scripts that duplicate CI workflow behavior.
- Flag MCP servers that are configured but have no active consumers in `mcp-servers.json`.

### R3: Opportunity Identification (Mandatory)
- Identify multi-step shell scripts that are candidates for n8n conversion.
- Identify periodic manual checks that could become scheduled n8n workflows.
- Identify Supabase ops events that could drive event-driven n8n triggers.
- Score each opportunity: ROI (High/Medium/Low), Risk (High/Medium/Low), Effort (days).

### R4: Deploy (Optional, `--apply` only)
- Load canonical workflow JSONs from `automations/n8n/`.
- Fetch current workflow from n8n API, compute diff.
- Deploy only if diff is non-empty (idempotent).
- Support `--env {dev,stage,prod}` with environment-specific targeting.
- Emit `report.json` + `report.md` and exit non-zero if deploy fails under `--apply`.

### R5: Output Artifacts (Mandatory)
```
out/automation_sweep/
├── inventory.json       # Full structured inventory (all classifications)
├── report.md            # Human summary with links to files
├── backlog.md           # Ranked opportunities (P0/P1/P2 + tags)
└── patches/
    └── *.diff           # Suggested moves/renames for stray files
```

### R6: CLI (Mandatory)
```
python scripts/automations/sweep_repo.py \
  [--env {dev,stage,prod}] \
  [--out out/automation_sweep] \
  [--apply] \
  [--verbose]
```

### R7: CI Gate (Optional)
- Audit-only job triggered on PRs touching `automations/**`, `scripts/**`, `infra/**`.
- Uploads inventory/report/backlog as artifacts.
- No secrets required for audit-only mode.

---

## Non-Goals

- No automatic merge or rebase of workflow JSON conflicts.
- No n8n credential creation (credentials must exist in n8n before deploy).
- No UI-based verification steps.

---

## Success Criteria

| Criterion | Measure |
|-----------|---------|
| Complete inventory | All 28+ workflow JSONs classified |
| Zero blind deploys | Every deploy preceded by diff check |
| Ranked backlog | ≥5 opportunities with P-tags and ROI scores |
| CI-safe | Exit code 0 when no issues found |
| No secrets in repo | Automated check via `scripts/audit/checks/` |
