# Docs platform constitution

> 10 immutable rules. Violations block merge.

## 1. Four planes are distinct

The repo SSOT plane, docs content/build plane, docs product UI plane, and human-operable workspace plane are architecturally separate. Never collapse two planes into one system, one repo, or one deploy target.

## 2. Repo is machine-readable SSOT

Spec bundles, contracts, YAML manifests, and schema definitions live in the git repo only. The repo is the single source of truth for all machine-readable artifacts. No other plane may originate canonical structured data.

## 3. Odoo documentation repo is content/build benchmark only

The `odoo/documentation` repo informs content structure, build tooling, extension patterns, and editorial standards. It is not a UI benchmark. Do not copy its theme, navigation, or frontend patterns.

## 4. Fluent 2 is UI/design benchmark only

Microsoft Fluent 2 (React v9) defines the app shell, navigation, design tokens, component library, and interaction patterns. It is not a publishing or content-authoring benchmark. Content rendering uses a separate renderer inside the Fluent shell.

## 5. Plane is human-operable surface only

Plane self-hosted provides planning boards, runbooks, wiki pages, and execution coordination for humans. It is not a machine-readable SSOT. Plane content that needs machine-readability must be mirrored back to repo as structured artifacts.

## 6. No duplicate sources of truth

Every piece of canonical content has exactly one home. Other planes may display summaries or links, never full copies. When content must appear in multiple planes, one plane is canonical and others reference it.

## 7. Deterministic builds

Running `make html` or `mkdocs build` locally must produce byte-identical output to CI. No network calls during build. No runtime content fetching. All content is static at build time.

## 8. Content and chrome are separated

The Fluent app shell owns the header, left navigation, actions toolbar, search overlay, and theme switching. The content renderer owns prose, code blocks, diagrams, admonitions, and metadata display. These two systems communicate via a defined interface, never by reaching into each other's DOM.

## 9. Every doc category has exactly one canonical surface

Each of the 14 documentation categories is assigned one canonical surface: repo (specs, contracts), published site (architecture, runbooks, guides), or Plane (plans, execution tracking). No category spans two canonical surfaces.

## 10. Accessibility is non-negotiable

WCAG 2.2 AA minimum for all published content and the Fluent app shell. Fluent's built-in accessible patterns (focus management, aria attributes, keyboard navigation, high contrast) are enforced, not optional. Color contrast, heading hierarchy, and alt text are CI-gated.
