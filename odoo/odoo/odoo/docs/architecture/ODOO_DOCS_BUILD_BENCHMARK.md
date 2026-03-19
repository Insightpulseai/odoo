# Odoo docs build benchmark

## Purpose

The `odoo/documentation` repo is the benchmark for Plane 2 (content/build). This document defines what we adopt, what we skip, and the resulting target structure.

## What to copy

These patterns from `odoo/documentation` are proven at scale and directly applicable:

- **Content tree structure**: Nested directories mirroring product areas. Each directory has an index page. Leaf pages are standalone topics.
- **Build/test pipeline**: Single build command, CI-enforced. Tests validate internal links, RST/markdown syntax, redirects, and image references.
- **Versioning**: Branch-per-version for major releases, allowing parallel maintenance of multiple live versions.
- **Language/version switch**: Published output supports switching between versions and (optionally) languages from the UI.
- **Separation of concerns**: Redirects, static assets, tests, and extensions each get their own top-level directory. Content is not mixed with build tooling.

## What NOT to copy

- **Visual UI**: Odoo docs use a custom Sphinx theme tightly coupled to odoo.com. We use Fluent 2 (Plane 3).
- **Sphinx-specific patterns**: RST directives, Sphinx extensions, `conf.py` configuration. We use MkDocs with Markdown.
- **Odoo-specific extensions**: Domain-specific directives (`.. odoo:module::`, etc.) are not portable. We build our own MkDocs extensions where needed.
- **Monolith build**: Odoo docs build the entire corpus in one pass. We support incremental builds for faster iteration.

## Target content structure

```
docs-site/
├── content/           # All authored content (Markdown)
│   ├── architecture/  # Platform architecture docs
│   ├── guides/        # How-to guides
│   ├── reference/     # API, CLI, config reference
│   ├── modules/       # Per-module documentation
│   ├── operations/    # Deployment, monitoring, runbooks
│   └── releases/      # Release notes, changelogs
├── extensions/        # MkDocs plugins and custom extensions
├── static/            # Images, diagrams, downloadable assets
├── redirects/         # Redirect map (old URL → new URL)
├── tests/             # Content tests (link checker, linter, schema)
├── templates/         # Page templates and frontmatter schemas
├── mkdocs.yml         # MkDocs configuration
├── Makefile           # Build/test/serve commands
└── requirements.txt   # Python dependencies (mkdocs, plugins)
```

### Directory purposes

| Directory | Purpose | Owner | Canonical for |
|---|---|---|---|
| `content/` | All published prose content | Docs team | Topic pages, guides, references |
| `extensions/` | MkDocs plugins (custom admonitions, cross-refs, metadata) | Platform team | Build-time content transforms |
| `static/` | Binary assets referenced by content | Docs team | Images, diagrams, downloads |
| `redirects/` | URL redirect mappings | Docs team | Backward compatibility of published URLs |
| `tests/` | Validation scripts and test fixtures | Docs team + platform | Content quality gates |
| `templates/` | Page scaffolds, frontmatter JSON schemas | Docs team | Consistency of new pages |

## Build contract

| Operation | Command | Output |
|---|---|---|
| Local build | `make build` | `site/` directory with static HTML |
| Local serve | `make serve` | Dev server on `localhost:8000` with hot reload |
| Test | `make test` | Runs link checker, linter, frontmatter validator, redirect validator |
| CI workflow | `.github/workflows/docs-build.yml` | Builds, tests, deploys to staging on PR; deploys to prod on merge to `main` |
| Output directory | `site/` | Static HTML, CSS, JS, assets. Consumed by Plane 3 UI or served directly. |

### CI contract

Every PR touching `docs-site/` triggers:

1. `make build` — must succeed (exit 0).
2. `make test` — must succeed (exit 0).
3. Cross-plane link validation — all `spec_ref` and `edit_uri` links resolve.
4. Deploy preview — staging URL posted as PR comment.

Merge to `main` triggers production deployment.

## Versioning strategy

**Model**: Branch-per-version.

| Branch | Published path | Status |
|---|---|---|
| `docs/19.0` | `/19.0/` | Current |
| `docs/18.0` | `/18.0/` | Maintained |
| `docs/17.0` | `/17.0/` | Archived (read-only) |

The `main` branch tracks the latest version. Version branches are cut at each major Odoo release. Archived versions are still published but display a banner indicating they are no longer maintained.

The version switcher in Plane 3 reads a `versions.json` manifest that lists all published versions, their branch, and their status (current, maintained, archived).

## Published docs model

Build output from each version branch is deployed to a versioned path under the docs domain. The latest version is also served at the root path.

```
docs.insightpulseai.com/          → latest (19.0)
docs.insightpulseai.com/19.0/     → 19.0 build output
docs.insightpulseai.com/18.0/     → 18.0 build output
docs.insightpulseai.com/17.0/     → 17.0 build output (archived)
```

Deployment target: Azure Static Web Apps or Azure Blob Storage with CDN, behind Azure Front Door. The Plane 3 UI app shell wraps this content or serves alongside it, depending on the integration model chosen during Phase 4.
