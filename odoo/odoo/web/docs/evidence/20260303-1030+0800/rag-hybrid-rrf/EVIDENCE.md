# RAG Hybrid Search RRF — Post-Merge Proof

**PR**: #506 (feat/rag-db-hybrid-rrf)
**Merged**: 2026-03-03T01:02:24Z (commit 80da7ddec)
**Evidence stamp**: 20260303-1030+0800

## Pipeline Summary

| Step | Status | Detail |
|------|--------|--------|
| Migrations applied | PASS | 20260303000001 + 20260303000002 via Management API |
| Corpus upsert | PASS | 443 docs, 1021 chunks across 5 corpora |
| tsvector population | PASS | 1021/1021 chunks with English stemmer |
| Smoke query (FTS) | PASS | 5/5 queries returning relevant results |
| Hotfix migration | COMMITTED | 20260303000003_rag_hotfixes.sql |

## Corpus Breakdown

| corpus_id | documents | chunks |
|-----------|-----------|--------|
| spec_bundles | 204 | 347 |
| ssot_yaml | 122 | 425 |
| docs_ai | 38 | 109 |
| docs_contracts | 22 | 40 |
| docs_runbooks | 57 | 100 |
| **Total** | **443** | **1021** |

## Hotfixes Applied (captured in migration 20260303000003)

1. **Trigger stemmer**: `rag.chunks_tsv_update()` used `'simple'` (no stemming) — changed to `'pg_catalog.english'`
2. **Column name**: `fts_search` and `hybrid_search_rrf` referenced `c.fts_content` — corrected to `c.tsv`
3. **Index type**: btree on `section_path` exceeded 2704-byte row limit — replaced with hash index
4. **PostgREST exposure**: Created public wrapper functions for `fts_search` and `hybrid_search_rrf` (SECURITY DEFINER)

## Smoke Query Results

All 5 queries PASS with relevant top hits and correct corpus matching:

- SMOKE-001 "copilot rules confirmation" → spec/ai-copilot/constitution.md (score 0.0221)
- SMOKE-002 "tool permissions" → docs/contracts/C-TOOLS-PERMISSIONS-01.md (score 0.3533)
- SMOKE-003 "Gemini provider AI" → ssot/ai/odoo_ai.yaml (score 0.1053)
- SMOKE-004 "release gates deployment" → spec/odoo-release-gates-control-plane/prd.md (score 0.0418)
- SMOKE-005 "IPAI module naming" → ssot/parity/odoo_enterprise.yaml (score 0.2372)

## Evidence Artifacts

- `logs/smoke_results.json` — full smoke query output with scores
- `logs/upsert_results.json` — full 5-corpus upsert results
- `logs/upsert_spec_bundles.json` — spec_bundles retry (after btree fix)

## STATUS=COMPLETE
