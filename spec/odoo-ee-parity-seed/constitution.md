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

---

## Article 3: Integration Invariants (Provider API Keys & Credentials)

### §3.1 No Client-Side Provider Keys (Hard Rule)

**Statement**: External provider API keys (Gemini, OpenAI, n8n Google credentials, etc.) MUST NEVER be exposed to client-side code (browser, mobile apps).

**Rationale**:
- Client-side exposure enables key theft, quota abuse, and unauthorized usage
- Browser DevTools, bundle source maps, and network inspection expose secrets
- Mobile app decompilation reveals hardcoded keys

**Enforcement**:
- CI linter MUST flag any provider API key usage in client-side code paths
- All provider API calls MUST route through server-side proxies (Supabase Edge Functions, backend routes)
- Client apps use `anon` key only, constrained by RLS

**Examples**:
- ✅ Supabase Edge Function calls Gemini API with `GEMINI_API_KEY` from Vault
- ✅ Backend route uses Google Service Account key from env/secret store
- ❌ React component imports `GEMINI_API_KEY` from `.env.local`
- ❌ Mobile app bundles `google_service_account.json` as asset

### §3.2 Secrets Referenced Only (Hard Rule)

**Statement**: All provider credentials MUST be referenced via environment variables or secret store paths, NEVER embedded directly in code or configuration files committed to git.

**Rationale**:
- Git history is immutable; committed secrets cannot be fully removed
- Secret rotation becomes manual and error-prone
- Compliance audits flag hardcoded secrets as critical vulnerabilities

**Enforcement**:
- `.gitignore` MUST exclude all secret files (`.env*`, `*credentials*.json`, `*service-account*.json`)
- CI secret scanner MUST run on every PR (detect patterns: `sk-`, `private_key`, `client_secret`)
- Pre-commit hook MAY warn on secret-like patterns

**Examples**:
- ✅ `process.env.GEMINI_API_KEY` in Edge Function
- ✅ Supabase Vault path: `google/service_account_key`
- ❌ `const apiKey = "sk-proj-abc123..."` in source file
- ❌ `credentials.json` committed with service account key

### §3.3 n8n Credentials Are Operational Config, Supabase Is SSOT (Hard Rule)

**Statement**: n8n credential objects are execution context configuration. Supabase `ops.*` tables are the canonical SSOT for integration state, audit trails, and provenance.

**Rationale**:
- n8n credentials are transient (encrypted in n8n DB, not version-controlled)
- Integration state (sync cursors, checkpoints) must persist beyond n8n execution
- Audit trails must be queryable and compliance-ready (Supabase provides this)

**Ownership Matrix**:
- **n8n owns**: Encrypted token storage, OAuth refresh automation, workflow execution context
- **Supabase SSOT owns**: Integration state (`ops.integration_state`), audit logs (`ops.run_events`), provenance tracking
- **Odoo SOR owns**: Nothing (integrations are operational control-plane, not ERP ledger)

**Conflict Policy**:
- If n8n and Supabase disagree on integration state, Supabase wins (SSOT)
- n8n execution logs are transient; `ops.run_events` is canonical audit trail
- n8n credential changes (rotation) MUST emit events to `ops.credential_rotations`

**Examples**:
- ✅ n8n stores Google OAuth refresh token → Supabase logs API call events
- ✅ n8n workflow updates `ops.integration_state` with Drive sync cursor
- ❌ n8n workflow writes directly to Odoo ledger tables (SOR violation)
- ❌ Integration state stored only in n8n workflow JSON (not queryable SSOT)

### §3.4 Audit Trail Completeness (Hard Rule)

**Statement**: Every external provider API call MUST emit a structured event to Supabase `ops.run_events` with correlation_id, request metadata, and response status.

**Rationale**:
- Compliance audits require complete trails (who, what, when, why)
- Debugging requires correlation across distributed systems (n8n, Edge Functions, Odoo)
- Cost monitoring requires token/quota usage tracking per API call

**Required Event Fields**:
- `run_id` (FK to `ops.runs`)
- `event_type` (e.g., `gemini_api_call`, `google_api_call`)
- `event_data`:
  - `provider` (gemini, google, openai, etc.)
  - `operation` (generateContent, files.list, chat.completions.create)
  - `request_id` / `correlation_id`
  - `response_status` (200, 429, 500, etc.)
  - `quota_consumed` (tokens, API units)
  - `latency_ms`

