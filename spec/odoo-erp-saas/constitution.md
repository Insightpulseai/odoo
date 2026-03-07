# Constitution — Odoo ERP SaaS

> Non-negotiable rules and constraints for the InsightPulseAI Odoo ERP SaaS platform.

---

## 1. Product Identity

This product is a **governed ERP SaaS platform**, not a marketplace VM image or a control-panel hosting offer. The distinction is structural:

| Characteristic | Marketplace Image | InsightPulseAI ERP SaaS |
|----------------|-------------------|------------------------|
| Provisioning | Manual / semi-auto | Fully automated, deterministic |
| Tenant lifecycle | Not managed | Create, suspend, resume, upgrade, archive, delete |
| Module governance | Unrestricted | Curated packs, OCA-first, policy-enforced |
| Upgrade path | Customer responsibility | Platform-managed, drift-checked, evidence-backed |
| Observability | DIY | Built-in: health, backups, alerts, audit |
| Billing | Infrastructure only | Product-level: plans, entitlements, metered add-ons |

---

## 2. Architecture Boundaries (Never Violate)

### ERP Core = Odoo CE

- Odoo Community Edition is the ERP core. Period.
- No Odoo Enterprise modules. No odoo.com IAP dependencies.
- No forks of Odoo CE — use upstream + addons only.

### Parity Layer = OCA Modules

- OCA modules are the **default** replacement for Enterprise features.
- OCA modules are never modified in-tree. Use `_inherit` overrides in `ipai_*` if needed.
- OCA submodule pins are the version SSOT.

### Bridge Layer = ipai_* Modules

- `ipai_*` modules are **thin bridges** and **meta/glue** only.
- They connect Odoo to external services (Supabase, Azure AI, n8n, SMTP).
- They NEVER replicate OCA parity functionality.
- They NEVER contain core business logic that belongs in Odoo or OCA.

### Control Plane = Supabase

- Supabase manages: tenant registry, plan catalog, module pack catalog, health state, audit log, orchestration state.
- Supabase is NOT a transaction database for Odoo. Odoo uses its own PostgreSQL.
- Supabase secrets are in Vault. Never in source.

### Runtime = Docker + CI/CD

- Odoo runs in deterministic Docker images, not bare-metal installs.
- Images are built via CI, tagged with SHA, promoted through environments.
- No manual server-side changes outside governed pipelines.

---

## 3. Tenant Isolation

- Each tenant gets its own PostgreSQL database.
- Each tenant gets its own filestore path or bucket.
- No shared database multi-tenancy for production plans.
- Tenant secrets are isolated in Supabase Vault per tenant.

---

## 4. Secrets Policy

- Secret values are never committed to any repo.
- Runtime secrets come from Supabase Vault or Azure Key Vault.
- `.env*` files are for local development only and must be in `.gitignore`.
- Operator actions that touch secrets are audit-logged.

---

## 5. Upgrade Governance

- No upgrade proceeds without:
  1. Pre-flight drift check (module versions, schema state)
  2. Verified backup (freshness < 24h)
  3. Module compatibility validation
  4. Post-deploy health check with evidence
- Failed upgrades auto-rollback or hold for operator intervention.
- Evidence packs are stored for every upgrade attempt.

---

## 6. Extension Policy

```
Config → OCA → ipai_* bridge (only if external service integration required)
```

- First: use Odoo built-in configuration.
- Second: use OCA community modules.
- Third: write `ipai_*` only if integrating an external service that has no OCA equivalent.
- Never: write `ipai_*` to replicate functionality available in OCA.

---

## 7. Non-Negotiable Constraints

1. **No EE lock-in**: Never depend on Odoo Enterprise or Odoo.sh services.
2. **No manual ops**: Every operational action must be automatable and reproducible.
3. **No unreviewed addons**: Tenants cannot install arbitrary third-party modules.
4. **No ad hoc SQL**: Schema changes only via migrations or Odoo ORM.
5. **No console-only changes**: Every infrastructure change has a repo commit or audit record.
6. **No shared-DB tenancy in production**: One database per tenant.
7. **Deterministic images**: Docker images are built from locked dependencies, never from `latest`.
