# EE Parity SSOT

This folder is the canonical source of truth for:

- EE feature catalog
- OCA/CE replacements
- install plans
- verification suites + results
- runtime evidence snapshots

## Files

- **EE_PARITY_SSOT.dbml** - ERD source (DBML format)
- **EE_SURFACE_CATALOG.yaml** - Odoo.sh platform features (24 Tier-0 surfaces)
- **VERCEL_ENTERPRISE_CATALOG.yaml** - Vercel Enterprise+ features (15 Tier-0 surfaces)
- **SUPABASE_FEATURES_CATALOG.yaml** - Supabase features (78 features with utilization tracking)
- **PARITY_GOALS.yaml** - Parity goals and targets

## Total Platform Surfaces

- **Odoo.sh**: 24 Tier-0 surfaces
- **Vercel Enterprise+**: 15 Tier-0 surfaces
- **Supabase**: 78 features (20 implemented, 12 planned, 46 N/A)
- **Total**: 117 platform capabilities tracked

## Usage

### Generate ERD from DBML

```bash
# Using dbdocs.io CLI
dbdocs build docs/parity/EE_PARITY_SSOT.dbml

# Or using dbdiagram.io (paste DBML content)
```

### View Feature Utilization

```bash
# Supabase features
yq '.summary' docs/parity/SUPABASE_FEATURES_CATALOG.yaml

# Odoo.sh surfaces
yq '.surfaces[] | select(.tier == 0)' docs/parity/EE_SURFACE_CATALOG.yaml | wc -l

# Vercel Enterprise surfaces
yq '.surfaces[] | select(.tier == 0)' docs/parity/VERCEL_ENTERPRISE_CATALOG.yaml | wc -l
```

### Check Parity Status

```bash
python3 scripts/parity/parity_check.py
```

## Odoo ORM Models

The parity SSOT is implemented as Odoo models in the `ipai_ee_parity` addon:

- `ipai.parity.feature` - EE feature catalog
- `ipai.parity.requirement` - Feature requirements
- `ipai.parity.solution` - Replacement solutions (OCA/CE/IPAI)
- `ipai.parity.mapping` - Feature → Solution coverage mapping
- `ipai.parity.install.plan` - Install plans
- `ipai.parity.install.step` - Install steps with dependencies
- `ipai.parity.verification.suite` - Test suites
- `ipai.parity.test.case` - Test cases
- `ipai.parity.run` - Test runs
- `ipai.parity.run.result` - Test results
- `ipai.parity.runtime.evidence` - Runtime evidence snapshots
- `ipai.parity.model.map` - Odoo model mappings

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PARITY SSOT SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Features   │──────│ Requirements │                   │
│  └──────┬───────┘      └──────────────┘                   │
│         │                                                   │
│         │  ┌──────────────┐                                │
│         ├──│   Mappings   │──┐                            │
│         │  └──────────────┘  │                            │
│         │                     │                            │
│  ┌──────▼───────┐      ┌─────▼────────┐                  │
│  │  Solutions   │      │ Constraints  │                  │
│  └──────┬───────┘      └──────────────┘                  │
│         │                                                   │
│         │  ┌──────────────┐                                │
│         ├──│ Install Plan │                                │
│         │  └──────┬───────┘                                │
│         │         │                                         │
│         │  ┌──────▼───────┐                                │
│         │  │ Install Step │                                │
│         │  └──────────────┘                                │
│         │                                                   │
│  ┌──────▼───────┐      ┌──────────────┐                  │
│  │  Model Map   │      │ Verification │                  │
│  └──────────────┘      └──────┬───────┘                  │
│                                │                            │
│                         ┌──────▼───────┐                  │
│                         │  Test Cases  │                  │
│                         └──────┬───────┘                  │
│                                │                            │
│                         ┌──────▼───────┐                  │
│                         │  Test Runs   │                  │
│                         └──────┬───────┘                  │
│                                │                            │
│                         ┌──────▼───────┐                  │
│                         │   Results    │                  │
│                         └──────────────┘                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Runtime Evidence (JSONB snapshots)          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Scaffold Odoo addon** - Create `ipai_ee_parity` addon with ORM models
2. **Seed initial data** - Populate features, solutions, and mappings
3. **Implement verification** - Create test suites and automated checks
4. **Runtime evidence collector** - Cron job to capture snapshots
5. **Dashboard** - Build UI to visualize parity status
