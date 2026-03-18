# WorkbenchX — Constitution

## Purpose

Build a **Supabase-native AI Workbench** that delivers the **enterprise outcomes** of Cloudera AI Workbench—governed development, containerized compute sessions, experiments tracking, model/app deployment—while fitting the **control-plane + evidence-first** operating model.

## Principles

1. **Governance-first**: Every run is tied to an authenticated principal; all actions are logged; all artifacts are retained and linkable.
2. **SSOT-first**: Specs + SSOT define what exists; runtime state is derived and audited.
3. **Containerized execution**: All compute happens in isolated sandboxes (Vercel Sandbox / DO runner); no "pet servers" for core workloads.
4. **Data access via policy**: No direct DB credentials in user code; access is mediated via RLS/RPC policies and signed short-lived tokens.
5. **Reproducibility**: Every run is replayable with pinned inputs (code ref, dataset ref, runtime image, params).
6. **Separation of concerns**: UI ≠ runner ≠ data plane ≠ model serving.
7. **Baseline-first**: Prefer Supabase/Vercel/DO primitives; external vendors are optional plugins.

## Non-negotiable constraints

* All internal APIs return JSON (no empty bodies).
* Every job/run produces: `run_id`, event log, and at least one evidence artifact.
* Long-running "apps" must be deployed as managed services with health checks and versioned releases (no ad-hoc daemon processes).
