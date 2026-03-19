# Constitution: ops-automation-sweep

**Spec**: ops-automation-sweep
**Version**: 1.0.0
**Status**: ACTIVE

---

## Purpose

Govern the behavior of all agents, scripts, and CI jobs that discover, validate, and deploy n8n workflow automations and related operational surfaces across the `Insightpulseai/odoo` monorepo.

---

## Non-Negotiables

### Execution Model
1. **No UI steps.** All operations are repo-first, CLI-driven, or API-driven. No n8n UI interactions during sweep or deploy phases.
2. **Read-only audit phase MUST run before any deploy phase.** No deploy executes without a prior audit artifact (`inventory.json`).
3. **All n8n deploys must be idempotent and diff-based.** No blind overwrite of existing workflows. Before updating, fetch the current workflow from n8n API, compute diff, deploy only if diff is non-empty.
4. **Any destructive action requires explicit `--apply` flag.** Without `--apply`, all operations are dry-run. With `--apply`, a report artifact must be produced before and after.

### Safety
5. **No secrets in repo.** All tokens (`N8N_API_KEY`, `N8N_MCP_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`) must come from environment variables, never committed to files.
6. **Fail loudly.** Any phase that cannot complete due to missing env vars, unreachable API, or invalid JSON must exit non-zero with a clear error message referencing the failing artifact path.
7. **Audit-only in CI.** CI jobs triggered by PR must never run with `--apply`. Apply is human-initiated only.

### Scope
8. **Canonical location is authoritative.** `automations/n8n/` is the SSOT for workflow JSONs. Stray workflows outside this path must be flagged and (with `--apply`) moved, not silently deployed from non-canonical paths.
9. **Deprecated references must be flagged, never silently ignored.** Any reference to old domains (`.net`), old paths (`n8n/`, `mcp/` root moves), or deprecated endpoints must appear in the report.
10. **Scope is repo-wide.** No directory is excluded except `.git/`, `node_modules/`, `__pycache__/`, `.cache/`.

### Output
11. **All artifacts land under `out/automation_sweep/`.** Never overwrite the previous run's artifacts without archiving (timestamped copy).
12. **Exit codes are CI-friendly.** `0` = success/no issues. `1` = errors found. `2` = deploy failures (with `--apply`).

---

## Roles and Ownership

| Role | Responsibility |
|------|----------------|
| Sweep script (`sweep_repo.py`) | Discovery, classification, report generation |
| Deploy script (`deploy_n8n_all.py`) | Idempotent deployment of canonical workflows |
| CI job (`automation-sweep.yml`) | Audit-only gate on PR, artifact upload |
| Human operator | Review backlog, run `--apply`, approve PRs |

---

## Conflict Resolution

If a workflow exists in both `automations/n8n/` and `n8n/workflows/`:
1. Compare by SHA256 hash → identical: mark canonical as authoritative, flag stray for removal.
2. Different content: flag as CONFLICT, do not auto-resolve, require human decision.

---

## Related Specs

- `spec/agent/constitution.md` — top-level agent contract
- `infra/dns/subdomain-registry.yaml` — canonical DNS SSOT
- `docs/agent_instructions/SSOT.md` — evidence path contract
