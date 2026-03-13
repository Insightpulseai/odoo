# Odoo / n8n / Supabase Integration Consolidation

Consolidate all Odoo ↔ n8n ↔ Supabase integration surfaces, decide the canonical architecture, and test all live connections end to end.

## Context

- Odoo is the ERP / System of Record.
- n8n is self-hosted.
- Supabase is self-hosted.
- Current target state is Azure-native for runtime and infra decisions.
- No manual UI instructions.
- No secrets in git.
- Prefer repo-first, CLI/API-driven implementation.
- Keep outputs machine-readable and evidence-backed.

## Important architectural rule

Do not assume n8n is the only integration path.
You must evaluate and classify each data flow into one of these categories:

1. **Workflow automation**
   - event-driven orchestration
   - approvals
   - notifications
   - business process glue
   - webhook/API mediation
   - low-volume CRUD
   - => preferred engine: **n8n**

2. **Data replication / ETL**
   - bulk sync
   - recurring extraction/loading
   - table-level movement
   - denormalized serving layers
   - repeatable warehouse loads
   - => preferred engine: **Supabase ETL** or another canonical ETL path if justified

3. **Direct application integration**
   - Odoo native API calls
   - thin service/bridge behavior
   - => only if explicitly justified and documented

## Goal

Produce one canonical Odoo/n8n/Supabase integration model, remove duplication, and test every active connection path.

---

## Phase 1 — Inventory

Scan the repo(s) and runtime config for all references to:
- Odoo XML-RPC / JSON-RPC / API integrations
- n8n webhooks, credentials, workflow exports, workflow IDs
- Supabase API URLs, PostgREST endpoints, direct Postgres connections, schema/table targets
- Supabase ETL references, jobs, configs, scripts, schedules, docs
- env vars, Docker Compose files, secrets placeholders, CI variables, specs, docs, runbooks

Build an inventory of every integration path and classify each as:
- canonical
- duplicate
- stale
- deprecated
- broken
- unknown owner

Also classify each path by engine:
- n8n workflow
- Supabase ETL
- direct API
- direct DB
- custom bridge/script

## Phase 2 — Canonical architecture decision

For every current or historical flow, decide the canonical owner:

A. Odoo → n8n
B. n8n → Odoo
C. n8n → Supabase
D. Supabase → n8n
E. Odoo → Supabase
F. Supabase ETL jobs

Rules:
- Use n8n for workflow orchestration and app-to-app automation.
- Use Supabase ETL for repeatable data movement/replication when it is a better fit than workflow automation.
- Prefer built-in n8n Odoo and Supabase nodes where they are sufficient.
- If the node cannot support a required operation, use HTTP Request and document why.
- Avoid direct Odoo ↔ Supabase writes unless explicitly justified.
- Eliminate duplicate mechanisms doing the same job through different stacks.

Required architectural outputs:
- one canonical direction/owner per integration flow
- one auth model per hop
- one endpoint/credential naming convention
- one policy for when to use n8n vs Supabase ETL

## Phase 3 — Implement consolidation

Apply minimal repo/config/doc changes to:
- remove stale endpoint/config references
- standardize env var names
- standardize credential naming
- update docs/specs/SSOT
- remove duplicate or deprecated integration paths
- clearly mark deferred/legacy paths
- add machine-readable integration SSOT artifacts

Create or update a machine-readable file such as:
- `ssot/integrations/odoo-n8n-supabase.yaml`

It must include for each connection:
- source
- destination
- engine (n8n / Supabase ETL / direct)
- protocol
- auth model
- canonical status
- test status
- owner repo/path

## Phase 4 — Connection tests

Build and run a deterministic connection test suite for:

### A. Odoo
- auth works
- low-risk model read works
- safe write/readback test if allowed
- API base URL/version/path validated

### B. n8n
- self-hosted base URL reachable
- webhook endpoints reachable
- required credentials present
- representative workflow test path executes safely

### C. Supabase
- self-hosted base URL reachable
- intended schema(s)/table(s) reachable
- CRUD smoke on safe sandbox/test table
- PostgREST/API/DB path validated as applicable

### D. Supabase ETL
- ETL config/job exists if intended
- source/target connectivity validated
- safe dry-run or smoke execution if supported
- output destination validated

### E. End-to-end

Validate at least one full canonical chain, for example:
- Odoo event/data → n8n → Supabase
- Odoo source → Supabase ETL → Supabase target
- Odoo → n8n → external side effect + Supabase state update

depending on the chosen canonical model.

Also validate:
- retry/error behavior
- idempotency / duplicate-run safety
- no secrets leakage in logs

## Phase 5 — Final outputs

Produce exactly:
1. Executive summary
2. Current integration inventory
3. Canonical architecture decision
4. n8n vs Supabase ETL decision matrix
5. Changes applied
6. Connection test matrix
7. Failures/blockers
8. Remaining follow-ups
9. Machine-readable artifact paths

### Decision matrix requirements

Include a table that explains when to use:
- n8n
- Supabase ETL
- direct Odoo API integration

Example columns:
- use case
- preferred engine
- rationale
- current implementation
- required migration action

## Constraints

- No manual UI guidance
- No secrets committed
- No fake "complete" claims
- Keep changes incremental and reviewable
- Prefer one canonical path over multiple overlapping ones
- Treat self-hosted Supabase and self-hosted n8n as first-class platform surfaces

## Success criteria

- one canonical Odoo/n8n/Supabase architecture
- explicit decision on which flows belong to n8n vs Supabase ETL
- every active connection tested
- duplicate/stale paths removed or deprecated
- machine-readable SSOT updated
- evidence captured
- final status clearly labeled:
  - complete
  - complete with deferred items
  - blocked
