# Curation Policy (ipai-learn)

## Goal

ipai-learn is a curated enterprise documentation hub. It is NOT a mirror of operational repos (e.g., odoo-ce).

## Audience Distinction

| Repository | Primary Audience | Content Type |
|------------|------------------|--------------|
| **odoo-ce** | Developers, Operators, DevOps | Technical docs, API refs, deployment guides, runbooks |
| **ipai-learn** | Enterprise stakeholders, Business users | Curated tutorials, executive summaries, onboarding guides |

## Rules

1. **Prefer deep links** to canonical sources in odoo-ce over copying.
2. **Copy only when content is**:
   - Executive-facing, stable, and broadly reusable
   - Not tightly coupled to repo internals
   - Approved for the enterprise learning audience
3. **Any copied doc must be recorded** in `CURATED_DOCS.yaml` with:
   - Source URL/path
   - Reason for inclusion
   - Owner
   - Last sync date
4. **Bulk migration of odoo-ce docs into ipai-learn is prohibited**.

## Success Criteria

### SC-REL-01 — Clean hub integrity preserved
- No bulk import of `odoo-ce/docs/**` into `ipai-learn`.
- Any copied docs must be **selective** and recorded in a curation manifest.

### SC-REL-02 — Cross-reference mechanism available and preferred
- `ipai-learn` links to canonical sources in `odoo-ce` for deep technical docs.
- No duplication unless explicitly curated.

### SC-REL-03 — CI prevents "migration creep"
- CI fails if an import script is executed in CI or if large doc dumps are introduced.
- Threshold: >50 new markdown files in one PR triggers failure.

### SC-REL-04 — Minimal curated "enterprise pack" defined
- A named list of 3–10 docs eligible for import exists in `CURATED_DOCS.yaml`.
- Each entry includes rationale and source links.

## Features Shipped

### FS-0001 — `ipai-learn` positioned as a curated enterprise documentation hub
- `ipai-learn` is confirmed non-empty and purpose-built as a "Microsoft Learn–style" curated docs portal.
- Scope intentionally limited (curated set vs. full monorepo dump).
- Audience distinction documented: enterprise stakeholders vs. developer/operators.

### FS-0002 — Repository relationship documented and source-of-truth boundaries defined
- Explicit "do not migrate the entire monorepo" guidance captured.
- Cross-reference mechanism preferred over duplication.

### FS-0003 — CI guardrail prevents bulk doc dumps
- Automated check fails PRs that introduce >50 new markdown files.
- Protects curated hub from accidental migration creep.

## Exceptions Process

To add docs beyond the curated manifest:
1. Open a PR with the specific docs to add
2. Update `CURATED_DOCS.yaml` with rationale
3. Ensure PR passes the guardrail check (or request explicit review if >50 files)
4. Get approval from a docs maintainer

## Related Documents

- `docs/curation/CURATED_DOCS.yaml` - Manifest of curated documents
- `scripts/ci/guardrail_no_bulk_doc_dump.sh` - CI guardrail script
