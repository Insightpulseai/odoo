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

---

## Enforcement Plan: SSOT/SOR Boundary

- Add a CI check that scans Supabase migrations/functions for tables that look like ledger primitives (invoice/journal/payment) and blocks introducing authoritative accounting tables outside Odoo.
- Require an "ownership declaration" block in new integration specs: `owner_system: odoo|supabase`.
- Require `ops.runs/run_events/artifacts` emission for any Edge Function worker path.

## Canonical Supabase Example References (Pattern Intake)

Use raw URLs for deterministic ingestion:
- Edge Functions README: https://raw.githubusercontent.com/supabase/supabase/master/examples/edge-functions/README.md
- GH Action deploy example: https://raw.githubusercontent.com/supabase/supabase/master/examples/edge-functions/supabase/functions/github-action-deploy/README.md
- Signed webhooks pattern (Stripe): https://raw.githubusercontent.com/supabase/supabase/master/examples/edge-functions/supabase/functions/stripe-webhooks/README.md
- Auth+RLS DB access pattern: https://raw.githubusercontent.com/supabase/supabase/master/examples/edge-functions/supabase/functions/select-from-table-with-auth-rls/index.ts
- Storage multipart upload pattern: https://raw.githubusercontent.com/supabase/supabase/master/examples/edge-functions/supabase/functions/file-upload-storage/index.ts
- (Optional) Realtime reference app: https://raw.githubusercontent.com/supabase/supabase/master/examples/slack-clone/nextjs-slack-clone/README.md

## Supabase Examples Intake Playbook (Reference-Only)

### Goal
Use Supabase upstream examples to accelerate SSOT/control-plane implementation while preserving:
- Supabase as SSOT (ops/orchestration/identity for non-Odoo surfaces)
- Odoo as SOR (ledger and posted ERP truth)

### Intake rules
1. Prefer pattern extraction over cloning whole example apps.
2. Extract only:
   - RLS policy shapes
   - Edge Function worker/deploy structure
   - Auth session handling patterns
   - Storage policy patterns
3. Every extracted pattern must be re-homed under our SSOT schemas (`ops.*`, `audit.*`, `mdm.*`, `ai.*`)
   with the SSOT/SOR boundary enforced (no shadow ledger tables).

### Canonical upstream references
- Edge Functions examples (local dev + deploy + GH Actions)
- Next.js user-management tutorial (Auth + RLS + Storage)

---

## Estimated Effort

- Phase 1 (Spec Kit): 1 hour
- Phase 2 (Script): 30 minutes
- Phase 3 (CI): 1 hour
- Phase 4 (Docs): 30 minutes

**Total:** ~3 hours
