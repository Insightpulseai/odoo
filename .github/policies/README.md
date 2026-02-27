# CI Policies — Machine-Checkable Contracts

> This directory lists all repository contracts enforced by CI.
> Each policy references the implementing script and workflow.
> **Status:** Canonical | **Last updated:** 2026-02-23

---

## Active Guards

| Policy | Contract Rule | Script | Workflow |
|--------|--------------|--------|----------|
| **Odoo addons_path allowlist** | `addons/oca/repos` MUST NOT appear in addons_path | `scripts/ci/check_odoo_addons_path.sh` | `odoo-addons-path-guard.yml` |
| **OCA module discovery** | Only `addons/oca/selected/` in addons_path | `scripts/ci/check_odoo_addons_path.sh` | `odoo-addons-path-guard.yml` |
| **Supabase directory contract** | `supabase/migrations/` + `supabase/functions/` required | `scripts/ci/check_supabase_contract.sh` | `supabase-contract-guard.yml` |
| **SQL migration placement** | No stray `.sql` outside `supabase/migrations/` or `supabase/seed/` | `scripts/ci/check_supabase_contract.sh` | `supabase-contract-guard.yml` |
| **Design tokens SSOT** | `design/figma/tokens/tokens.json` validates against schema | `scripts/ci/validate_tokens.py` | `tokens-validate.yml` |
| **DevContainer addons mounts** | No `/mnt/extra-addons` in devcontainer config | `scripts/ci/check_addons_path_invariants.sh` | (inline gate) |
| **Spec Kit bundle structure** | New `spec/<slug>/` requires all 4 files | — | `spec-kit-hygiene.yml` |
| **n8n workflow secrets** | No hardcoded secrets in workflow JSON | `scripts/ci/check_n8n_workflow_secrets.sh` | `secret-scan.yml` |
| **Agent instructions drift** | CLAUDE.md/AGENTS.md/GEMINI.md must match SSOT | `scripts/agents/check_agent_instruction_drift.py` | `agent-instructions-drift.yml` |
| **DNS SSOT** | `subdomain-registry.yaml` is the only DNS source | `scripts/dns/generate-dns-artifacts.sh` | `dns-ssot-apply.yml` |

---

## Policy Governance

**Adding a new policy:**
1. Create/update the guard script in `scripts/ci/`
2. Create/update the workflow in `.github/workflows/`
3. Add a row to the table above
4. Register as a contract in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
5. Update `docs/architecture/CANONICAL_MONOREPO_LAYOUT.md` CI Enforcement Summary

**Modifying a policy:**
- Update script + workflow + this table + contracts index atomically in the same PR

**Policy exceptions:**
- Document in the guard script with an `# EXCEPTION: <file> — <reason>` comment
- Exceptions must be reviewed and approved via PR

---

## References

| Document | Purpose |
|----------|---------|
| `docs/architecture/SSOT_BOUNDARIES.md` | Full SSOT boundary rules across all domains |
| `docs/architecture/MONOREPO_CONTRACT.md` | Monorepo structure contract + CI invariants |
| `docs/architecture/CANONICAL_MONOREPO_LAYOUT.md` | Platform-specific boundary rules (Vercel, Superset, DO) |
| `docs/policies/SSOT_DATABASE_POLICY.md` | Database SSOT policy (Postgres/MySQL/SQLite) |
| `docs/architecture/CONNECTION_MATRIX.md` | Connection type reference (pooler vs direct) |
| `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | All cross-domain machine-enforced contracts |
