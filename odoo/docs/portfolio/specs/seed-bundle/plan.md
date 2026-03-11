# Plan — Seed Bundle

## Architecture

```
seeds/
├── workstreams/
│   ├── afc_financial_close/      # SAP AFC equivalent
│   │   ├── 00_workstream.yaml    # Workstream definition
│   │   ├── 10_templates.yaml     # Close templates
│   │   ├── 20_tasks.yaml         # 33 closing tasks
│   │   ├── 30_checklists.yaml    # Evidence requirements
│   │   ├── 40_kpis.yaml          # Performance metrics
│   │   ├── 50_roles_raci.yaml    # Role assignments
│   │   └── 90_odoo_mapping.yaml  # Odoo model mapping
│   │
│   └── stc_tax_compliance/       # SAP STC equivalent
│       ├── 00_workstream.yaml    # Workstream definition
│       ├── 10_worklist_types.yaml
│       ├── 20_compliance_checks.yaml
│       ├── 30_scenarios.yaml
│       ├── 60_localization_ph.yaml
│       └── 90_odoo_mapping.yaml
│
├── shared/                       # Cross-workstream configs
│   ├── roles.yaml
│   ├── calendars.yaml
│   ├── notification_profiles.yaml
│   ├── approval_policies.yaml
│   └── org_units.yaml
│
├── schema/                       # Yamale schemas
│   ├── afc_workstream.schema.yaml
│   ├── afc_templates.schema.yaml
│   ├── afc_tasks.schema.yaml
│   ├── stc_workstream.schema.yaml
│   ├── stc_checks.schema.yaml
│   ├── stc_scenarios.schema.yaml
│   └── shared_calendars.schema.yaml
│
└── scripts/
    ├── validate_seeds.sh         # Schema validation
    └── yaml_to_payload.py        # JSON export
```

## Implementation Phases

### Phase 1: Structure (Complete)
- [x] Create directory structure
- [x] Define AFC workstream and tasks
- [x] Define STC workstream and checks
- [x] Add shared configurations

### Phase 2: Validation (Complete)
- [x] Create Yamale schemas
- [x] Create validation script
- [x] Add CI workflow

### Phase 3: Integration (Complete)
- [x] Create yaml_to_payload converter
- [x] Create ipai_ppm_a1 Odoo module
- [x] Add import/export wizards

### Phase 4: Operations (Pending)
- [ ] Load seeds into production Odoo
- [ ] Verify import accuracy
- [ ] Document operational procedures

## Tooling

| Tool | Purpose | Version |
|------|---------|---------|
| yamale | Schema validation | latest |
| yamllint | YAML linting | latest |
| pyyaml | YAML parsing | 6.0+ |

## CI Integration

GitHub Actions workflow validates on PR:
1. Run yamllint (warnings only)
2. Run yamale schema validation
3. Test yaml_to_payload conversion
4. Verify output is valid JSON
