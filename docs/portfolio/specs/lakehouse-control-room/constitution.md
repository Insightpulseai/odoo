# Constitution — Lakehouse Control Room (No Databricks License)

## Non-Negotiables
1. **No Databricks license dependency**: must run on open-source + commodity cloud primitives.
2. **Supabase is the system-of-record** for runs, run_events, artifacts, and RBAC (RLS enforced).
3. **Deterministic execution**: every run is reproducible; inputs/outputs are versioned and hashed.
4. **No manual UI-only ops**: all deployments and orchestration steps must be automatable via CLI/CI.
5. **GitHub Spec Kit compliance**: work must be anchored to `spec/<slug>/{constitution,prd,plan,tasks}.md`.
6. **Secure-by-default**: secrets never stored in repo; no plaintext credentials in logs/artifacts.
7. **Observability required**: every run emits structured events; health checks and failure classification are mandatory.
8. **Pluggable compute**: executor must support multiple backends (Spark optional; SQL-only path required).
9. **Open table formats**: Delta/Iceberg/Hudi must be supported via open tooling (MVP can pick one, but design must not preclude others).
10. **Odoo-first operationalization**: when Odoo is live, it becomes a primary upstream system; ingestion contracts must be explicit.

## Invariants (Always True)
- Every run has: `run_id`, `phase`, `status`, `input_manifest`, `output_manifest`, `started_at`, `finished_at`.
- Every artifact is immutable and addressable: `sha256`, `content_type`, `byte_size`, `storage_url`.
- Executor is stateless; state lives in Supabase + object storage.
- RLS boundaries: org/project/environment; least privilege enforced.
- Runs MUST reference `git_sha` and `spec_slug` for traceability.

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Run event completeness | 95% | Runs with complete event trails (no missing phases) |
| Enqueue-to-start latency | < 30s | Median time for lightweight phases |
| Deterministic rebuild | 100% | Same inputs + same commit → identical output hashes |
| Odoo ingestion freshness | < 15 min | Data freshness for operational tables (V1) |
| Cap enforcement | 100% | No cap exceeded without termination |

## Constraints

### Technical
- PostgreSQL 15+ (Supabase)
- S3-compatible object storage (MinIO/AWS S3/GCS/Azure Blob)
- Containerized executors (Docker/K8s/DO workers)
- Node.js 20+ for Edge Functions
- Python 3.11+ for data processing
- Delta-rs or Iceberg for table format (MVP chooses one)

### Operational
- Forward-only migrations (no destructive changes)
- Evidence-first deployment (proofs before claims)
- CI gates block non-compliant changes
- Secrets via vault/env; never in artifacts
- Audit trail: all run events persisted
- Signed artifact URLs or private bucket access

## Out of Scope
- Re-creating proprietary Databricks UX pixel-perfect.
- Proprietary Unity Catalog implementation; we provide open catalog equivalents.
- Enterprise-only governance features unless open-source equivalents exist.
- Photon engine (proprietary); use tuning + Trino + Spark AQE instead.

## Governance
- Changes to this constitution require explicit approval
- All significant features require a spec bundle
- Contract changes require migration + compatibility verification
