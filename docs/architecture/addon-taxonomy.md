# Addon Taxonomy

> Classification of Odoo addon types, their source authority, governance rules,
> and filesystem locations. Follows the OCA module governance pattern.

## Taxonomy

| Tier | Prefix/Location | Source Authority | Governance | Example |
|------|----------------|-----------------|------------|---------|
| **Core** | `vendor/odoo/addons/` (local) or `/opt/odoo/addons/` (container) | Odoo SA upstream | Never modify. Read-only mirror. | `base`, `account`, `sale`, `hr_expense` |
| **OCA** | `addons/oca/<repo>/` | OCA GitHub repos | Never modify source. Override via `_inherit` in `ipai_*`. Pin in `.gitmodules`. | `web_responsive`, `account_reconcile_oca`, `mis_builder` |
| **Bridge** | `addons/ipai/ipai_<domain>_<feature>/` | InsightPulse AI | Full ownership. Extends core/OCA via `_inherit`. Thin integration layer to Azure/Foundry services. | `ipai_odoo_copilot`, `ipai_copilot_actions`, `ipai_enterprise_bridge` |
| **Local** | `addons/local/` | InsightPulse AI | Minimal overrides that do not fit bridge pattern. Rare. Not in default addons_path. | (avoid if possible) |
| **L10n** | `vendor/odoo/addons/l10n_*/` or `addons/oca/l10n-*/` | Odoo SA / OCA | Country-specific localization. Never modify upstream. Override via `ipai_l10n_*` if needed. | `l10n_ph`, `l10n_ph_bir` |
| **Experimental** | `addons/ipai/ipai_exp_*/` | InsightPulse AI | Proof-of-concept. Never installed in production. `development_status: Alpha` in manifest. | `ipai_exp_voice_input` |

## Decision Flow

```
Need a capability?
  |
  +-- Is it in Odoo CE core? -> Use core. Done.
  |
  +-- Is there a stable OCA module? -> Adopt OCA. Done.
  |
  +-- Is it a thin bridge to an external service? -> Create ipai_<domain>_<feature>. Done.
  |
  +-- Is it a localization? -> Use l10n_* from core/OCA. Override only if needed.
  |
  +-- Is it experimental/POC? -> Create ipai_exp_*. Never deploy to production.
  |
  +-- None of the above? -> Create ipai_<domain>_<feature> as bridge module.
```

This is the `Config -> OCA -> Delta (ipai_*)` philosophy from CLAUDE.md.

## Naming Convention

### Bridge Modules (ipai_*)

Pattern: `ipai_<domain>_<feature>`

| Domain | Examples |
|--------|---------|
| `ai` | `ipai_ai_copilot`, `ipai_ai_tools` |
| `auth` | `ipai_auth_oidc` |
| `finance` | `ipai_finance_ppm` |
| `copilot` | `ipai_copilot_actions` |
| `odoo` | `ipai_odoo_copilot` |
| `enterprise` | `ipai_enterprise_bridge` |
| `l10n` | `ipai_l10n_ph_bir` |
| `exp` | `ipai_exp_voice_input` |

### Manifest Requirements

Every `ipai_*` module manifest must include:

```python
{
    'name': 'IPAI <Feature Name>',
    'version': '19.0.1.0.0',
    'category': '<Odoo Category>',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'depends': ['<minimal explicit deps>'],
    'data': [
        'security/ir.model.access.csv',
        # ...
    ],
    'installable': True,
    'auto_install': False,
    'development_status': 'Beta',  # or Alpha, Stable, Mature
}
```

## Governance Rules

### Core (vendor/odoo/)

- Read-only. Never modify files under `vendor/odoo/`.
- Updated via `git pull` from upstream Odoo 19 branch.
- If core behavior needs adjustment, create an `ipai_*` module using `_inherit`.

### OCA (addons/oca/)

- Governed by `oca-governance.md` rules.
- Submodule pins in `.gitmodules`. Update via `git submodule update --remote`.
- Never modify OCA source. Create `ipai_*` override module instead.
- Quality gate: 19.0 branch exists, CI green, `development_status >= Stable`.
- Must-have baseline: 56 modules across 3 categories (see `oca-governance.md`).

### Bridge (addons/ipai/)

- Full ownership by InsightPulse AI team.
- Must follow Odoo 19 coding conventions (`odoo19-coding.md`).
- Must have `ir.model.access.csv` with all 4 CRUD columns.
- Must not depend on Enterprise modules or odoo.com IAP.
- Minimal dependencies -- depend only on what you actually use.

### Experimental (addons/ipai/ipai_exp_*)

- `development_status: Alpha` required in manifest.
- Not in production addons_path.
- No stable module may depend on an experimental module.
- Graduation path: rename from `ipai_exp_*` to `ipai_*` when stable.

## SSOT References

- Module manifest registry: `config/addons.manifest.yaml`
- OCA baseline: `ssot/odoo/oca-baseline.yaml`
- OCA lock: `ssot/odoo/oca.lock.ce19.json`
- Package classification: `ssot/odoo/package-classification.yaml`
