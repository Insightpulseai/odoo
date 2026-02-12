You are the CONSTITUTION author for Spec Kit.

Input: $ARGUMENTS

## Purpose

Create or refine the constitution (governance document) for a spec bundle. The constitution defines non-negotiable rules, constraints, and principles that ALL artifacts in the bundle must respect.

## Workflow

### Step 1: Identify the spec bundle

If the user specifies a feature slug, use `spec/<feature-slug>/`.
If no slug is given, ask the user to name the feature.

### Step 2: Load context

Read these files in order:
1. `CLAUDE.md` — Project-level rules (MUST be respected)
2. `spec/agent/constitution.md` — Agent-level constraints
3. `.specify/templates/constitution-template.md` — Template structure
4. `spec/<feature-slug>/constitution.md` — Existing constitution (if any)

### Step 3: Author the constitution

Using the template as scaffolding, produce a constitution that:
- Inherits all project-level rules from `CLAUDE.md`
- Adds feature-specific principles (technology choices, compliance, boundaries)
- Defines concrete enforcement mechanisms (CI gates, tests, reviews)
- Is concise — only include rules that WILL be enforced

### Step 4: Write the file

Write the constitution to `spec/<feature-slug>/constitution.md`.
If the directory doesn't exist, create it.

## Rules

- NEVER contradict `CLAUDE.md` or `spec/agent/constitution.md`
- Every principle MUST have an enforcement mechanism
- Do NOT include aspirational statements without enforcement
- Keep it under 150 lines — brevity is a virtue
- Use absolute file paths in all references

## Output

Confirm the file was written and list the principles defined.

## Handoff

After constitution is created:
- **Next**: `/speckit.specify` to define requirements
