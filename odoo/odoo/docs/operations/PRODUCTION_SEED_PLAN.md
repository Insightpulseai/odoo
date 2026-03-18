# Production Seed Plan — Odoo

> Single operator/developer document for production database bootstrap.
> SSOT: `ssot/migration/production_seed_plan.yaml`
> Dedup map: `ssot/migration/seed_canonical_map.yaml`

---

## Scope

This plan covers the deterministic bootstrap of an Odoo production database from zero to operational. The same structure applies to `odoo_dev` and `odoo_staging` with environment-specific overrides.

## Database Naming

| Environment | Database Name | Server |
|-------------|--------------|--------|
| dev | `odoo_dev` | `ipai-odoo-dev-pg` |
| staging | `odoo_staging` | `ipai-odoo-staging-pg` |
| prod | `odoo` | `ipai-odoo-prod-pg` |

**Never use `odoo_prod`.**

---

## Phase Order

### Phase 1: Odoo CE Core + OCA Baseline

**What**: Initialize database with Odoo CE base + 56 OCA must-have modules.

```bash
# Inside devcontainer or ACA container
odoo-bin --database=odoo --init=base --stop-after-init
python3 scripts/odoo/install_oca_from_ssot.py --db=odoo
```

**Source of truth**: `config/addons.manifest.yaml`
**Duration**: ~10-15 minutes
**Validation**: Base installed, OCA modules present

### Phase 2: Canonical IPAI Seed Modules

**What**: Install ONLY canonical seed modules. Block deprecated duplicates.

**Canonical modules**:

| Module | Seeds | Status |
|--------|-------|--------|
| `ipai_project_seed` | Project templates | Ready |
| `ipai_zoho_mail` | Zoho SMTP config | Ready |
| `ipai_bir_tax_compliance` | BIR deadlines, tax rates | Ready |
| `ipai_ai_copilot` | Copilot tools, bot partner | Ready |
| `ipai_finance_workflow` | Finance stages (5), projects (2), tasks (20) | **BLOCKED** — `installable=False` |

**Blocked modules** (DO NOT install):

| Module | Reason |
|--------|--------|
| `ipai_finance_close_seed` | Duplicate finance stages/projects/tasks |
| `ipai_mailgun_smtp` | Mailgun is deprecated |

```bash
odoo-bin --database=odoo \
  --init=ipai_project_seed,ipai_zoho_mail,ipai_bir_tax_compliance,ipai_ai_copilot \
  --stop-after-init
```

**Known blocker**: `ipai_finance_workflow` cannot be installed until manifest is updated to `installable=True`.

### Phase 3: Companies, Users, Groups

**What**: Create companies, users, and assign security groups.

```bash
python3 scripts/odoo/seed_prod_users.py --db=odoo
```

**Creates**:
- Company: InsightPulse AI (PH, PHP)
- Company: TBWA\Santiago Mangada Puno
- 4 internal users (CEO, DevOps, Finance Mgr, Project Mgr)
- 1 portal user

**Idempotent**: Uses search-or-create pattern. Safe to re-run.

**Post-action**: Change default passwords (set to `changeme` by script).

### Phase 4: Supabase Control Plane Seeds

**What**: Seed Supabase platform layer (NOT Odoo).

```bash
# Target: Supabase PostgreSQL, not Odoo PG
supabase db seed --db-url=$SUPABASE_DB_URL
```

**Separate concern**: These seeds populate Supabase tables for the control plane, not Odoo business data.

### Phase 5: Validation + Evidence

**What**: Prove the seed result.

```bash
python3 scripts/odoo/validate_seed_state.py \
  --db=odoo \
  --plan=ssot/migration/production_seed_plan.yaml
```

**Checks**:
- All canonical modules installed
- No deprecated modules installed
- Company count matches (2)
- User count and group assignments correct
- Finance stages == 5 (not 6 or 11)
- Month-end tasks == 20 (not 39 or 95)
- BIR tasks: single canonical set (33)
- Mail server: Zoho at sequence=1, no Mailgun
- Non-prod: mail suppression active

**Output**: `docs/evidence/<date>/production-seed-validation.json`

---

## Duplicate Groups (Resolved)

| Group | Canonical Source | Deprecated | Rule |
|-------|-----------------|-----------|------|
| Finance stages | `ipai_finance_workflow` (5 stages) | `ipai_finance_close_seed` (6 stages) | Block deprecated install |
| Finance projects | `ipai_finance_workflow` (2 projects) | `ipai_finance_close_seed` (2 projects) | Block deprecated install |
| Month-end tasks | `ipai_finance_workflow` (20 tasks) | `ipai_finance_close_seed` (75 tasks) | Block deprecated install |
| BIR tasks | `07_tasks_bir_tax.xml` (33 tasks) | `tasks_bir.xml` (27 tasks) | Delete duplicate file |
| Mail server | `ipai_zoho_mail` (Zoho SMTP) | `ipai_mailgun_smtp` + `ipai_enterprise_bridge` | Delete deprecated module |
| Supabase mirrors | `supabase/seeds/` | `ops-platform/supabase/seeds/` | Delete mirror directories |

---

## Environment-Specific Overrides

| Concern | Dev | Staging | Prod |
|---------|-----|---------|------|
| Mail delivery | Suppressed (Mailpit) | Suppressed | Active (Zoho) |
| Demo data | Optional (`odoo_dev_demo`) | No | No |
| Cron jobs | Enabled | Enabled | Enabled |
| Public access PG | Allowed (temporary) | Private endpoint | Private endpoint |
| Backup retention | 7 days | 14 days | 35 days + LTR |

---

## Recovery / Rerun Rules

- All seed scripts are **idempotent** (search-or-create pattern)
- Safe to re-run any phase without duplicating data
- If a phase fails, fix the issue and re-run from that phase (not from scratch)
- To start over: drop + recreate database, then run full sequence

---

## Remaining Gaps

- [ ] `ipai_finance_workflow` must be made installable
- [ ] `tasks_bir.xml` duplicate file must be deleted
- [ ] Chart of accounts: no PH-specific CoA seed yet (relies on OCA `l10n_ph` if available)
- [ ] BIR ATC codes: partially seeded, needs completion
- [ ] Staging sanitization script: not yet built
- [ ] Non-prod mail suppression: config exists but not enforced

---

## One-Sentence Summary

> Run `scripts/odoo/init_production_db.sh` against the SSOT plan, then validate with `scripts/odoo/validate_seed_state.py` and check evidence output.
