# IPAI Tenancy Model

> **Authoritative decision record** for how InsightPulseAI serves multiple tenants
> (IPAI itself, W9 Studio, OMC, TBWA\SMP, and future clients) from a **single local
> Odoo 18 database**.
>
> **SSOT index:** [ssot/tenants/tenants-registry.yaml](../../ssot/tenants/tenants-registry.yaml)
> **Last updated:** 2026-04-14

---

## Decision

**Single database, multi-company Odoo 18.** All tenants live in `odoo_dev`
(dev) / `odoo_staging` (staging) / `odoo` (prod) as separate `res.company` rows
with row-level record-rule isolation and per-company user whitelists.

| Dimension | Choice |
|---|---|
| Database per tenant | ❌ Rejected |
| ACA app per tenant | ❌ Rejected |
| Shared DB + shared company | ❌ Rejected |
| **Shared DB + `res.company` per tenant** | ✅ **Adopted** |

---

## Why this model (vs the alternatives)

### Considered and rejected: DB-per-tenant

- **Pros:** Hard data isolation, per-tenant version autonomy, simple backups.
- **Cons:**
  - Operational overhead grows linearly with tenant count (connection pool,
    migrations, backups, schema drift across DBs).
  - Cross-tenant reporting (provider-level dashboards, PH BIR consolidated
    filings across IPAI + W9) becomes a union-query nightmare.
  - Blows the "only local `odoo_dev`" constraint stated in this engagement.
  - OCA module upgrades have to be orchestrated N times.
- **Verdict:** Rejected at current scale (4 tenants, 1 provider). Re-evaluate
  if a single client requires data-residency in a different region or if
  a tenant exceeds ~20 % of total DB size.

### Considered and rejected: ACA-app-per-tenant

- **Pros:** Blast-radius isolation, independent scaling.
- **Cons:** Same DB-count problem + ACA env sprawl. Memory `project_azure_integration_doctrine.md`
  and `azure_rg_normalization.md` already standardize on one shared runtime env.
- **Verdict:** Rejected.

### Considered and rejected: Single shared company

- **Pros:** Simplest operationally.
- **Cons:** No data isolation — a W9 bookkeeper could read a TBWA\SMP invoice.
  Unacceptable once there's any external client.
- **Verdict:** Rejected.

### Adopted: Shared DB + `res.company` per tenant

- **Pros:**
  - Native Odoo multi-company is battle-tested; ACLs via record rules are first-class.
  - Cross-tenant provider reports work out of the box (`env.companies` whitelist).
  - Single migration/upgrade path.
  - Consolidated backups.
  - Matches the "only local `odoo_dev`" constraint.
  - OCA multi-company modules already in the ecosystem
    (`account_financial_report`, `mis-builder` with company filters, etc.).
- **Cons & mitigations:**
  - *Soft* isolation — depends on record-rule correctness.
    → Mitigation: drift-guard test asserts every model with `company_id` has
    a deny-by-default company-filter rule. Per-tenant audit each quarter.
  - Shared storage → a DB-level breach exposes all tenants.
    → Mitigation: PostgreSQL RLS on sensitive tables, pg_hba.conf restrictions,
    daily encrypted backup, Azure Key Vault for credential rotation.
  - Noisy-neighbor risk.
    → Mitigation: monitor slow-query log; partition heavy clients if they
    approach 20 % of DB workload.

---

## Reference architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 One Odoo 18 CE instance                      │
│                  (odoo_dev / staging / prod)                 │
│                                                              │
│  ┌───────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │ res.company 1 │ │res.company 2 │ │ res.company 3..N   │   │
│  │ InsightPulseAI│ │  W9 Studio   │ │ OMC, TBWA\SMP,...  │   │
│  │ role: provider│ │role: venture │ │ role: client       │   │
│  │ visibility:   │ │ visibility:  │ │ visibility:        │   │
│  │   global      │ │   scoped     │ │   scoped_strict    │   │
│  └───────┬───────┘ └──────┬───────┘ └──────────┬─────────┘   │
│          │                │                    │             │
│          │  record rules (ir.rule)             │             │
│          ▼                ▼                    ▼             │
│  ┌────────────────────────────────────────────────────┐      │
│  │ Shared tables (res.partner, account.move, ...)     │      │
│  │ Every row has company_id → strictly filtered       │      │
│  └────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
           ▲                                     ▲
           │                                     │
   ┌───────┴────────┐                   ┌────────┴─────────┐
   │ Portal users   │                   │ Provider admins  │
   │ company_ids:   │                   │ company_ids:     │
   │ [own company]  │                   │ [ALL companies]  │
   └────────────────┘                   └──────────────────┘
```

---

## Data-isolation contract

### 1. Every tenant-owned model MUST define `company_id`

Record rule template (generated per-model):

```xml
<record id="rule_<model>_company_filter" model="ir.rule">
  <field name="name">&lt;Model&gt; — multi-company</field>
  <field name="model_id" ref="model_<model>"/>
  <field name="global" eval="True"/>
  <field name="domain_force">
    [('company_id', 'in', company_ids)]
  </field>
