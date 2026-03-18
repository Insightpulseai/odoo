---
description: Create a technical implementation plan from the feature specification.
handoffs:
  - label: Generate Tasks
    agent: speckit.tasks
    prompt: Generate the task breakdown from the plan
  - label: Generate Checklist
    agent: speckit.checklist
    prompt: Generate a quality checklist for this feature
scripts:
  sh: .specify/scripts/setup-plan.sh --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).
The user input typically contains the **tech stack** and architecture choices.

## Outline

1. **Run `{SCRIPT}`** from repo root and parse output for `FEATURE_SPEC`, `IMPL_PLAN`, `SPECS_DIR`, `BRANCH`.
   All paths must be absolute.

2. **Load context** (read in order):
   - `CLAUDE.md` — Project-level rules
   - `spec/<slug>/constitution.md` — Governance constraints
   - `spec/<slug>/prd.md` — Feature requirements (the WHAT)
   - `.specify/templates/plan-template.md` — Template structure
   - `spec/<slug>/plan.md` — Existing plan (if updating)

3. **Phase 0: Research unknowns**

   Before planning, inspect the codebase to understand:
   - Existing patterns and conventions
   - Integration points and dependencies
   - Files that will be affected
   - Technical constraints from the stack

   If there are unresolved technical questions, write `spec/<slug>/research.md` with:
   - Questions investigated
   - Findings and evidence
   - Decisions made with rationale

4. **Phase 1: Design**

   Using the plan template, produce:

   a. **Summary**: Map every FR/NFR from the spec to a technical approach
   b. **Technical context**: Language/version, framework, database, testing, platform
   c. **Constitutional compliance**: Validate every constitution principle (PASS/FAIL)
   d. **Source code layout**: File structure with exact paths
   e. **Architecture decisions**: Each decision with justification and alternatives considered
   f. **Complexity assessment**: Per-component complexity (Low/Medium/High)
   g. **Risks and mitigations**: Identified risks with concrete mitigation strategies
   h. **Verification commands**: Exact commands to validate the implementation

   For Odoo modules specifically:
   - Follow `Config → OCA → Delta (ipai_*)` philosophy
   - Use `ipai_<domain>_<feature>` naming
   - Reference existing addons/ structure
   - Include install/update scripts

5. **Phase 2: Write the plan**

   Write to `spec/<slug>/plan.md`.

6. **Gate evaluation**: If any constitution principle is FAIL, stop and report the violation.

## Rules

- Do NOT implement. Do NOT edit source code files.
- Every architectural decision MUST have a justification
- Validate against constitution — flag any FAIL items
- Reference spec requirement IDs (FR-001, etc.) throughout
- Use absolute file paths in all references
- Prefer the simplest approach that satisfies all requirements
- For Odoo: prefer Config > OCA > ipai_* delta

## Output

Report:
1. Constitutional compliance (all PASS / any FAIL)
2. Complexity assessment summary
3. Key risks identified
4. File path written

## Handoff

After plan is created:
- **Next**: `/speckit.tasks` to generate task breakdown
- **Then**: `/speckit.checklist` for quality validation
- **Finally**: `/speckit.implement` to execute