**Enforcement**:
- CI checks MUST verify all Edge Functions emit audit events
- Weekly compliance report: "API calls without audit trail" (target: 0)

**Examples**:
- ✅ Edge Function logs Gemini API call with prompt tokens, response status
- ✅ n8n workflow emits event to `ops.run_events` after Google Drive API call
- ❌ API call made without corresponding `ops.run_events` entry
- ❌ Audit event missing `correlation_id` or `response_status`

---

## Article 4: Structural Boundaries

### §4.1 Directory Taxonomy

The repository organizes Odoo modules into four canonical directories:

1. **`addons/odoo/`** (Upstream Core): Odoo CE core modules (read-only reference)
2. **`addons/oca/`** (EE Parity Layer): Modules implementing Odoo Enterprise Edition feature parity using OCA patterns
3. **`addons/ipai/`** (Integration Bridges): Modules connecting Odoo to external services and systems
4. **`addons/ipai_meta/`** (Meta Modules): Repository infrastructure and development tooling

**Authoritative Reference**: `docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md` defines complete taxonomy, boundary rules, decision trees, and migration strategy.

### §4.2 Parity Location Invariant (Hard Rule)

**Statement**: All modules implementing Odoo Enterprise Edition feature parity MUST reside in `addons/oca/`.

**Rationale**:
- OCA modules provide community-vetted implementations
- Reduces maintenance burden (shared upstream)
- Avoids duplication and fragmentation

**Enforcement**: CI keyword detection + manifest parsing in `scripts/ci/check_parity_boundaries.sh`

**Examples**:
- ✅ `addons/oca/subscription_management` (EE parity)
- ❌ `addons/ipai/ipai_subscriptions` (wrong location)

### §4.3 Integration Scope Constraint (Hard Rule)

**Statement**: Modules in `addons/ipai/` MUST be integration bridges or external service connectors ONLY.

**Allowed Categories**:
- External service connectors (Slack, Auth0, payment gateways)
- API bridges (MCP, REST controllers for non-Odoo clients)
- AI/ML tools (OCR, document processing, embeddings)
- BIR compliance (Philippine-specific tax/regulatory)
- Data integration (ETL, sync engines, webhook receivers)

**Forbidden Categories**:
- ❌ EE feature parity (belongs in `addons/oca/`)
- ❌ General business logic (belongs in `addons/oca/`)
- ❌ OCA module duplicates (extend existing OCA modules instead)

**Enforcement**: Justification file requirement (`PARITY_CONNECTOR_JUSTIFICATION.md`) + CI validation

### §4.4 Baseline Tolerance Policy

**Current State**: 45 existing violations tracked in `scripts/ci/baselines/parity_boundaries_baseline.json`

**Policy**:
- **Existing violations**: Allowed to remain (grandfathered)
- **New violations**: Blocked by CI (must fix before merge)
- **Migration cadence**: Incremental over 6 months (target: zero violations by 2026-08-20)
- **Baseline review**: First Monday of each month

**Rationale**: Avoid forced migrations and repository churn while preventing new violations.

### §4.5 Enforcement Chain

**CI Workflow** → `scripts/ci/check_parity_boundaries.sh` → Baseline Comparison → Documentation

**Enforcement Mechanisms**:
1. **CI Validation** (`.github/workflows/parity-boundaries.yml`):
   - Runs on every PR to `main`
   - Keyword detection (EE terms in wrong location)
   - Manifest parsing (Enterprise dependencies)
   - Justification file verification
   - Baseline comparison (allow existing, block new)

2. **Pre-Commit Hook** (optional):
   - Local enforcement before CI
   - Faster feedback loop
   - Reduces CI build failures

3. **Monthly Baseline Review**:
   - First Monday of each month
   - Track migration progress (7-8 modules per month target)
   - Update baseline after approved migrations

**Exit Codes**:
- `0`: Pass (no new violations)
- `1`: Fail (new violations detected)

**Cross-References**:
- Complete taxonomy: `docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md`
- CI script: `scripts/ci/check_parity_boundaries.sh`
- Baseline tracking: `scripts/ci/baselines/parity_boundaries_baseline.json`
- Workflow: `.github/workflows/parity-boundaries.yml`
