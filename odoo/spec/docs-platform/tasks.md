# Docs platform tasks

## T1: Inventory

- [x] T1.1: Audit all files under `docs/` — count, classify, identify duplicates
- [x] T1.2: Build initial MkDocs site with 44 pages from existing content
- [x] T1.3: Verify local `mkdocs build` produces working output
- [ ] T1.4: Generate `docs-inventory.yaml` manifest with category assignments for all 270+ docs
- [ ] T1.5: Produce duplicate report — identify content that exists in multiple locations

## T2: Content skeleton

- [ ] T2.1: Create `docs-site/` directory tree per plan (content/, extensions/, static/, redirects/, tests/)
- [ ] T2.2: Create category subdirectories under `content/` for all 14 categories
- [ ] T2.3: Write `mkdocs.yml` with nav tree, theme config, and extension list
- [ ] T2.4: Write `Makefile` with `html`, `clean`, `serve`, and `linkcheck` targets
- [ ] T2.5: Create placeholder `index.md` for each category with title and description

## T3: Build pipeline

- [ ] T3.1: Configure MkDocs Material theme with InsightPulse branding
- [ ] T3.2: Write GitHub Actions workflow for CI build on push to main
- [ ] T3.3: Configure Azure Static Web Apps deployment target
- [ ] T3.4: Implement versioning strategy — tagged releases produce versioned snapshots
- [ ] T3.5: Verify deterministic build completes in < 5 seconds
- [ ] T3.6: Add link checker to CI pipeline

## T4: Fluent 2 UI system

- [ ] T4.1: Initialize React app with FluentProvider and design tokens
- [ ] T4.2: Build app shell layout — header, left nav, content pane, right TOC
- [ ] T4.3: Implement dark mode toggle with Fluent theme tokens
- [ ] T4.4: Build collapsible left nav tree from docs taxonomy
- [ ] T4.5: Build right-side TOC auto-generated from content headings
- [ ] T4.6: Build search overlay with full-text results preview
- [ ] T4.7: Add admin bar — edit-on-GitHub link, metadata display, last-updated
- [ ] T4.8: WCAG 2.2 AA audit of app shell components

## T5: Plane workspace

- [ ] T5.1: Create Plane workspace with projects per platform area
- [ ] T5.2: Define cycle structure aligned to delivery phases
- [ ] T5.3: Create wiki pages for operational runbooks
- [ ] T5.4: Add links from Plane issues to repo spec bundles
- [ ] T5.5: Document which content categories are Plane-native vs mirrored

## T6: Content migration

- [ ] T6.1: Move architecture docs to published site content tree
- [ ] T6.2: Move spec bundles to repo SSOT locations (confirm or restructure)
- [ ] T6.3: Move runbooks to published site
- [ ] T6.4: Move delivery plans to Plane
- [ ] T6.5: Create redirect map for all moved files
- [ ] T6.6: Archive duplicates to `docs/archive/` with deprecation headers
- [ ] T6.7: Verify zero broken internal links after migration

## T7: Governance

- [ ] T7.1: Define frontmatter schema (title, owner, created, updated, status)
- [ ] T7.2: Write CI lint to validate frontmatter on all docs
- [ ] T7.3: Assign owners to all 14 categories
- [ ] T7.4: Set up quarterly review cycle — flag stale docs after 90 days
- [ ] T7.5: Document naming conventions and archive/deletion rules

## T8: Operationalize

- [ ] T8.1: Integrate search indexing (Pagefind or Algolia DocSearch)
- [ ] T8.2: Build version switcher in app shell
- [ ] T8.3: Create release note automation from git tags
- [ ] T8.4: Add build status badge to repo README
- [ ] T8.5: Schedule weekly broken link check via GitHub Actions
