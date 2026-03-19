# Docs platform target state

## Why four planes

The docs platform separates into four planes to enforce a single rule: every artifact has exactly one canonical home. No content is duplicated across planes. Each plane has a distinct owner, toolchain, and deployment surface. Changes flow through linking, not copying.

Without this separation, documentation drifts. Specs diverge from published docs. UI changes break content contracts. Planning artifacts get embedded in repos where they rot. Four planes prevent all of this by making ownership explicit and boundaries enforceable.

## The four planes

### Plane 1: Repo SSOT

**Owner**: Git (code review process).
**Canonical for**: Machine-readable artifacts — spec bundles, YAML manifests, contracts, code-adjacent documentation.

Content in this plane lives alongside the code it describes. It changes through the same PR process as code. It is versioned by git, not by a docs build system. Examples: `specs/`, `contracts/`, `CLAUDE.md`, module `__manifest__.py` metadata, CI workflow docs.

This plane never contains prose meant for end-user consumption. If a spec needs a human-readable published form, Plane 2 links to and renders from Plane 1 artifacts.

### Plane 2: Docs content/build

**Owner**: Docs team.
**Canonical for**: Published documentation — guides, references, tutorials, API docs, changelogs.

This plane follows the structure benchmarked from `odoo/documentation` (see `ODOO_DOCS_BUILD_BENCHMARK.md`). It contains content source files, build configuration, extensions, static assets, redirects, and tests. MkDocs builds the output. CI validates and deploys.

Content here is authored for humans. It references Plane 1 artifacts by link, never by copy.

### Plane 3: Docs product UI

**Owner**: Platform team.
**Canonical for**: User experience — navigation, search, version switching, accessibility, visual presentation.

This plane is a Fluent 2 React v9 application shell (see `FLUENT2_DOCS_UI_SYSTEM.md`). It consumes Plane 2 build output and renders it. The UI owns layout, navigation, search indexing, theming, and interactive surfaces. It does not own content.

### Plane 4: Human workspace

**Owner**: All teams.
**Canonical for**: Planning, runbooks, execution coordination, work tracking.

Plane self-hosted. Issues, cycles, modules, and views live here. Runbooks that coordinate cross-team work live here. This plane links to Plane 1 specs and Plane 2 published docs but never duplicates their content.

## Authority boundaries

| Artifact type | Canonical plane | Must never be duplicated in |
|---|---|---|
| Spec bundles (YAML, contracts) | Plane 1: Repo | Plane 2, 4 |
| Module manifests, code docs | Plane 1: Repo | Plane 2, 3 |
| Published guides, references | Plane 2: Content | Plane 1, 4 |
| Build config, extensions | Plane 2: Content | Plane 1, 3 |
| Static assets (images, diagrams) | Plane 2: Content | Plane 1 |
| App shell, nav, search UX | Plane 3: UI | Plane 2 |
| Theme tokens, layout components | Plane 3: UI | Plane 2 |
| Work items, cycles, roadmap | Plane 4: Workspace | Plane 1, 2 |
| Runbooks, execution checklists | Plane 4: Workspace | Plane 2 |
| Meeting notes, decisions | Plane 4: Workspace | Plane 1, 2 |

## Linking model

Planes reference each other through stable links, never through content duplication.

- **Repo → Published**: Spec bundles include a `published_url` field pointing to Plane 2 output. CI validates these links.
- **Published → Source**: Every published page includes a source link (`edit_uri`) pointing back to the Plane 2 content file, and optionally a `spec_ref` linking to the Plane 1 spec bundle.
- **Workspace → Repo/Published**: Plane work items reference repo PRs/commits by URL and published docs by URL. Plane modules map to repo directories.
- **Work item → Spec**: Each Plane issue that implements a spec includes a `spec_bundle` field linking to the Plane 1 YAML manifest path.

Links are validated by CI. Broken cross-plane links fail the build.

## Architecture diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCS PLATFORM                            │
│                                                             │
│  ┌──────────────┐    links     ┌──────────────────────┐     │
│  │  PLANE 1     │───────────►  │  PLANE 2             │     │
│  │  Repo SSOT   │  spec_ref    │  Content / Build     │     │
│  │              │◄─────────────│                      │     │
│  │  specs/      │  edit_uri    │  content/             │     │
│  │  contracts/  │              │  extensions/          │     │
│  │  manifests   │              │  static/              │     │
│  │              │              │  tests/               │     │
│  │  Owner: Git  │              │  Owner: Docs team     │     │
│  └──────┬───────┘              └──────────┬───────────┘     │
│         │                                 │                 │
│         │ PR/commit URLs                  │ build output    │
│         │                                 ▼                 │
│  ┌──────┴───────┐              ┌──────────────────────┐     │
│  │  PLANE 4     │   doc URLs   │  PLANE 3             │     │
│  │  Workspace   │◄────────────►│  Docs Product UI     │     │
│  │  (Plane)     │              │  (Fluent 2 React)    │     │
│  │              │              │                      │     │
│  │  issues      │              │  app shell           │     │
│  │  cycles      │              │  navigation          │     │
│  │  runbooks    │              │  search               │     │
│  │              │              │  version switcher     │     │
│  │  Owner: All  │              │  Owner: Platform      │     │
│  └──────────────┘              └──────────────────────┘     │
│                                                             │
│  ─────────── = canonical link (validated by CI)             │
│  ◄─────────► = bidirectional reference                      │
└─────────────────────────────────────────────────────────────┘
```

## Key constraints

1. Content is authored in exactly one plane. Other planes link to it.
2. CI validates all cross-plane links on every PR.
3. No plane embeds another plane's build artifacts in its source tree.
4. Plane 3 (UI) is stateless with respect to content. It renders Plane 2 output at request time.
5. Plane 4 (workspace) is ephemeral for execution artifacts. Decisions that affect architecture graduate to Plane 1 specs or Plane 2 published docs.
