# Docs Authority Boundaries

> Contract defining what lives where across the four documentation planes.
> Canonical reference: `ssot/docs/docs-platform-canonical-map.yaml`

---

## 1. Four-Plane Authority

| Plane | Owns | Must Never Contain |
|-------|------|--------------------|
| **Repo** (`Insightpulseai/odoo`) | Specs, SSOT YAMLs, contracts, architecture docs, code-adjacent references, templates, archive | Runbooks, meeting notes, planning coordination, authored tutorials |
| **Published Docs** (`docs.insightpulseai.com`) | Authored user/developer guides, versioned API references, tutorials, searchable knowledge base | Raw specs, SSOT manifests, planning docs, full copies of repo content |
| **Plane** (`plane.insightpulseai.com`) | Runbooks, planning docs, execution coordination, meeting notes, retrospectives | Canonical specs, architecture decisions, contracts, authored guides |
| **ADLS Lake** (`adls://ipai-lake`) | Analytical data, telemetry, audit logs, ETL artifacts | Documentation content, specs, planning docs |

---

## 2. Duplication Rules

- Canonical content lives in **exactly one** surface.
- **Summaries and links** to canonical content are allowed on any surface.
- **Full copies** of canonical content on a non-canonical surface are prohibited.
- Cross-references use stable paths or URLs, never inline duplication.

---

## 3. Repo-Only Artifacts

These artifacts live exclusively in the repo and are never published directly:

- Spec bundles (`spec/`)
- SSOT YAMLs (`ssot/`)
- Contracts (`docs/contracts/`)
- Machine-readable manifests (build configs, token files, canonical maps)
- Code-adjacent docs (`addons/*/README.md`, inline module docs)
- Templates (`docs/templates/`, `spec/**/templates/`)
- Archive (`archive/`)

---

## 4. Published-Docs-Only Artifacts

These artifacts live exclusively on the published docs site:

- Authored user and developer guides
- Versioned API references
- Tutorials and how-to content
- Searchable knowledge base articles
- Styled navigation and site structure (MkDocs config)

Published docs may **reference** repo source paths (e.g., "see `docs/architecture/ADLS_DESIGN.md`") but must not duplicate repo content verbatim.

---

## 5. Plane-Only Artifacts

These artifacts live exclusively in Plane workspaces:

- Operational runbooks (workspace: `ops`)
- Sprint/delivery planning documents
- Execution coordination (task assignments, status tracking)
- Meeting notes and retrospectives
- Incident post-mortems (draft phase; final versions may be published)

---

## 6. Mirroring Rules

| Direction | Allowed | Prohibited |
|-----------|---------|------------|
| Plane -> Repo | Summary cards linking to repo paths | Full copies of specs or contracts |
| Plane -> Published | Summary cards linking to published URLs | Full copies of guides or references |
| Repo -> Plane | Delivery plans mirrored as Plane issues (`spec/*/plan.md`) | Full spec bundles pasted into Plane |
| Repo -> Published | Source references cited by path | Raw YAML/contract files served as docs |
| Published -> Repo | Not applicable | Published guide content copied into repo |
| Published -> Plane | Linked from runbooks | Full guide content pasted into Plane |

---

## 7. Archive and Deletion Rules

| Event | Action |
|-------|--------|
| Content moves from repo to published docs | Old repo location gets `status: archive` tag and a pointer to the published URL |
| Content moves from Plane to repo | Old Plane item gets archived with link to repo path |
| Published page relocated | Old URL gets a redirect (301) in the MkDocs config |
| Stale duplicate detected | Owner notified; duplicate deleted after 30 days if not reclassified |
| Content deprecated | Moved to `archive/` (repo) or archived state (Plane); removed from published site |

---

## 8. Governance

- **Quarterly audit**: Cross-surface duplication review. Compare `docs-platform-canonical-map.yaml` against actual content locations.
- **Unclassified content**: Any document without a canonical surface assignment in the map is flagged for classification within 14 days.
- **Audit owner**: Platform team lead.
- **Audit output**: Updated canonical map + list of resolved/flagged items committed to `docs/evidence/<YYYYMMDD-HHMM>/docs-audit/`.
- **Escalation**: Unresolved classification after 30 days escalates to CTO.
