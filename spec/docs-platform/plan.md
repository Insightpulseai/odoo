# Docs platform implementation plan

## Phase 1: Inventory

Audit all existing docs, specs, runbooks, and wiki content. Classify each artifact by canonical surface (repo, published site, or Plane). Produce a manifest YAML listing every document with its current location, target category, and migration action.

**Outputs:** `docs-inventory.yaml`, category assignment for all 270+ docs, duplicate report.

## Phase 2: Content skeleton

Create the docs content tree modeled after `odoo/documentation`:

```
docs-site/
  content/           # authored markdown/rst by category
    architecture/
    product-specs/
    runbooks/
    integrations/
    platform-azure/
    erp-odoo/
    data-platform/
    ai-agents/
    finance-compliance/
    governance/
    release-logs/
    templates/
  extensions/         # custom MkDocs/Sphinx extensions
  static/             # images, diagrams, fonts
  redirects/          # redirect map for moved content
  tests/              # build tests, link checks
  mkdocs.yml          # build config
  Makefile            # deterministic build entry point
```

**Outputs:** directory tree, `mkdocs.yml`, `Makefile`, placeholder index per category.

## Phase 3: Build pipeline

Set up deterministic local build with MkDocs (or Sphinx). Configure CI publishing via GitHub Actions to Azure Static Web Apps. Define versioning strategy: tagged releases produce versioned doc snapshots, `latest` always points to main.

**Outputs:** working `make html`, GitHub Actions workflow, version switcher config, build time < 5s verified.

## Phase 4: Fluent 2 UI system

Build the Fluent 2 React v9 app shell:

- **FluentProvider** with light/dark theme tokens
- **Header**: logo, breadcrumb, theme toggle, search trigger
- **Left nav**: collapsible tree matching 14 categories
- **Content pane**: rendered docs with heading anchors
- **Right TOC**: auto-generated from content headings
- **Search overlay**: full-text search with results preview
- **Admin bar**: edit-on-GitHub link, metadata display, last-updated timestamp

**Outputs:** app shell package, Storybook components, design token file, dark mode verified.

## Phase 5: Plane workspace

Create the Plane self-hosted workspace structure:

- Project per major platform area (ERP, Data, AI, Platform)
- Cycles aligned to delivery phases
- Wiki pages for runbooks and operational procedures
- Links back to repo spec bundles (not copies)
- Define which content is Plane-native (plans, execution tracking) vs mirrored (summaries linking to published site)

**Outputs:** Plane workspace configured, linking convention documented, wiki seed content.

## Phase 6: Content migration

Move canonical content to the correct surface per the taxonomy. Add redirects for moved files. Archive duplicates to `docs/archive/` with a deprecation header. Update all cross-references.

**Outputs:** all docs in canonical location, redirect map complete, zero broken links, archive tagged.

## Phase 7: Governance

Establish ownership, naming conventions, metadata requirements, review cadence, and archive/deletion rules:

- Every doc has an `owner` field in frontmatter
- Naming: `<category>/<slug>.md`, kebab-case
- Metadata: title, owner, created, updated, status (draft/published/archived)
- Review: quarterly review cycle, stale docs flagged after 90 days
- Deletion: archived docs retained 1 year, then prunable

**Outputs:** governance doc, frontmatter schema, CI lint for metadata, review schedule.

## Phase 8: Operationalize

- Search indexing (Pagefind or Algolia DocSearch)
- Version switcher in app shell
- Language support scaffold (future, not implemented)
- Release note automation from git tags and changelogs
- Monitoring: build status badge, broken link check on schedule

**Outputs:** search working, version switcher working, release note pipeline, monitoring dashboard.

## Dependency map

```
Phase 1 (Inventory)
  |
  v
Phase 2 (Content skeleton) -----> Phase 5 (Plane workspace)
  |                                   |
  v                                   |
Phase 3 (Build pipeline)              |
  |                                   |
  v                                   v
Phase 4 (Fluent 2 UI) ----------> Phase 6 (Content migration)
                                      |
                                      v
                                  Phase 7 (Governance)
                                      |
                                      v
                                  Phase 8 (Operationalize)
```

- Phases 2 and 5 can run in parallel after Phase 1.
- Phase 4 can run in parallel with Phase 5 after Phase 3.
- Phase 6 requires Phases 4 and 5 complete.
- Phases 7 and 8 are sequential after Phase 6.
