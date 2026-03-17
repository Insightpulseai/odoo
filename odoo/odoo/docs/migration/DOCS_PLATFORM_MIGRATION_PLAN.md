# Docs platform migration plan

Eight phases to move from the current state (docs scattered across repo, no build pipeline, no UI) to the four-plane target state.

## Phase 1: Inventory

**Description**: Audit all existing documentation artifacts. Classify each by its canonical surface in the four-plane model. Identify duplicates, orphans, and misplaced content.

**Inputs**:
- Current repo: 167 architecture docs, 27 contracts, 76 spec bundles
- Existing `docs/` directory tree
- `CLAUDE.md` and `docs/ai/*.md` reference files

**Outputs**:
- `docs/migration/inventory.yaml` — every artifact with path, type, target plane, migration action (move, merge, archive, delete)
- Duplicate report — artifacts that exist in multiple locations with differing content
- Orphan report — artifacts referenced by nothing

**Dependencies**: None. This phase has no prerequisites.

**Acceptance criteria**:
- Every file under `docs/`, `specs/`, `contracts/` is listed in the inventory
- Each entry has a `target_plane` (1-4) and `action` (move, merge, archive, delete)
- Duplicate count is documented with specific file pairs
- Inventory is reviewed and approved by docs team lead

## Phase 2: Content skeleton

**Description**: Create the `docs-site/content/` directory tree following the structure defined in `ODOO_DOCS_BUILD_BENCHMARK.md`. Populate with index pages only — no migrated content yet.

**Inputs**:
- Target content structure from `ODOO_DOCS_BUILD_BENCHMARK.md`
- Inventory from Phase 1 (determines which sections are needed)

**Outputs**:
- `docs-site/` directory with `content/`, `extensions/`, `static/`, `redirects/`, `tests/`, `templates/`
- Index pages (`index.md`) for each content section
- `mkdocs.yml` with nav structure matching the skeleton
- Frontmatter schema in `templates/frontmatter-schema.json`
- `requirements.txt` with MkDocs and plugin dependencies

**Dependencies**: Phase 1 (inventory determines section structure).

**Acceptance criteria**:
- `make build` succeeds with skeleton content (no broken links)
- `make serve` renders all index pages
- Nav structure in `mkdocs.yml` matches the content tree
- Frontmatter schema validates against all index pages

## Phase 3: Build pipeline

**Description**: Set up CI/CD for the docs build. Local build, test suite, PR preview deployments, production deployment on merge.

**Inputs**:
- `docs-site/` skeleton from Phase 2
- CI patterns from `ODOO_DOCS_BUILD_BENCHMARK.md`

**Outputs**:
- `Makefile` with `build`, `serve`, `test`, `clean` targets
- `.github/workflows/docs-build.yml` — CI workflow
- Link checker test in `tests/`
- Frontmatter linter in `tests/`
- Redirect validator in `tests/`
- Cross-plane link validator (checks `spec_ref` and `edit_uri` links)
- Staging deployment on PR (preview URL posted as PR comment)
- Production deployment on merge to `main`
- `versions.json` manifest for the version switcher

**Dependencies**: Phase 2 (build pipeline needs content skeleton to build).

**Acceptance criteria**:
- `make test` runs all validators and exits 0 on the skeleton
- CI workflow triggers on PRs touching `docs-site/`
- Preview URL is posted as a PR comment within 5 minutes of push
- Production deployment completes within 10 minutes of merge
- `versions.json` is generated and served at the docs root
- Broken internal links fail the build

## Phase 4: Fluent 2 UI

**Description**: Build the docs product UI as a Fluent 2 React v9 application. This is Plane 3 — the user experience layer that consumes Plane 2 build output.

**Inputs**:
- `FLUENT2_DOCS_UI_SYSTEM.md` (design spec)
- `fluent-docs-component-map.md` (component mapping)
- Build output from Phase 3 (static HTML/JSON to render)

**Outputs**:
- React app with `FluentProvider`, `webLightTheme`, `webDarkTheme`
- App shell: global header, left nav (Tree), main content pane, right TOC/metadata pane
- Search overlay (SearchBox + Dialog) with `Ctrl+K` / `Cmd+K`
- Version switcher (Dropdown reading `versions.json`)
- Settings dialog (theme, density, accessibility preferences)
- Responsive layout (drawer nav on mobile, collapsed right pane)
- Accessibility audit report (axe-core, WCAG 2.2 AA)

**Dependencies**: Phase 3 (UI needs build output to render content).

**Acceptance criteria**:
- App shell renders on Chrome, Firefox, Safari, Edge (latest 2 versions)
- axe-core reports 0 critical or serious violations
- Keyboard navigation works for all interactive elements
- Dark mode and high contrast mode render correctly
- Search returns results within 200ms for the full content corpus
- Lighthouse accessibility score >= 95

## Phase 5: Plane workspace

**Description**: Structure the Plane self-hosted instance for docs operations. Define the link model between Plane work items and repo/published artifacts.

**Inputs**:
- Plane instance (already deployed at `plane.insightpulseai.com`)
- Inventory from Phase 1 (determines Plane module structure)
- Linking model from `DOCS_PLATFORM_TARGET_STATE.md`

