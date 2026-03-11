# Product Requirements: Odoo EE Parity Seed Generator

## Overview

Automated system to extract Odoo Enterprise vs Community Edition capabilities from the official Editions comparison page using a working Python implementation.

## User Stories

**As a** parity maintainer,
**I want** an automatically updated catalog of all EE capabilities,
**So that** I can identify new features requiring OCA parity solutions.

**As a** developer,
**I want** confidence-scored OCA module recommendations,
**So that** I can quickly find equivalents without manual research.

**As a** CI/CD engineer,
**I want** deterministic seed generation with drift detection,
**So that** Editions page changes trigger alerts automatically.

## Functional Requirements

### FR1: Editions Page Scraping
- **FR1.1:** Fetch HTML from `https://www.odoo.com/page/editions`
- **FR1.2:** Parse 11+ capability categories (Finance, Sales, HR, etc.)
- **FR1.3:** Extract capability names and descriptions
- **FR1.4:** Generate unique IDs via slugification
- **FR1.5:** Deduplicate based on normalized names
- **FR1.6:** Attach evidence URLs with section anchors

### FR2: Seed YAML Generation
- **FR2.1:** Output schema: `meta`, `categories`, `capabilities` sections
- **FR2.2:** Mark availability as "unknown" (conservative default)
- **FR2.3:** Include metadata: extraction confidence, manual review flag
- **FR2.4:** Validate against `kb/parity/editions_seed.schema.json`
- **FR2.5:** Atomic write (temp file + rename)

### FR3: CE Module Candidate Detection (Enrichment Phase 2)
- **FR3.1:** Scan Odoo CE `vendor/odoo/odoo/addons/` manifests
- **FR3.2:** Match capability names to module summaries
- **FR3.3:** Confidence scoring: exact match (1.0), fuzzy (0.5-0.9), description overlap (0.3-0.7)
- **FR3.4:** Output `enriched/ce_candidates.yaml`

### FR4: OCA Equivalent Matching (Enrichment Phase 2)
- **FR4.1:** Load `oca.lock.json` as module index (288 modules)
- **FR4.2:** Keyword matching: capability → OCA module keywords
- **FR4.3:** Category mapping: Finance → `OCA/account-*` repos
- **FR4.4:** Manual override via `parity/oca_map.yaml` (priority 1)
- **FR4.5:** Confidence scoring: keyword overlap, category alignment, manual override
- **FR4.6:** Output `enriched/oca_equivalents.yaml`

### FR5: Cross-Reference & Deduplication
- **FR5.1:** Compare seed IDs with `ee_parity_mapping.yml` feature_ids
- **FR5.2:** Generate reports:
  - `new_capabilities.yaml` - Seed rows not in mapping
  - `missing_from_seed.yaml` - Mapping features not in seed
  - `duplicates.yaml` - ID conflicts requiring resolution
- **FR5.3:** Exit non-zero if duplicates found (CI gate)

### FR6: CI/CD Integration
- **FR6.1:** Weekly cron: Sundays at midnight UTC
- **FR6.2:** Manual trigger: `workflow_dispatch`
- **FR6.3:** Drift detection: `git diff --exit-code parity/parity_seed.editions.yaml`
- **FR6.4:** Artifact upload: seed YAML + enrichment results
- **FR6.5:** Slack notification on drift (optional)

## Non-Functional Requirements

### NFR1: Performance
- **NFR1.1:** Total runtime <1 minute (acceptable for CI)
- **NFR1.2:** Network fetch <30 seconds
- **NFR1.3:** Schema validation <5 seconds

### NFR2: Reliability
- **NFR2.1:** HTTP retry with exponential backoff (3 attempts)
- **NFR2.2:** Partial extraction on parse errors (log + continue)
- **NFR2.3:** Graceful degradation if enrichment fails (seed still valid)

### NFR3: Maintainability
- **NFR3.1:** Self-documenting code (type hints, docstrings)
- **NFR3.2:** Unit tests for core functions (slugify, deduplication)
- **NFR3.3:** Integration test: full pipeline smoke test

### NFR4: Security
- **NFR4.1:** No credentials required (Editions page is public)
- **NFR4.2:** No arbitrary code execution (no `eval()` on manifests)
- **NFR4.3:** Safe YAML parsing (use `yaml.safe_load` only)

## Data Model

### Seed YAML Structure (Simplified)

