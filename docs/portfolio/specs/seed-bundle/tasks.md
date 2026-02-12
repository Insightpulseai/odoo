# Tasks — Seed Bundle

## Completed

### Structure
- [x] Create seeds directory structure
- [x] Define AFC workstream definition
- [x] Define AFC templates (month/quarter/year)
- [x] Define 33 AFC tasks across 4 phases
- [x] Define AFC checklists (evidence requirements)
- [x] Define AFC KPIs
- [x] Define AFC RACI roles
- [x] Define AFC Odoo mapping
- [x] Define STC workstream definition
- [x] Define STC worklist types (S4_VAT, S4_VND, S4_INV, S4_WHT)
- [x] Define 16 STC compliance checks
- [x] Define 8 STC scenarios
- [x] Define PH localization overlay (BIR forms, ATC codes)
- [x] Define STC Odoo mapping
- [x] Create shared roles configuration
- [x] Create shared calendars (PH holidays 2025-2026)
- [x] Create shared notification profiles
- [x] Create shared approval policies
- [x] Create shared org units

### Validation
- [x] Create Yamale schema for AFC workstream
- [x] Create Yamale schema for AFC templates
- [x] Create Yamale schema for AFC tasks
- [x] Create Yamale schema for STC workstream
- [x] Create Yamale schema for STC checks
- [x] Create Yamale schema for STC scenarios
- [x] Create Yamale schema for shared calendars
- [x] Create validate_seeds.sh script
- [x] Create GitHub Actions workflow

### Integration
- [x] Create yaml_to_payload.py converter
- [x] Create ipai_ppm_a1 Odoo module
- [x] Create Odoo import wizard
- [x] Create Odoo export wizard
- [x] Create spec bundle documentation

## Pending

### Operations
- [ ] Test seed import in development Odoo
- [ ] Verify all 33 AFC tasks imported correctly
- [ ] Verify all 16 STC checks imported correctly
- [ ] Verify PH localization overlays applied
- [ ] Document import/export procedures

### Enhancements
- [ ] Add "Generate TaskList" wizard for period creation
- [ ] Add YAML export option (not just JSON)
- [ ] Add /ipai/a1/export API endpoint
- [ ] Add webhook token authentication

## Dependencies

| Task | Depends On |
|------|------------|
| Production import | Odoo CE18 environment |
| API endpoint | ipai_ppm_a1 module installed |
| Webhook auth | n8n/CI configuration |