</record>
```

### 2. User provisioning contract

| User type | `company_id` | `company_ids` (whitelist) |
|---|---|---|
| IPAI provider admin | 1 (IPAI) | `[1, 2, 3, 4, ...]` — all tenants |
| IPAI operator (non-admin) | 1 | `[1]` only |
| W9 Studio operator | 2 | `[2]` only |
| OMC operator | 3 | `[3]` only |
| TBWA\SMP portal user | 4 | `[4]` only |
| Cross-tenant consultant | {primary} | explicit whitelist, review every 90 days |

### 3. Portal users (`base.group_portal`) are deny-by-default

Any table accessed by a portal user must have an explicit company record rule.
No implicit cross-company leaks.

### 4. Billing data is scoped to `provider + self`

A tenant sees **its own invoices** plus **IPAI's invoices directed at it**.
Never any other tenant's billing.

### 5. Audit log requirement

Enable `audit_log` (OCA) on these models at minimum:
- `res.users`, `res.groups`, `res.company`, `ir.rule`
- `account.move`, `account.move.line`
- Any `ipai_bir_*` filing model
- Client-specific custom models

---

## Tenant onboarding runbook

For every new tenant (IPAI-internal or client):

1. **Add SSOT row** in `ssot/tenants/tenants-registry.yaml` with status `prospect`.
2. **Create identity file** `ssot/tenants/<code>/identity.yaml` from the template
   (copy from `tbwa-smp/identity.yaml`, fill fields).
3. **Create `res.company`** via migration or admin UI; record the assigned
   `company_id` back into both SSOT files.
4. **Provision users** with `company_ids` whitelist matching the tenant.
5. **Validate record rules** with automated smoke test:
   - Log in as the new tenant's user.
   - Assert they CANNOT read any record with `company_id != their_company_id`.
   - Assert they CAN read their own records.
6. **Key Vault scope** — create per-tenant secret prefix if the tenant has
   external integrations (bank feeds, e-filing, SMTP).
7. **Billing setup** — subscription in `sale.subscription` or project-based
   terms in `project.project`.
8. **Flip status** to `active` in the registry; update this doc's changelog.

---

## Open questions (blocks full activation)

These MUST be resolved before onboarding TBWA\SMP or any net-new client:

### Q1. What is OMC's relationship to IPAI?

Three candidates with sharply different implications:

| Scenario | Record-rule policy | Billing |
|---|---|---|
| **Client** (OMC pays IPAI for finance-ops-as-a-service) | Strict deny-by-default | Per-seat or retainer |
| **Sister entity** (OMC and IPAI share ownership) | Relaxed (cross-company reports OK) | Internal (no billing) |
| **Shared finance function** (OMC operators run IPAI's books) | OMC users assigned to IPAI company + their own | Salaries; no billing |

Until answered: OMC sits in the registry with `role: tbd`.

### Q2. Is the "Finance Framework Unified Workbook" an existing system to migrate?

If yes (likely, given 11 named users with standardized codes), we need:
- Export of current chart of accounts, partners, transactions.
- Mapping of user codes (CKVC, RIM, LAS, ...) to Odoo `res.users.login` + `res.partner.ref`.
- Cutover plan with parallel-run period.

### Q3. TBWA\SMP data residency

TBWA is part of Omnicom group, typically M365-heavy and compliance-strict.
- Does their contract permit data in Azure Sponsorship sub (`eba824fb-…`)?
- Or do they require a dedicated pay-as-you-go sub in PH region?

This determines whether TBWA\SMP can fit the single-DB model or triggers
a PH-regional DB-per-tenant exception.

---

## Migration from current state

Today, `odoo_dev` runs with (effectively) one company. The plan:

1. **Snapshot** current DB as `odoo_dev_pre_multicompany_<date>`.
2. **Rename** current company → `InsightPulseAI` (company_id `1`).
3. **Create** `W9 Studio` (company_id `2`).
4. **Import** OMC data once Q1 is resolved.
5. **Stub** TBWA\SMP (company_id `4`) with `active: false` until contract signed.
6. **Deploy** record rules from `addons/ipai/ipai_multicompany_rules/` (new
   module to create — gap).
7. **Validate** with the onboarding smoke test above, per company.

---

## Related

- **Memory:** `project_tenant_map_20260414.md` (pointer to this doc)
- **SSOT:** [`ssot/tenants/tenants-registry.yaml`](../../ssot/tenants/tenants-registry.yaml)
- **CLAUDE.md:** DB constraint "odoo_dev (development), odoo_staging (staging), odoo (production) — only these 3 environments"
- **Benchmarks:** [`docs/benchmarks/d365_finance_copilot_parity_catalog.md`](../benchmarks/d365_finance_copilot_parity_catalog.md)
  — D365 also uses multi-company (`dataareaid`); our model is conceptually
  equivalent with stronger row-level ACLs.

## Changelog

- **2026-04-14** Initial decision recorded. Model: single-DB multi-company.
  SSOT structure created for IPAI, W9 Studio, OMC (pending), TBWA\SMP (stub).
