# Org Doc Platform Admission Policy

> Rules for adding new documentation sources to the org-wide
> documentation platform index.

---

## Admission Rules

### Rule 1: Source Must Have a Clear Owner

Every doc source admitted to the index must have:
- A named owner (team or individual)
- Owner recorded in `source_inventory.yaml`
- Owner responsible for staleness and accuracy

Sources without an owner are rejected.

### Rule 2: Source Must Be in a Recognized Format

Accepted formats:
- Markdown (`.md`)
- reStructuredText (`.rst`)
- YAML (`.yaml`, `.yml`) -- for structured docs like contracts, configs
- Plain text (`.txt`) -- only for READMEs and changelogs

Rejected formats:
- Binary files (`.pdf`, `.docx`, `.pptx`) -- extract to markdown first
- Images (`.png`, `.jpg`) -- not searchable
- Compiled/minified files (`.min.js`, `.pyc`)

### Rule 3: Source Must Be Registered in source_inventory.yaml

Before indexing, add an entry to `source_inventory.yaml` with:

```yaml
- path: "docs/new-source/"
  owner: "Team Name"
  doc_type: engineering  # engineering | architecture | runbook | policy | spec
  sensitivity: internal  # public | internal | confidential
  format: markdown
  refresh_cadence: weekly
  added_date: "2026-03-15"
  notes: "Description of what this source covers"
```

### Rule 4: External Sources Require Explicit Approval

For docs hosted outside this repo (Azure docs, OCA wiki, vendor portals):
- Must have a `source.yaml` contract in `config/org-docs/sources/`
- Contract specifies URL, fetch method, rate limits, license terms
- Requires approval from platform owner
- Must not violate copyright or terms of service

### Rule 5: Generated/Derived Docs Must Not Be Indexed

Do not index:
- CI/CD output logs
- Build artifacts
- Auto-generated API docs (index the source instead)
- Evidence bundles (`docs/evidence/`) -- these are proof artifacts, not source docs
- Lock files (`oca.lock.json`, `package-lock.json`)
- Compiled schema files (index the DBML/YAML source)

**Rationale**: Indexing generated content creates duplication and staleness risk.
Index the source that generates the content instead.

### Rule 6: Evidence Bundles Are Excluded by Default

Files under `docs/evidence/` are execution proof, not reference documentation.
They are excluded from the index to avoid:
- Inflating index size with transient data
- Confusing search results with dated evidence
- Staleness (evidence is point-in-time by definition)

Exception: An evidence file may be indexed if it is explicitly registered
in `source_inventory.yaml` with `doc_type: evidence` and a clear reason.

---

## Admission Checklist

Before adding a new source, verify:

- [ ] Source has a named owner
- [ ] Source is in a recognized format (md, rst, yaml, txt)
- [ ] Entry added to `source_inventory.yaml`
- [ ] If external: `source.yaml` contract created and approved
- [ ] Source is not generated/derived content
- [ ] Source does not contain secrets or credentials
- [ ] Sensitivity level assigned (public, internal, confidential)
- [ ] Test: source loads successfully with the document loader

---

## Removal Policy

To remove a source from the index:

1. Mark as `deprecated: true` in `source_inventory.yaml`
2. On next refresh, deprecated source docs are excluded
3. After 30-day grace period, docs are purged from index
4. Remove the `source_inventory.yaml` entry
5. Commit with message: `chore(org-docs): remove <source> from index`

---

## Sensitivity Guidelines

| Level | Definition | Examples |
|-------|-----------|----------|
| `public` | Safe to expose externally | README, public API docs, architecture overviews |
| `internal` | Internal team use only | Runbooks, contracts, spec bundles, coding rules |
| `confidential` | Restricted access | Security policies, credential rotation procedures, audit findings |

When in doubt, classify as `internal`. The platform owner can reclassify.

---

## Conflict Resolution

If two sources provide conflicting information:
1. The more recently updated source takes precedence
2. If both are current, the source closer to `CLAUDE.md` in the SSOT hierarchy wins
3. Flag the conflict in the monthly eval review
4. Source owners must reconcile within one refresh cycle

---

*Created: 2026-03-15*
*Owner: Platform Engineering*
