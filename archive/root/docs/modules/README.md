# Catalog — Vercel & Supabase Examples, Templates, UI

This directory is the **SSOT for all Vercel and Supabase first-party resources** used in
or evaluated for this monorepo.

## Why a catalog?

Templates, examples, and UI components are not tribal knowledge.
Each item is **catalogued** (machine-readable JSON), **indexed** (human-readable INDEX.md),
and **blueprinted** (agent-executable runbooks in `blueprints/`).

The catalog answers three questions per resource:
1. **Should we use it?** (`status`: approved / candidate / deprecated)
2. **What exactly do we copy?** (`what_to_lift` field)
3. **How do we apply it?** → Blueprint YAML → generated runbook → `apply_blueprint.py <id>`

---

## Structure

```
docs/catalog/
├── README.md                          ← this file
├── SOURCES.md                         ← source repo URLs + scope
├── INDEX.md                           ← generated human index (do not edit directly)
│
├── vercel.examples.catalog.json       ← github.com/vercel/next.js/tree/main/examples
├── vercel.templates.catalog.json      ← vercel.com/templates
├── supabase.examples.catalog.json     ← github.com/supabase/supabase/tree/main/examples
├── supabase.ui.catalog.json           ← Supabase UI Library + Platform Kit
│
└── blueprints/                        ← ready-build/deploy YAML blueprints
    ├── schema.json                    ← blueprint schema definition
    ├── *.blueprint.yaml               ← one blueprint per deployable scenario
    └── generated/                     ← generated runbooks (do not edit directly)
        └── *.md
```

---

## JSON catalog schema

Each catalog file uses this schema (see `SOURCES.md` for source URLs):

```json
{
  "version": 1,
  "source": {
    "provider": "vercel|supabase",
    "type": "examples|templates|ui|platform-kit",
    "base_url": "https://..."
  },
  "items": [
    {
      "id": "unique-slug",
      "title": "Human title",
      "url": "https://...",
      "tags": ["nextjs", "auth", "monorepo", ...],
      "use_cases": ["ops-console", "multi-tenant", "ai-agents", "observability", "marketing", "platform-kit"],
      "adoption_level": "reference|harvest|adopt",
      "what_to_lift": ["exact file or feature slice"],
      "risk": "low|medium|high",
      "license_notes": "MIT / Apache-2.0 / etc.",
      "owner": "team or person",
      "status": "candidate|approved|deprecated",
      "last_reviewed": "YYYY-MM-DD"
    }
  ]
}
```

**`adoption_level` meanings**:
- `reference` — read and understand; don't copy yet
- `harvest` — copy minimal slices (the `what_to_lift` list) into our codebase
- `adopt` — full component/library is a first-class dependency

---

## How to add a catalog item

1. Open the appropriate `*.catalog.json`
2. Add a new entry to `items[]` following the schema above
3. Run `python3 scripts/catalog/validate_catalogs.py` — must exit 0
4. Run `python3 scripts/catalog/build_index.py` — regenerates `INDEX.md`
5. Commit both files; CI will enforce consistency

---

## How to apply a blueprint

```bash
# List available blueprints
python3 scripts/catalog/apply_blueprint.py --list

# Generate agent relay prompt for a blueprint
python3 scripts/catalog/apply_blueprint.py ops-console-dashboard

# With environment variables pre-filled
python3 scripts/catalog/apply_blueprint.py ops-console-dashboard --env-file .blueprint.env
```

`apply_blueprint.py` outputs an **Agent Relay Template** — a single prompt you paste into
Claude Code (or any agent) to scaffold the blueprint into the monorepo.

---

## CI gates

| Workflow | What it enforces |
|----------|-----------------|
| `catalog-gate.yml` | Catalogs validate + INDEX.md matches generated output |
| `blueprint-gate.yml` | Blueprints validate + generated docs match YAML source |

Both workflows fail with a clear diff if any generated file is out of date.
