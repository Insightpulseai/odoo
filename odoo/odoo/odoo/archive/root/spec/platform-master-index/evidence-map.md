# Evidence Map — Platform Master Index

> Maps each epic to its concrete evidence artifacts in the repo.
> "Evidence" means: migration files, edge functions, SSOT entries,
> contract docs, evidence bundles, and shipped commits.
>
> Last audited: 2026-03-01

---

## Infrastructure Evidence

### Supabase Migrations (ops.* schema chain)
| Migration | Purpose | Epic |
|-----------|---------|------|
| `20251219_ops_advisor_schema.sql` | Advisor recommendations, scoring | E4 |
| `20260124000004_ops_multisignal_scoring.sql` | Health windows, alert state, scoring | E4 |
| `20260124000005_ops_routing_matrix_escalation.sql` | Routing + escalation | E4 |
| `20260124100001_ops_config_registry.sql` | Config registry | E1 |
| `20260124120000_marketplace_integrations.sql` | Marketplace schema | E6 |
| `20260124200001_ops_tables_browser.sql` | Schema inspection | E1 |
| `20260124_1000_ops_lakehouse_control_plane.sql` | Lakehouse indexing | E2 |
| `20260125_000001_secret_registry.sql` | Secret registry | E1 |
| `20260125_000002_ops_run_system.sql` | ops.runs + run_events + artifacts | E1 |

### Supabase Edge Functions
| Function | Purpose | Epic |
|----------|---------|------|
| `ops-advisory-scan` | Advisor scan runtime | E4 |
| `copilot-chat` | M365 copilot broker | E5 |
| `ipai-copilot` | IPAI copilot | E5 |
| `plane-sync` | Plane GitHub sync | E6 |
| `marketplace-webhook` | Marketplace events | E6 |
| `docs-ai-ask` | RAG endpoint | E2 |
| `context-resolve` | Context resolution | E2 |
| `embed-chunk-worker` | Embedding worker | E2 |
| `memory-ingest` | Memory ingestion | E2 |
| `llm-webhook-ingest` | LLM observability | E1 |
| `bir-urgent-alert` | BIR urgent alerts (O365) | E5 |

### SSOT Entries
| File | Purpose | Epic |
|------|---------|------|
| `docs/architecture/SSOT_BOUNDARIES.md` | 14 boundary sections | E1 |
| `docs/architecture/PLATFORM_REPO_TREE.md` | Surface area allowlist | E1 |
| `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | 17 contracts (9 active) | E1 |
| `ssot/bridges/catalog.yaml` | 8 integration bridges | E3 |
| `ssot/secrets/registry.yaml` | Secret identifiers + consumers | E1 |
| `ssot/integrations/n8n_devops_templates.yaml` | n8n DevOps templates | E1 |

### Platform Components
| File | Purpose | Epic |
|------|---------|------|
| `platform/advisor/scorer.ts` | Advisor scoring engine | E4 |
| `platform/vercel-integrations/github_issues.ts` | Vercel-GitHub integration | E7 |
| `web/do-advisor-agent/` | DO advisor agent | E9 |
| `web/do-advisor-ui/` | DO advisor UI console | E9 |

---

## Shipped Evidence Bundles

### docs/evidence/20260212-1730/ops-backend/SHIPPED.md
- **Status**: COMPLETE
- **Commit**: d2e2d75a
- **Deliverables**: 10 tables, 12+ RPC functions, 3 Edge Functions, RLS policies
- **Covers**: E1 (ops ledger), E2 (SoW primitives)

### docs/evidence/20260212-1830/phase4-ops-ui-rpcs/SHIPPED.md
- **Status**: COMPLETE
- **Commit**: a766951e
- **Deliverables**: SuperClaude→Pulser bridge + ops UI RPC migrations
- **Covers**: E1 (ops ledger)

### docs/evidence/20260212-2045/o365-integration/IMPLEMENTATION.md
- **Status**: COMPLETE
- **Deliverables**: ipai_bir_notifications (12 files, ~1400 lines) + bir-urgent-alert Edge Function
- **Covers**: E5 (M365 interaction plane)

### docs/evidence/20260212-2045/plane-integration/IMPLEMENTATION.md
- **Status**: COMPLETE
- **Deliverables**: ipai_bir_plane_sync (10 files, ~1300 lines) + SQL bootstrap
- **Covers**: E6 (Plane marketplace)

---

## Gaps (no evidence found)

| Task | What's missing | Impact |
|------|---------------|--------|
| T4.4 | Vercel deployment health scan | No observability on deploy failures |
| T5.3 | M365 identity mapping | No auth hardening for M365 plane |
| T6.4 | Sentry → Plane intake | No automated incident routing |
| T6.5 | Plane project UUID fill | Sync is a no-op without UUIDs |
| T7.3 | Vercel cron-as-code | Crons lost on redeploy |
| T8.2 | GitHub auth reliability | All PR automation blocked |
| T9.1 | DO snapshot retention | Cost accumulates |
| T9.2 | OCR droplet remediation | Unresolved alerts |

---

## Advisor Scorer TODO (platform/advisor/scorer.ts:127)

```
// TODO: Route to sources/vercel.ts, sources/supabase.ts, sources/digitalocean.ts
// based on rule.source. Return null if rule passes, Finding if it fails.
```

This TODO blocks T4.3 (advisor scan routes) and T4.4 (Vercel health scan)
from producing real findings. The scorer exists but source adapters
for Vercel, Supabase, and DigitalOcean are stubs.
