# Implementation Plan: Odoo EE Parity Seed Generator

## Architecture

**3-Phase Pipeline:**
1. **Phase 1:** Seed generation (Editions page → YAML)
2. **Phase 2:** Enrichment (CE candidates + OCA equivalents)
3. **Phase 3:** Cross-reference (deduplication with ee_parity_mapping.yml)

## File Structure

```
spec/odoo-ee-parity-seed/
├── constitution.md              # Spec Kit constitution
├── spec.md                      # Feature specification (PRD-equivalent)
├── plan.md                      # This file
└── tasks.md                     # Task breakdown

spec/parity/
├── odoo_editions_parity_seed.yaml   # Main output
└── README.md                        # Usage guide

scripts/
└── gen_odoo_editions_parity_seed.py # Working scraper implementation

.github/workflows/
└── editions-parity-seed.yml         # Weekly CI workflow
```

## Implementation Sequence

### Phase 1: Foundation (Spec Kit + Schema)
1. Create Spec Kit directory structure
2. Write constitution.md (principles, constraints)
3. Write spec.md (requirements, data model)
4. Write plan.md (this file)
5. Write tasks.md (task breakdown)

### Phase 2: Core Generator Script
1. Create `gen_odoo_editions_parity_seed.py` with working implementation
2. Implement HTML fetching with retry logic
3. Implement BeautifulSoup parsing (text-based extraction)
4. Implement area → app → feature data model
5. Implement heuristic EE-only detection
6. Implement YAML output with placeholder mappings
7. Test script execution locally

### Phase 3: CI/CD Integration
1. Create `.github/workflows/editions-parity-seed.yml`
2. Configure weekly cron (Sundays at midnight UTC)
3. Add manual trigger (`workflow_dispatch`)
4. Implement drift detection (`git diff --exit-code`)
5. Add artifact upload
6. Test CI workflow

### Phase 4: Documentation
1. Create `spec/parity/README.md` with manual enrichment guide
2. Add inline comments to Python script
3. Document data model and heuristics

## Key Technical Decisions

### BeautifulSoup4 Text-Based Parsing
- **Why:** Resilient to markup changes, simpler than DOM traversal
- **How:** Extract visible text dump, parse for section/app/feature patterns
- **Trade-off:** Less precise than CSS selectors, but more maintainable

### Heuristic EE-Only Detection
- **Keywords:** OCR, AI, Studio, VoIP, IoT, Barcode, Shopfloor, Scheduling
- **Conservative:** Defaults to `assumed_ee_only: false` unless keyword match
- **Override:** Manual enrichment can correct false positives/negatives

### Placeholder Mapping Fields
- **Phase 1:** All mapping fields set to `null`, confidence to `0.0`
- **Phase 2:** Manual enrichment fills in OCA repos/modules
- **Benefit:** Clean separation of automated extraction vs manual curation

## Verification Strategy

### Local Testing
```bash
python scripts/gen_odoo_editions_parity_seed.py
python -c "import yaml; d=yaml.safe_load(open('spec/parity/odoo_editions_parity_seed.yaml')); print(f\"Extracted {len(d['parity_seed']['rows'])} rows\")"
```

### CI Testing
- Weekly automated execution
- Drift detection via `git diff`
- Artifact upload for manual review
- ≥20 rows smoke test

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Editions page HTML changes | Text-based parsing is resilient; CI detects changes weekly |
| Network timeout | HTTP timeout 30s; user-agent header avoids bot blocking |
| YAML syntax errors | PyYAML handles escaping; CI syntax validation |
| Manual enrichment drift | Seed regeneration preserves manual edits via git merge |

## Rollback Plan

```bash
# Revert to last commit
git checkout HEAD^ -- spec/parity/odoo_editions_parity_seed.yaml

# Or disable CI workflow
# Edit .github/workflows/editions-parity-seed.yml → comment out cron
```

## Estimated Effort

- Phase 1 (Spec Kit): 1 hour
- Phase 2 (Script): 30 minutes
- Phase 3 (CI): 1 hour
- Phase 4 (Docs): 30 minutes

**Total:** ~3 hours
