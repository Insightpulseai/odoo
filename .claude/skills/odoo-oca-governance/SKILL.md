---
name: OCA Module Governance
description: Verify OCA module adoption quality gates — maturity level, 19.0 CI status, test install, no EE deps, manifest registration
---

# OCA Module Governance Skill

## When to use
When adding, updating, or reviewing any OCA module in `addons/oca/`.

## Quality gates checklist

Before adding any OCA module to the install baseline:

1. Verify 19.0 branch exists and CI is green on the OCA repo
2. Check `development_status` >= `Stable` in `__manifest__.py`
3. Test install in disposable DB: `test_<module>`
4. Verify no conflicts with existing `ipai_*` modules
5. Document in `config/addons.manifest.yaml` with repo, tier, and provenance
6. Confirm no Enterprise dependencies or odoo.com IAP calls

## Porting workflow (18.0 → 19.0)

```bash
oca-port origin/18.0 origin/19.0 <module> --verbose --dry-run
odoo-bin upgrade_code --addons-path <path>
odoo-bin -d test_<module> -i <module> --stop-after-init --test-enable
```

Never port without running `upgrade_code`. Odoo 18 changed `tree` to `list` globally.

## Hard rules

- Never modify OCA source — create `ipai_*` override module
- Never copy OCA files into `addons/ipai/` — use `_inherit`
- Stable modules cannot depend on Beta modules
- Never skip test install
- OCA path is always `addons/oca/` (slash, never hyphen)
