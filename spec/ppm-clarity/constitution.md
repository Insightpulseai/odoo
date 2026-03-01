# Constitution — PPM Clarity (Notion Replacement)

## Purpose
Replace Notion as IPAI's PPM + knowledge-base platform.
Implement portfolio register, rollups, search, and weekly reports
natively in Supabase + Ops Console — no external dependency.

## Principles
1. **Repo is SSOT**: Portfolio register lives in `ssot/ppm/portfolio.yaml`
2. **Evidence by construction**: Every initiative has a spec slug + tracking ref
3. **Automated rollups**: Status derives from ops data, not manual updates
4. **Search-first**: All docs, specs, ops events are findable in one interface
5. **No Notion**: Zero dependency on notion.so APIs or client libraries

## Non-negotiable constraints
- Portfolio truth: `ssot/ppm/portfolio.yaml` drives the portfolio list
- Blockers roll up automatically from `ops.convergence_findings` + `ops.agent_errors`
- Weekly report generated automatically as `ops.artifacts(kind=ppm_report)`
- Search covers spec slugs, failure modes, run_ids, PR numbers via FTS
