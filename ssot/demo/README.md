# Demo Seed Packs

This directory defines layered, idempotent demo/showroom data packs for Odoo CE + OCA 18.

## Principles

- deterministic load order
- idempotent seeding
- no demo pack may silently mutate production identifiers
- every seeded record must carry a stable external key
- scenario packs must depend only on lower packs, never sideways
- blocked and ready fixtures must be paired where applicable

## Pack order

1. `100-system-shared`
2. `200-finance`
3. `225-ph-compliance`
4. `250-fitout-docs`
5. `900-pulser-demo`

## Intended use

- local showroom/demo environments
- UAT/demo databases
- eval/demo scenarios for Pulser
- deterministic regression fixtures

## Not intended for

- production tenant bootstrap as-is
- uncontrolled manual editing in database UI without SSOT sync

## Loader

Run from repo root:

```bash
python scripts/demo/seed_demo.py --all
python scripts/demo/seed_demo.py --pack 200-finance
python scripts/demo/seed_demo.py --dry-run
```

## Verification

```bash
pytest tests/demo/
```