```yaml
parity_seed:
  source:
    url: "https://www.odoo.com/page/editions"
    fetched_at: "2026-02-13T12:00:00Z"
    notes: "Seed extracted from editions comparison page; enrich with OCA mapping + evidence URLs per row."
  schema_version: "v1"
  rows:
    - area: "Finance"                           # Section header from Editions page
      app: "Accounting"                        # App name under section
      feature: null                            # null = app-level row
      source_url: "https://www.odoo.com/page/editions"
      evidence_text: null
      assumed_ee_only: false                   # Heuristic hint only
      mapping:
        oca_repo: null                         # TODO: manual enrichment
        oca_module: null                       # TODO: manual enrichment
        ipai_module: null                      # TODO: if custom bridge needed
      confidence: 0.0                          # Default; manual override to 1.0
      notes: "seed row (app-level) from editions page"

    - area: "Finance"
      app: "Accounting"
      feature: "OCR on invoices"               # Subfeature (↳ lines from page)
      source_url: "https://www.odoo.com/page/editions"
      evidence_text: "OCR on invoices"
      assumed_ee_only: true                    # Heuristic: OCR/AI keywords detected
      mapping:
        oca_repo: "https://github.com/OCA/account-invoicing"
        oca_module: "account_invoice_import"
        ipai_module: null
      confidence: 0.8                          # Manual override after verification
      notes: "seed row (feature-level) from editions page; mapping required"
```

### Key Design Choices

- **area**: Top-level section (Finance, Sales, HR, etc.)
- **app**: Application name (Accounting, Invoicing, CRM, etc.)
- **feature**: Subfeature or null for app-level rows
- **assumed_ee_only**: Heuristic hint based on keywords (OCR, AI, Studio, VoIP, IoT, Barcode, Shopfloor, Scheduling)
- **mapping**: Placeholder structure for manual OCA enrichment
- **confidence**: Default 0.0; enrichment phase sets to 0.0-1.0 based on match quality
- **notes**: Free-form annotation for manual review

---

## Supabase Feature Mapping (SSOT Implementation Contract)

| Supabase Capability | SSOT Usage (Required) | SOR Boundary / Constraint |
|---|---|---|
| Postgres Database | Canonical schemas for `ops.*`, `mdm.*`, `ai.*`, `audit.*`, plus `odoo_replica.*` | `odoo_replica.*` is read-only replica/derivative; Odoo remains authoritative for ledger/posted docs |
| RLS + Auth | All non-Odoo apps/portals/agents must gate via Auth + RLS; tables private by default | Never grant anon/select on SOR replicas; elevate only workers; log every privileged action |
| RPC / Instant APIs | Prefer RPC as stable interface; apps call RPC not tables | RPCs must not write Odoo-owned domains; use exception queues instead |
| Edge Functions | Webhook ingestion, workers, queue consumers, backfills, signing/verification | Any write-back into Odoo must be audited and limited to non-SOR domains |
| Realtime | Ops-console run status, exception queues, human review loops | No sensitive SOR data broadcast; only event metadata + scoped payloads |
| Storage + CDN | Artifacts, exports, evidence, attachments mirrored with provenance | Odoo attachments are SOR; Supabase stores pointers/hashes unless explicitly mirrored |
| Queues | Durable async orchestration (retries, DLQ, rate limits) | Every job emits `ops.runs`, `ops.run_events`, `ops.artifacts` |
| Cron | Scheduled sync, refresh, reconciliation, reporting | Must be idempotent and checkpointed |
| Observability | Logs/metrics/drains + evidence-first verification | Fail CI if evidence hooks are missing for new workflows |
| Vectors / AI | Embeddings, retrieval indexes, feature store, insight artifacts | Must include provenance pointers to source records; no hallucinated facts without citations |

### Acceptance criteria
1. Any new integration must declare: owner system, sync mode, checkpoints, RLS model, failure modes, evidence outputs.
2. CI must be able to detect and block "shadow ledger" patterns (writes into Odoo-owned domains from Supabase).
3. All integrations must use ownership declaration template: `templates/supabase-integration/OWNERSHIP_DECLARATION.md`

---

## Testing Strategy

### Unit Tests
- `test_slugify()` - ID normalization
- `test_build_categories()` - Category aggregation
- `test_confidence_scoring()` - Match confidence calculation

### Integration Tests
- `test_seed_generation_smoke.sh` - Full pipeline execution
- `test_schema_validation.py` - Schema compliance
- `test_cross_reference.py` - Deduplication logic

### CI Tests
- Weekly determinism verification
- Drift detection accuracy
- Artifact upload success
