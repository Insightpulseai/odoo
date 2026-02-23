# Tasks: Odoo EE Parity Seed Generator

## Milestone 1: Foundation (Spec Kit + Schema)

- [x] 1.1: Create `spec/odoo-ee-parity-seed/` directory structure
- [x] 1.2: Write `constitution.md` (principles, constraints, success criteria)
- [x] 1.3: Write `spec.md` (functional/non-functional requirements)
- [x] 1.4: Write `plan.md` (architecture, file structure, sequence)
- [x] 1.5: Write `tasks.md` (this file)
- [ ] 1.6: Create `kb/parity/editions_seed.schema.json` (JSON Schema definition)
- [ ] 1.7: Validate schema with example YAML fixture

## Milestone 2: Phase 1 - Seed Generator

- [ ] 2.1: Create `scripts/gen_odoo_editions_parity_seed.py`
- [ ] 2.2: Implement HTML fetching with retry logic
- [ ] 2.3: Implement BeautifulSoup parsing (text-based extraction)
- [ ] 2.4: Implement area → app → feature data model
- [ ] 2.5: Implement heuristic EE-only detection
- [ ] 2.6: Implement YAML output with placeholder mappings
- [ ] 2.7: Test script execution locally
- [ ] 2.8: Verify output YAML is valid and contains ≥20 rows

## Milestone 3: CI/CD Integration

- [ ] 3.1: Create `.github/workflows/editions-parity-seed.yml`
- [ ] 3.2: Configure weekly cron (Sundays at midnight UTC)
- [ ] 3.3: Add manual trigger (`workflow_dispatch`)
- [ ] 3.4: Implement drift detection (`git diff --exit-code`)
- [ ] 3.5: Add artifact upload (seed YAML)
- [ ] 3.6: Test manual workflow trigger
- [ ] 3.7: Verify CI runs successfully

## Milestone 4: Documentation

- [ ] 4.1: Create `spec/parity/README.md` (usage guide)
- [ ] 4.2: Document manual enrichment workflow
- [ ] 4.3: Add inline comments to Python script
- [ ] 4.4: Document data model and heuristics
- [ ] 4.5: Create quickstart guide for developers

## Milestone 5: Testing (Future)

- [ ] 5.1: Create `scripts/parity/test_generate_seed.py` (unit tests)
- [ ] 5.2: Write `test_slugify()`, `test_heuristic_detection()`
- [ ] 5.3: Create smoke test script
- [ ] 5.4: Test full pipeline end-to-end
- [ ] 5.5: Verify schema validation catches errors

## Milestone 6: Enrichment Scripts (Future - Phase 2)

- [ ] 6.1: Create `scripts/parity/enrichment/match_ce_modules.py`
- [ ] 6.2: Create `scripts/parity/enrichment/match_oca_equivalents.py`
- [ ] 6.3: Create `scripts/parity/enrichment/apply_manual_overrides.py`
- [ ] 6.4: Create `parity/oca_map.yaml` manual override file

## Milestone 7: Cross-Reference (Future - Phase 3)

- [ ] 7.1: Create `scripts/parity/cross_reference.py`
- [ ] 7.2: Implement seed vs ee_parity_mapping.yml comparison
- [ ] 7.3: Generate deduplication reports
- [ ] 7.4: Add CI gate for duplicate detection
