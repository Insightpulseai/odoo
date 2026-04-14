# ipai_<module_name>

> **Template.** Copy this directory to `addons/ipai/ipai_<module_name>/`,
> replace every `<module_name>` placeholder, and fill in the required sections below.
> See `CLAUDE.md` §"Odoo extension and customization doctrine".

## Purpose

One-paragraph statement of what this module does in plain language.

## Scope

- **In scope:** what this module covers
- **Non-goals:** what this module explicitly does NOT cover

## Module type

One of: **bridge** | **overlay** | **adapter** | **extension**

## Dependencies

- Odoo CE modules: `...`
- OCA modules: `...`
- Other `ipai_*` modules: `...`

## Installation

```bash
./scripts/odoo_install.sh -d odoo_dev -m ipai_<module_name>
```

## User flows

1. ...
2. ...

## Installed components

- Models: `...`
- Views: `...`
- Security groups: `...`
- Cron jobs: `...`

## Upgrade notes

- From version X.Y → X.Z: ...

## Required documentation

- [Module introspection](docs/MODULE_INTROSPECTION.md) — why this module exists
- [Technical guide](docs/TECHNICAL_GUIDE.md) — how it's built

## Owner

- Primary: ...
- Backup: ...
