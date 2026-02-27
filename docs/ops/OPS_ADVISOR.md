# Ops Advisor — Runbook

The Ops Advisor is an **Azure Advisor-like dashboard** built into the ops-console.
It continuously evaluates platform health across five pillars and surfaces actionable findings with severity ratings.

---

## Pillars

| Pillar | Description |
|--------|-------------|
| `cost` | Spending efficiency: bundle size, bandwidth, idle resources |
| `security` | Exposure and compliance: RLS policies, env var hygiene, deployment protection |
| `reliability` | Uptime and resilience: droplet health, deployment frequency, CI gate coverage |
| `operational_excellence` | Process maturity: monitoring, integration drift, schema health |
| `performance` | Speed and responsiveness: LCP targets, error rate thresholds, connection pooling |

---

## Severity Scale

| Level | Weight | Meaning |
|-------|--------|---------|
| `critical` | −25 | Immediate risk (data exposed, service down) |
| `high` | −10 | Significant degradation or exposure |
| `medium` | −5 | Notable gap; address within a sprint |
| `low` | −2 | Minor improvement opportunity |
| `info` | 0 | Informational; no score impact |

Score per pillar = `max(0, 100 − Σ severity_weight)`.

---

## Data Model

```
ops.advisor_runs          ← one row per scan
  └── ops.advisor_findings  ← one row per rule violation (fingerprint-deduplicated)
  └── ops.advisor_scores    ← one row per pillar per run
```

Migration: `supabase/supabase/migrations/20260222000000_ops_advisor.sql`

---

## Running a Scan

### Manual (local)

```bash
# Dry run — prints findings without writing to database
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
  tsx platform/advisor/scorer.ts --dry-run

# Live run — creates ops.advisor_runs record + writes findings + scores
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
  tsx platform/advisor/scorer.ts
```

### Via API

```bash
# Trigger a scan (returns run record immediately; scorer runs async)
curl -X POST /api/advisor/runs \
  -H "Content-Type: application/json"

# Check latest run + scores
curl /api/advisor/runs

# Get all findings for the latest run
curl /api/advisor/findings

# Filter by pillar and severity
curl "/api/advisor/findings?pillar=security&severity=critical"
```

### Via Ops Console UI

Navigate to `/advisor` → click **Run Scan**.
The dashboard polls for completion and refreshes score rings automatically.

---

## Ruleset

Rules live in `platform/advisor/ruleset.yaml`.
Each rule has:

```yaml
- id: my-rule-id
  pillar: security          # cost | security | reliability | operational_excellence | performance
  severity: high            # critical | high | medium | low | info
  title: "Human-readable title"
  description: "What this checks and why it matters."
  remediation: "How to fix it."
  source: vercel            # vercel | digitalocean | supabase (maps to a source module)
  tags: [tag1, tag2]
```

### Adding a Rule

1. Edit `platform/advisor/ruleset.yaml` — add a new entry under the appropriate pillar.
2. Implement evaluation logic in the relevant source (`platform/advisor/sources/vercel.ts`, `digitalocean.ts`, or `supabase.ts`).
3. In `platform/advisor/scorer.ts`, add a case in `evaluateRule(rule, sources)` to call your new source check.
4. Run `tsx platform/advisor/scorer.ts --dry-run` to verify the rule fires correctly.
5. Commit with `feat(advisor): add rule {id}`.

---

## Sources

| Source module | External API | What it checks |
|---------------|-------------|----------------|
| `sources/vercel.ts` | Vercel REST API v9 | Projects, deployments, env vars, build status |
| `sources/digitalocean.ts` | DO API v2 | Droplet status, bandwidth usage |
| `sources/supabase.ts` | Supabase Management API | Project health, branch status, connection stats |

All sources are read-only and use bearer token auth via env vars.

---

## Workbooks

Workbooks are structured checklists for specific release scenarios.
They evaluate a dedicated ruleset subset and present pass/fail status with remediation guidance.

Available workbooks: see `/advisor/workbooks` in the ops-console.

To add a workbook:
1. Create a ruleset YAML in `platform/advisor/rulesets/<name>.yaml`.
2. Add a source module if the workbook checks a new external API.
3. Create the UI route at `apps/ops-console/app/advisor/workbooks/<name>/page.tsx`.
4. Create an API route at `apps/ops-console/app/api/advisor/workbooks/<name>/route.ts`.
5. Add the workbook to the `WORKBOOKS` list in `apps/ops-console/app/advisor/workbooks/page.tsx`.

---

## Score Ring Colors (UI)

| Pillar | Color |
|--------|-------|
| cost | Amber |
| security | Red |
| reliability | Green |
| operational_excellence | Blue |
| performance | Purple |

Rings use recharts `RadialBarChart` — each bar is one pillar, value = score 0–100.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Supabase not configured` (API 503) | Missing `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY` | Set env vars in `.env.local` |
| Score rings show "—" | No complete run in `ops.advisor_runs` | Run a scan |
| Findings page shows 0 findings | Latest run has `status = pending` | Wait for scorer or run manually |
| Rule not firing | Source check returns `null` | Add evaluation logic in `scorer.ts evaluateRule()` |
| Fingerprint collision | Same rule/resource fired twice | Expected — dedup prevents duplicates |

---

## Related

- `platform/advisor/ruleset.yaml` — all rule definitions
- `platform/advisor/scorer.ts` — scan engine
- `supabase/supabase/migrations/20260222000000_ops_advisor.sql` — schema
- `apps/ops-console/app/advisor/` — UI routes
- `apps/ops-console/app/api/advisor/` — API routes
- `docs/ops/MOBILE_RELEASE_READINESS.md` — Mobile workbook runbook
