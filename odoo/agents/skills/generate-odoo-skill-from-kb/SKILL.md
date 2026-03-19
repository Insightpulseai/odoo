# SKILL: Generate Procedural Skill From Odoo19 KB

## Skill ID

generate-odoo-skill-from-kb

## Skill Type

Procedural (Deterministic, Output-Generating)

## Risk Level

LOW

## Requires Approval

false

## Purpose

Generate a new procedural skill (SKILL.md + registry entry stub) grounded in the
vendored+pinned Odoo 19 KB. This converts “knowledge” (KB sections) into
“procedure” (deterministic steps).

Outputs are deterministic given the same inputs and pinned commit.

---

## Preconditions (MUST ALL BE TRUE)

1. KB pin verification passes
2. Index artifacts exist and are non-empty (orm/security/frontend/deployment)
3. Generator exists: `scripts/kb/generate_skill_from_kb.py`
4. Registry exists: `agents/registry/odoo_skills.yaml`

---

## Inputs

```yaml
skill_id: string                   # kebab-case, unique
title: string
kb_topics:                          # which index files/sections to ground on
  - orm
  - security
  - frontend
  - deployment
target_use_case: string             # e.g. "scaffold a minimal module"
tier: "local" | "remote"            # default routing hint (not enforcement)
guardrails:
  forbid_enterprise_modules: true|false
  prod_requires_staging_success: true|false
```

---

## Hard Rules

- ❌ Never cite unpinned upstream material
- ✅ Always embed KB pinned_commit in generated artifacts
- ✅ Always generate deterministic step ordering (no “maybe”)

---

## Execution Steps (ORDER IS MANDATORY)

### Step 1 — Evidence Folder

Create:
`docs/evidence/<YYYY-MM-DD>/kb/generate-skill/<run_id>/`

Write inputs.json + repo HEAD + kb pin snapshot.

---

### Step 2 — Verify KB Pin

Run:
`python3 scripts/kb/verify_odoo_docs_pin.py`

Fail on mismatch.

---

### Step 3 — Generate Skill Artifacts

Run:
`python3 scripts/kb/generate_skill_from_kb.py --skill-id <skill_id> --topics <csv> --out agents/skills/<skill_id>/SKILL.md`

Generator MUST produce:

- `agents/skills/<skill_id>/SKILL.md`
- Evidence copy at `docs/evidence/.../generated_SKILL.md`

Content requirements:

- Preconditions
- Inputs/Outputs schema
- Hard rules
- Deterministic steps
- Failure modes
- Allowed routing constraints
- `kb_pinned_commit: <sha>` embedded

---

### Step 4 — Generate Registry Stub

Generator MUST also emit:

- `agents/registry/stubs/<skill_id>.yaml`

With:

- id, title, version
- kb_pinned_commit
- guardrails
- default routing hint

---

### Step 5 — Validate Generated Artifacts

Run:
`python3 tests/test_skill_registry.py` (or a dedicated generator test if present)

Fail if:

- skill_id conflicts
- required headings missing
- kb_pinned_commit missing

---

### Step 6 — Evidence Outputs

Write:

- final_status.json
- checksums.txt for generated files

---

## Allowed LLM Routing

Local SLM allowed for:

- formatting SKILL.md text
- summarizing KB sections into step rationale

Remote model optional for:

- better natural-language phrasing only

The procedure structure is deterministic and must be enforced by generator.

---

## Postconditions

On success:

- New skill exists under agents/skills/<skill_id>/SKILL.md
- Registry stub exists
- Evidence exists
