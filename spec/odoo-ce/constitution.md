# Odoo CE Platform Constitution

## Mission
Run a self-hosted Odoo 18 Community Edition platform with OCA modules and IPAI custom modules, with deterministic CI gates and no Enterprise/IAP dependencies.

## Non-negotiables
- CE + OCA only (no Enterprise modules)
- No IAP upsells: no outbound references or “buy credits” flows
- Deterministic contracts: repo structure + schema artifacts must be drift-checked in CI
- Production deployment must be reproducible from git + CI

## Quality Gates
- Repo structure check must pass
- Contract checks must pass (repo tree + schema artifacts)
- Odoo/OCA CI must pass for touched modules
