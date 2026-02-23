# Constitution: Odoo EE Parity Seed Generator

## Purpose
Systematically extract and track Odoo Enterprise vs Community Edition capabilities from the official Editions comparison page, providing an evidence-based foundation for OCA parity planning.

## Principles

### Evidence-Based Extraction
- All data must be traceable to the Odoo Editions page
- No hallucinations or assumptions about availability
- Mark unknown fields as "unknown" until verified
- Attach evidence URLs to every capability row

### Deterministic Generation
- Reproducible output from same source HTML
- Schema-validated YAML structure
- Idempotent execution (safe to re-run)
- CI-enforced determinism with drift detection

### Enrichment Transparency
- Confidence scoring (0.0-1.0) for all automated matches
- Manual override capability for known equivalents
- Clear separation of seed (Phase 1) vs enrichment (Phase 2)

### Integration Philosophy
- Complements (not replaces) existing `ee_parity_mapping.yml`
- Feeds into parity planning workflows
- Supports cross-referencing and deduplication

## Constraints

### Technical Constraints
- Python 3.12+ for all scripts
- BeautifulSoup4 for HTML parsing (not Selenium - keep it simple)
- YAML output (not JSON) for human readability
- Schema validation required before commit

### Operational Constraints
- Weekly CI execution (Sundays at midnight UTC)
- <1 minute total runtime (network + parsing + validation)
- Minimal dependencies (beautifulsoup4, requests, pyyaml, jsonschema only)
- No external API calls beyond fetching Editions page

### Quality Constraints
- ≥50 capabilities extracted (smoke test threshold)
- Zero duplicate IDs (enforced by script)
- Schema compliance (JSON Schema validation)
- Evidence URL for every capability

## Success Criteria

1. ✅ Seed YAML auto-generated weekly from Editions page
2. ✅ 85%+ capabilities have confidence ≥0.7 for OCA matches
3. ✅ Zero manual intervention required for weekly regeneration
4. ✅ CI detects Editions page changes within 7 days
5. ✅ Integration with existing parity workflows (cross-reference clean)

## Non-Goals

- ❌ Replacing existing `ee_parity_mapping.yml` (they serve different purposes)
- ❌ Real-time extraction (weekly is sufficient)
- ❌ JavaScript rendering (Editions page is static HTML)
- ❌ Multi-version support (focus on current Odoo major version only)
