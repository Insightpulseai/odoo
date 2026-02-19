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

---

## ipai_* Namespace Reservation (Non-Negotiable)

The `ipai_*` module namespace is RESERVED for:
- Integration Bridge connectors (e.g. `ipai_slack_connector`, `ipai_auth_oidc`)
- AI/MCP tools with no OCA equivalent
- BIR compliance modules (Philippine-specific)
- OCR/expense automation glue

The `ipai_*` namespace is FORBIDDEN for:
- Modules that replicate Odoo Enterprise functionality → use `addons/oca/*`
- Modules that replicate existing OCA modules → use or extend `addons/oca/*`
- General business logic → use `addons/oca/*`

**Justification requirement**: Any `ipai_*` module outside the reserved categories
MUST have a `PARITY_CONNECTOR_JUSTIFICATION.md` in its module directory.

---

## Supabase SSOT + Odoo SOR Boundary (Non-Negotiable)

### Definitions
- **System of Record (SOR):** The authoritative system for legally auditable ERP transactions and accounting artifacts.
- **System of Truth (SSOT):** The authoritative system for control-plane truth: identity/authorization for non-Odoo apps, orchestration state, integration checkpoints, master-data overlays, analytics/AI layers, and governance evidence.

### Odoo is the SOR for:
- Accounting truth: invoices/bills, journal entries, payments, taxes, reconciliations
- ERP operational truth (final state): stock moves, POs/SOs (final), manufacturing orders
- Legal/audit artifacts: posted documents and final approvals that must match the ledger

**Rule:** Supabase may store *references* to Odoo SOR entities (ids, external_ids, hashes, timestamps) and *replicas* for analytics, but must not become authoritative for the above.

### Supabase is the SSOT for:
- **ops/control plane:** runs, run_events, job queues, retries/DLQ, idempotency keys, artifacts/evidence
- **identity & access for non-Odoo surfaces:** portals, ops-console, agents, APIs (RLS-first)
- **integration state:** cursors/checkpoints, mapping tables, sync configurations, webhook receipts
- **master data overlays:** enrichment, canonical product/brand/category registries (when not owned by Odoo)
- **analytics & AI layers:** gold/platinum views, embeddings, feature stores, insight artifacts

### Ownership & conflict policy
1. Each entity has exactly one owner system (**Odoo** OR **Supabase**).
2. If owned by Odoo, Supabase never "wins" conflicts; conflicts become **exceptions** routed to review/repair.
3. Write paths into Odoo are **restricted** to non-SOR domains (e.g., enrichment tags) and must be audited (run_events + artifacts).

### Hard "Don'ts"
- Don't implement a "shadow ledger" in Supabase (no authoritative accounting postings outside Odoo).
- Don't create write paths into Odoo for Odoo-owned domains (ledger/posted docs/inventory moves).
- Don't bypass RLS for app clients; only service workers may use elevated roles, with audit trails.

## Supabase Partner Integrations Policy (SSOT Extension Surface)

Supabase partner integrations are permitted only when:
1. A Supabase-native primitive does not already solve the requirement, and
2. The integration does not violate SSOT/SOR boundaries (no shadow ledger; no writebacks into Odoo-owned domains).

### Allowed categories (typical)
- Auth (external IdP/UI), DevTools, Data Platform admin, Messaging/Email, FDW/federation, Edge runtimes.

### Required controls
- RLS remains the authorization perimeter for non-Odoo surfaces.
- Any worker/integration must emit `ops.runs`, `ops.run_events`, `ops.artifacts`.
- Secrets remain out of git; injected via env/secret stores only.

## Supabase UI Policy (Accelerator, Not SSOT)

- Supabase UI components are permitted as **scaffolding** for SSOT-facing apps (ops-console, portals, agent consoles)
  where **Supabase Auth + RLS** is the authorization perimeter.
- Supabase UI must not become the canonical design system; our design tokens remain SSOT.
- Treat Supabase UI as **shadcn-style generated components** (vendored into repo), not a long-lived dependency,
  because the legacy `supabase/ui` library is deprecated and components are moving into the main monorepo.
