# Canonical Monorepo Layout — Platform Composition Policies

> **This document supplements `docs/architecture/MONOREPO_CONTRACT.md`** (full directory structure + CI invariants).
> It adds platform-specific boundary rules for Vercel, Superset, DigitalOcean Postgres, and OCA addons discovery.
> **Do not edit MONOREPO_CONTRACT.md** to add these rules — this file is the canonical home for platform-composition policy.

**Status:** Canonical | **Last updated:** 2026-02-23 | **Owner:** Architecture Team

---

## Cross-References

| Document | Purpose |
|----------|---------|
| `docs/architecture/MONOREPO_CONTRACT.md` | Full directory structure, CI invariants, data flow rules |
| `docs/architecture/SSOT_BOUNDARIES.md` | Cross-domain SSOT rules (auth, mail, DNS, secrets) |
| `docs/architecture/CONNECTION_MATRIX.md` | DB and service connection type reference (pooler vs direct) |
| `docs/policies/SSOT_DATABASE_POLICY.md` | Postgres/MySQL/SQLite SSOT policy |
| `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | Machine-enforced cross-domain contracts |
| `.github/policies/README.md` | CI guard index (all active machine-checkable policies) |

---

## 1. OCA Addons Discovery Policy

```
addons/oca/
├── repos/        ← git submodules ONLY — NEVER in addons_path
└── selected/     ← symlink allowlist — the ONLY OCA path in addons_path
```

**Rules:**
- `addons/oca/repos/*` is **never** added to Odoo `addons_path`. It contains submodule checkouts used to build the symlink allowlist.
- `addons/oca/selected/` contains only symlinks pointing into `repos/`. This is the **only** OCA path that goes in `addons_path`.
- Adding a new OCA module = add a symlink to `selected/`, commit it, update `odoo.conf`.
- Removing a module = remove the symlink from `selected/`, update `odoo.conf`.

**CI Enforcement:** `scripts/ci/check_odoo_addons_path.sh` → workflow `odoo-addons-path-guard.yml`

---

## 2. Vercel Monorepo Policy

**Rule: one Vercel Project per deployable app folder.**

```
web/
├── ops-console/        → Vercel Project: ipai-ops-console    (rootDirectory: web/ops-console)
├── ai-control-plane/   → Vercel Project: ipai-control-plane  (rootDirectory: web/ai-control-plane)
└── shared-ui/          → NOT a Vercel Project (workspace package only)
```

**Requirements:**
- Each deployable app under `web/*` (or `apps/*`) maps to a **separate** Vercel Project.
- Each Vercel Project **MUST** set `rootDirectory` to the app folder. A root-level `vercel.json` that serves multiple apps is prohibited.
- Shared packages (`web/shared-ui`, `supabase/packages`) are workspace dependencies only — never deployed as standalone projects.
- Environment variables are **per-project** — no cross-app env var sharing via Vercel.

**Why:** Avoids env var leakage between apps, prevents build configuration drift, ensures atomic deployments.

---

## 3. Superset Policy

### Metadata DB

| Setting | Required Value | Rationale |
|---------|---------------|-----------|
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL only | SQLite loses data on container restart; not multi-replica safe |
| SQLite | ❌ Prohibited | See `docs/policies/SSOT_DATABASE_POLICY.md` |

### Datasource Connections

| Connection Type | When | Notes |
|----------------|------|-------|
| **Transaction Pooler** | BI/read-only workloads | IPv4-safe; preferred for Superset on DO |
| **Direct** | Long-lived IPv6-capable services | Supabase Direct is IPv6-first |

See `docs/architecture/CONNECTION_MATRIX.md` for full connection decision guide.

---

## 4. DigitalOcean Managed PostgreSQL Policy

**Rule: Network Access must be allowlisted — "open to all inbound" is prohibited in production.**

| Access | Policy |
|--------|--------|
| DO droplet (same VPC) | ✅ Allowlisted by default |
| GitHub Actions CI runners | ✅ Allowlist explicitly if needed for migrations |
| External / public internet | ❌ Prohibited |
| SSL | Required for all connections |

**Why:** DO Managed PG clusters default to "open" on creation. This must be locked down immediately after provisioning.

**IaC:** Enforce via Terraform (`infra/digitalocean/terraform/`) — never change via DO dashboard without a matching commit.

---

## 5. CI Enforcement Summary

| Guard | Script | Workflow | Enforces |
|-------|--------|----------|---------|
| OCA addons-path | `scripts/ci/check_odoo_addons_path.sh` | `odoo-addons-path-guard.yml` | `addons/oca/repos` never in addons_path |
| Supabase contract | `scripts/ci/check_supabase_contract.sh` | `supabase-contract-guard.yml` | `supabase/migrations/` + `supabase/functions/` exist; no stray SQL |
| Design tokens SSOT | `scripts/ci/validate_tokens.py` | `tokens-validate.yml` | `tokens.json` validates against schema |
| DevContainer mounts | `scripts/ci/check_addons_path_invariants.sh` | (inline) | No `/mnt/extra-addons` in devcontainer |

See `.github/policies/README.md` for the full active guard index.