**Outputs**:
- Plane project for docs platform operations
- Modules: Architecture, Content, UI, Infrastructure, Migration
- Custom properties on issues: `spec_bundle` (URL), `published_url` (URL), `repo_path` (string)
- Labels: `plane:docs`, `plane:content`, `plane:ui`, `plane:infra`
- Cycle template for docs releases
- Runbook template for content reviews

**Dependencies**: None for Plane setup. Phase 1 inventory informs module structure.

**Acceptance criteria**:
- Plane project exists with all defined modules
- Custom properties are configured and usable on issues
- At least one cycle is created using the template
- A sample issue demonstrates the full link model (spec_bundle → repo PR → published URL)

## Phase 6: Content migration

**Description**: Move content from its current location to the correct canonical surface. Create redirects for moved content. Archive duplicates.

**Inputs**:
- Inventory from Phase 1 (migration actions per artifact)
- Content skeleton from Phase 2 (target locations)
- Build pipeline from Phase 3 (validates migrated content)

**Outputs**:
- Content moved to `docs-site/content/` per inventory plan
- Redirects added to `redirects/` for every moved URL
- Archived content moved to `docs/archive/` with a deprecation notice
- Deleted duplicates (after confirming the canonical copy is correct)
- Updated cross-references in all remaining docs
- Migration log: `docs/migration/migration-log.yaml` with per-file status

**Dependencies**: Phases 1, 2, 3 (inventory, skeleton, and pipeline must be ready).

**Acceptance criteria**:
- `make test` passes after all content is migrated (no broken links)
- Every moved file has a redirect entry
- No content exists in more than one canonical location
- Migration log accounts for every file in the Phase 1 inventory
- Archived content is clearly marked and not linked from active nav

## Phase 7: Governance

**Description**: Establish the operating model for the docs platform. Define who owns what, how content is reviewed, and what metadata is required.

**Inputs**:
- Four-plane architecture from `DOCS_PLATFORM_TARGET_STATE.md`
- Migrated content from Phase 6

**Outputs**:
- Ownership matrix: every content section has a named owner (team, not individual)
- Naming conventions document: file naming, directory naming, frontmatter field naming
- Required metadata: every page must have `title`, `description`, `owner`, `last_reviewed`, `status`
- Review cadence: quarterly review of all content sections. Stale pages (not reviewed in 6 months) are flagged.
- Contribution guide: how to add, update, or deprecate a page
- PR review checklist: what reviewers check on docs PRs

**Dependencies**: Phase 6 (governance applies to migrated content).

**Acceptance criteria**:
- Ownership matrix covers 100% of content sections
- Frontmatter linter enforces required metadata on CI
- Contribution guide is published in the docs site itself
- At least one quarterly review cycle is scheduled in Plane
- PR review checklist is linked in the PR template

## Phase 8: Operationalize

**Description**: Enable the features that make the docs platform a production system: search indexing, version switcher, release notes workflow, and deprecation handling.

**Inputs**:
- Fluent 2 UI from Phase 4 (search overlay, version switcher)
- Build pipeline from Phase 3 (versioned output)
- Governance from Phase 7 (deprecation policy)

**Outputs**:
- Search index: full-text index built at build time, served as static JSON or via a lightweight API
- Version switcher: reads `versions.json`, renders in header, navigates to versioned paths
- Release notes workflow: template in `content/releases/`, linked from Plane cycles, announced via `MessageBar` in the UI for 30 days after release
- Deprecation handling: pages marked `status: deprecated` show a `MessageBar` banner with a link to the replacement. After 2 major versions, deprecated pages are archived.
- Archive handling: archived content is removed from nav and search index but remains accessible via direct URL with a banner
- Analytics: page view tracking (privacy-respecting, no third-party cookies) for identifying stale or unused content

**Dependencies**: Phases 3, 4, 7 (pipeline, UI, and governance must be in place).

**Acceptance criteria**:
- Search returns relevant results for 95% of a test query set (defined in `tests/search-queries.yaml`)
- Version switcher shows all published versions and navigates correctly
- A sample release note is published and visible in the UI with a `MessageBar`
- A sample deprecated page shows the deprecation banner and links to the replacement
- A sample archived page is inaccessible from nav and search but loads via direct URL with a banner
- Analytics dashboard shows page view data for the past 7 days

## Phase dependency graph

```
Phase 1 (Inventory)
  │
  ├──► Phase 2 (Content skeleton)
  │      │
  │      └──► Phase 3 (Build pipeline)
  │             │
  │             ├──► Phase 4 (Fluent 2 UI)
  │             │       │
  │             │       └──► Phase 8 (Operationalize)
  │             │               ▲
  │             └──► Phase 6 (Content migration)
  │                     │
  │                     └──► Phase 7 (Governance)
  │                             │
  │                             └──► Phase 8 (Operationalize)
  │
  └──► Phase 5 (Plane workspace) [independent]
```

Phases 1 and 5 can run in parallel. Phases 4 and 6 can run in parallel after Phase 3. Phase 8 waits for Phases 4, 6, and 7.
