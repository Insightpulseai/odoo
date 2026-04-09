# Module Decision Rubric

> Before writing custom code, walk through these five tiers in order.
> Stop at the first tier that satisfies the requirement.

## Decision Flow

```
Requirement
  │
  ├─ Tier 1: Standard Odoo admin/config?  ──→ Use it. Done.
  │
  ├─ Tier 2: Official Odoo extension surface?  ──→ Use it. Done.
  │
  ├─ Tier 3: OCA module exists?  ──→ Use OCA. Done.
  │
  ├─ Tier 4: Genuine gap, org-specific need?  ──→ Build ipai_*. Done.
  │
  └─ Tier 5: None of the above apply?  ──→ Reject as unnecessary.
```

---

## Tier 1 — Standard Odoo Admin/Config

Use when the feature is mostly setup, configuration, or documented application behavior.

**Examples:**
- Database management (init, dump, restore, duplicate)
- User/company/multi-company setup
- Payment provider configuration
- Philippines localization (l10n_ph)
- Website domains, CDN, SEO, analytics
- Email server configuration
- Live chat and chatbot setup
- POS hardware and payment terminals
- Cloud storage (Azure attachment storage)
- Scheduled actions / cron jobs via UI

**Check:** Does the [Odoo 18 Administration docs](https://www.odoo.com/documentation/19.0/administration.html) or application docs already cover it?

---

## Tier 2 — Official Odoo Extension Surface

Use when the need requires code but is supported through standard Odoo development patterns.

**Includes:**
- ORM models, fields, constraints, computed fields
- Standard view inheritance (XML)
- Actions, server actions, automated actions
- Reports (QWeb)
- Security: access rights, record rules, field access
- Owl components, JS modules, services, hooks
- Official APIs: JSON-RPC, XML-RPC, Extract API
- CLI: `odoo-bin scaffold`, module install/upgrade
- Data files, demo data, cron definitions
- Standard module `_inherit` / `_inherits`

**Check:** Can you implement this using only documented Odoo 18 developer reference patterns?

---

## Tier 3 — OCA

Use when the feature is not in standard Odoo but is reusable and community-grade.

**When to prefer OCA:**
- The module exists in an OCA repo with 19.0 branch
- It extends core behavior cleanly
- It is not private/org-specific glue
- It has OCA CI (pre-commit, tests passing)

**Current OCA repos in `oca-aggregate.yml`:** 28 repos covering server-tools, web, accounting, HR, sales, purchase, project, DMS, REST, AI, queue, and more.

**Check:** Search [OCA GitHub](https://github.com/OCA) and [OCA Apps](https://odoo-community.org) before building.

**Rules:**
- Never modify OCA source — create an `ipai_*` override module instead
- Pin to 19.0 branch in `oca-aggregate.yml`
- OCA modules are gitignored; fetched at deploy time via `gitaggregate`

---

## Tier 4 — ipai_*

Build custom only when Tiers 1-3 are insufficient and the need is genuinely org-specific.

**Valid reasons:**
- External bridge/integration glue (e.g., `ipai_ocr_gateway`, `ipai_slack_connector`)
- InsightPulseAI-specific workflow policy (e.g., `ipai_finance_ppm`, `ipai_tbwa_finance`)
- Dependency/meta bundles (e.g., `ipai_enterprise_bridge`)
- True gaps not covered by Odoo core or OCA

**Requirements for any ipai_* module:**
- `__manifest__.py` with proper metadata
- Permission model (access rights + record rules)
- Upgrade path (migration scripts if needed)
- Tests (at minimum: install test)
- Naming: `ipai_<domain>_<feature>`
- Located in `addons/ipai/`

**Anti-patterns (do NOT build ipai_* for):**
- Duplicating standard Odoo admin/config
- Reimplementing official Odoo integration points
- Copying OCA module behavior into private code
- Platform/admin concerns that belong in configuration
- Frontend stacks parallel to Owl/standard JS

---

## Tier 5 — Reject / Not Needed

If Odoo already has it AND OCA already has it, do not build a custom duplicate.

**Examples of rejected custom work:**
- Custom payment provider wrapper when Odoo supports the provider natively
- Custom localization when l10n_ph exists
- Custom website/CDN configuration module
- Custom chatbot framework when Odoo live chat exists
- Custom DB lifecycle tooling when `odoo-bin` CLI covers it

---

## Quick Reference

| Question | Answer | Tier |
|---|---|---|
| Is it in Odoo 18 admin/app docs? | Use standard config | 1 |
| Can I build it with standard ORM/views/APIs? | Use official extension | 2 |
| Does OCA have a 19.0 module for it? | Use OCA | 3 |
| Is it org-specific bridge/policy/gap? | Build ipai_* | 4 |
| Already exists in core + OCA? | Reject custom work | 5 |

---

## References

- Odoo 18 Administration: `https://www.odoo.com/documentation/19.0/administration.html`
- Odoo 18 Developer Reference: `https://www.odoo.com/documentation/19.0/developer.html`
- OCA GitHub: `https://github.com/OCA`
- OCA Apps: `https://odoo-community.org`
- OCA Must-Have Modules: `https://odoo-community.org/list-of-must-have-oca-modules`
- Repo aggregate config: `oca-aggregate.yml`
- Module naming convention: `CLAUDE.md` (Module Philosophy section)
