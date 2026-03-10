# Plan — Platform Master Index

## Milestone Map

### M0 — Governance SSOT + Foundational SoW
**Dependency**: None (foundation for everything)
**Evidence**:
- docs/architecture/SSOT_BOUNDARIES.md (14 boundary sections)
- docs/architecture/PLATFORM_REPO_TREE.md (surface area allowlist)
- supabase/migrations/20260125_000002_ops_run_system.sql (ops.runs + ops.run_events)
- supabase/migrations/20260124000004_ops_multisignal_scoring.sql (health windows)
- docs/contracts/PLATFORM_CONTRACTS_INDEX.md (17 contracts, 9 active)

### M1 — Advisor Runtime + DB Primitives
**Depends on**: M0
**Evidence**:
- supabase/migrations/20251219_ops_advisor_schema.sql (advisor tables)
- supabase/migrations/20260124000004_ops_multisignal_scoring.sql (scoring)
- supabase/functions/ops-advisory-scan/index.ts (scan runtime)

### M2 — Interaction Planes
**Depends on**: M0, M1
**Evidence**:
- supabase/functions/copilot-chat/index.ts (M365 broker)
- supabase/functions/ipai-copilot/index.ts (IPAI copilot)
- design/tokens/m365_planner.tokens.json (M365 design tokens)
- design/wireframe/m365_planner.shell.json (M365 wireframes)

### M3 — Marketplace Integrations
**Depends on**: M0
**Evidence**:
- supabase/functions/plane-sync/index.ts (Plane sync)
- supabase/functions/marketplace-webhook/index.ts (marketplace events)
- supabase/migrations/20260124120000_marketplace_integrations.sql (schema)

### M4 — Deployment Determinism + Drift Elimination
**Depends on**: M0, M1
**Evidence**:
- vercel.json (root) + apps/ops-console/vercel.json (project config)
- automations/n8n/workflows/vercel-drain-handler.json
- automations/n8n/workflows/deployment-notify.json
- docs/ops/VERCEL_PRODUCTION_CHECKLIST_SSOT.md

## Dependency Graph

```
M0 (Governance SSOT + SoW)
├── M1 (Advisor runtime + DB)
│   ├── M2 (Interaction planes: M365, Slack)
│   └── M4 (Deployment determinism)
└── M3 (Marketplace: Plane, Sentry)
```

## Critical Path
M0 → M1 → M4 (deployment determinism blocks production confidence)
M0 → M3 (Plane integration independent of advisor)
