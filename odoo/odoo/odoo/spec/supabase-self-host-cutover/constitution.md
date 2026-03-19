# Constitution: Supabase Cloud-to-Self-Hosted Migration

> Non-negotiable rules governing every phase of this migration.
> No task, script, or agent action may violate these constraints.

---

## C-001: Cloud Is Truth Until Cutover

The managed Supabase project `spdtwktxdalcfigzeqrz` remains the **single source of truth** for all consumers until the final cutover gate (Phase 5) passes. No consumer may be pointed at the self-hosted instance until its phase gate is green.

## C-002: Idempotent and Resumable

Every migration script must be idempotent. Re-running any step must produce the same end state without duplication, corruption, or side effects. Partial failures must be resumable from the last successful checkpoint.

## C-003: No Manual Steps

Every action is scripted and version-controlled under `scripts/supabase-migrate/`. No SSH-and-type workflows. No "run this SQL in Studio". If it cannot be scripted, it cannot ship.

## C-004: Dry-Run Mode Required

Every destructive operation (schema drop, data import, DNS switch, consumer rewire) must support a `--dry-run` flag that logs intended actions without executing them. Dry-run output is saved to `docs/evidence/`.

## C-005: Verification Gates Before Phase Advance

Each phase (2 through 5) defines explicit verification gates. The next phase cannot begin until all gates of the current phase emit `PASS`. Gate results are machine-readable JSON stored in `docs/evidence/<timestamp>/supabase-migrate/`.

## C-006: Rollback Path Per Phase

Every phase documents a rollback procedure that restores the prior state. Rollback scripts live alongside forward scripts. Rollback is tested in dry-run before the forward operation executes.

## C-007: Secrets Never Leave Key Vault

No secret is hardcoded, logged, echoed, or stored in files. Scripts pull secrets at runtime:

```bash
az keyvault secret show --vault-name kv-ipai-dev --name <secret-name> --query value -o tsv
```

Connection strings are assembled in-memory from vault-fetched components. `.env` files for Docker Compose reference vault-backed values injected by deployment scripts.

## C-008: Evidence Artifacts for Every Phase

Every phase emits structured evidence to `docs/evidence/<YYYYMMDD-HHMM>/supabase-migrate/`:

| Artifact | Format | Purpose |
|----------|--------|---------|
| `schema-parity.json` | JSON | Extension, table, RLS comparison |
| `row-counts.json` | JSON | Per-table row counts, cloud vs self-hosted |
| `function-health.json` | JSON | Per-function endpoint status |
| `consumer-smoke.json` | JSON | Per-consumer connectivity result |
| `gate-result.json` | JSON | Phase gate pass/fail with reasons |
| `*.log` | Text | Raw command output |

## C-009: Edge Functions Deploy from Repo

Edge Functions are deployed from `supabase/supabase/functions/` in this repository, never exported from the cloud project. The repo is the source of truth for function code. Cloud is only the source of truth for data and runtime schema state.

## C-010: Consumer Rewire Uses Declared Manifest

Consumer rewiring follows `config/supabase-consumers.yaml` (to be created in T-016). No ad-hoc rewiring. The manifest declares every consumer, its current endpoint, its target endpoint, and its smoke test command. Rewiring is executed in manifest order.

---

## Scope Boundaries

**In scope**: Schema, data, Edge Functions, RLS policies, extensions, storage buckets, consumer bindings, DNS, monitoring.

**Out of scope**: Supabase Auth provider configuration changes (GoTrue config is already deployed in Phase 1), Supabase Studio customizations (disposable), billing/account matters.

---

## Violation Protocol

If any constitution rule is violated during execution:

1. Halt the current phase immediately
2. Log the violation to `docs/evidence/` with full context
3. Do not proceed until the violation is resolved and the phase gate is re-run

---

*Spec bundle: supabase-self-host-cutover | Created: 2026-03-14*
