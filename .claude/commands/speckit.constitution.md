---
description: Create or update the constitution (governance principles) for a spec bundle.
handoffs:
  - label: Define Requirements
    agent: speckit.specify
    prompt: Define the product requirements for this feature
  - label: Create Plan
    agent: speckit.plan
    prompt: Create an implementation plan for this feature
scripts:
  sh: .specify/scripts/check-prerequisites.sh --paths-only --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/speckit.constitution` is either a feature slug or a description of the principles to create.

### Step 1: Identify the spec bundle

1. If the user provides a feature slug (e.g., `ipai-finance-ppm`), use `spec/<slug>/`.
2. If the user describes principles without a slug, ask for the feature slug first.
3. If `{SCRIPT}` was run, parse the JSON output for `FEATURE_DIR` and `FEATURE_SLUG`.

### Step 2: Load context

Read these files in order (skip any that don't exist):
1. `CLAUDE.md` — Project-level rules (**non-negotiable**, must be inherited)
2. `spec/agent/constitution.md` — Agent-level execution constraints
3. `.specify/templates/constitution-template.md` — Template scaffolding
4. `spec/<slug>/constitution.md` — Existing constitution (if updating)

### Step 3: Author the constitution

Using the template as scaffolding, produce a constitution that:

1. **Inherits project rules**: All rules from `CLAUDE.md` apply automatically. Do NOT duplicate them — reference them.
2. **Adds feature-specific principles**: Technology choices, compliance requirements, scope boundaries, performance targets.
3. **Defines enforcement mechanisms**: Every principle MUST have a concrete enforcement gate:
   - CI check (GitHub Actions workflow)
   - Test requirement (unit/integration)
   - Review criteria (PR checklist item)
   - Automated validation (linter, schema check)
4. **Includes constraints table**: Technology stack, compliance, deployment, dependencies.
5. **Defines amendment process**: How this constitution can be changed.

### Step 4: Write the file

1. Create `spec/<slug>/` directory if it doesn't exist.
2. Write the constitution to `spec/<slug>/constitution.md`.
3. If this is a new bundle, also copy blank templates for `prd.md`, `plan.md`, `tasks.md` from `.specify/templates/`.

### Step 5: Validate

- Verify the constitution does NOT contradict `CLAUDE.md`.
- Verify every principle has an enforcement mechanism.
- Verify no aspirational statements exist without gates.

## Rules

- **NEVER** contradict `CLAUDE.md` or `spec/agent/constitution.md`
- Every principle MUST have a concrete enforcement mechanism
- Do NOT include aspirational statements without enforcement
- Keep it under 150 lines — brevity is a virtue
- Use absolute file paths in all references
- Reference `CLAUDE.md` by section, don't copy its rules

## Output

Report:
1. File path written
2. Number of principles defined
3. Any conflicts detected with `CLAUDE.md`

## Handoff

After constitution is created:
- **Next**: `/speckit.specify` to define product requirements
- **Then**: `/speckit.plan` to create implementation plan
