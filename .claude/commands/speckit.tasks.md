---
description: Generate an actionable task breakdown from the implementation plan.
handoffs:
  - label: Analyze Consistency
    agent: speckit.analyze
    prompt: Check cross-artifact consistency
  - label: Execute Implementation
    agent: speckit.implement
    prompt: Execute all tasks to build the feature
scripts:
  sh: .specify/scripts/check-prerequisites.sh --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Run `{SCRIPT}`** from repo root and parse `FEATURE_DIR` and `AVAILABLE_DOCS`.

2. **Load context** (read in order):
   - `CLAUDE.md` — Project-level rules
   - `spec/<slug>/constitution.md` — Governance constraints
   - `spec/<slug>/prd.md` — Requirements (for traceability)
   - `spec/<slug>/plan.md` — Implementation plan (**required**)
   - `.specify/templates/tasks-template.md` — Template structure
   - `spec/<slug>/tasks.md` — Existing tasks (if updating)

3. **Parse the plan** and extract:
   - Components to build
   - File paths from source code layout
   - Dependencies between components
   - Complexity assessments
   - Architecture decisions

4. **Generate task breakdown** using the template structure:

   ### Task Format
   ```
   - [ ] T001 [P] [US1] Description — `path/to/file`
   ```
   - `T001` — Unique task ID
   - `[P]` — Parallelizable (can run concurrently)
   - `[US1]` — Linked user story from spec
   - File path — Exact path from repo root

   ### Phase Structure
   ```
   Phase 1: Setup          — Project scaffolding, config
   Phase 2: Foundational   — Data models, base services (blocks all else)
   Phase 3+: User Stories  — One phase per P1 story, then P2, then P3
   Phase N: Polish         — Docs, CI, final verification
   ```

   ### Requirements per phase
   - **Test-first**: Write tests FIRST, ensure they FAIL before implementing
   - **Checkpoints**: Each phase ends with a validation checkpoint
   - **Dependencies**: Define execution order explicitly
   - **File paths**: Every task references at least one file

5. **Write tasks** to `spec/<slug>/tasks.md`.

6. **Build dependency graph** at the bottom of the file:
   ```
   T001, T002 (parallel) → T003 → T004
   T004 → T005..T007 (US1)
   ```

7. **Build progress table**:
   ```
   | Phase | Total | Done | % |
   ```

## Rules

- Every task MUST have a unique ID (T001, T002, ...)
- Every task MUST reference at least one file path
- Every user story requirement MUST map to at least one task
- Tasks should be completable in a single focused session
- Do NOT include implementation code — just describe what to do
- Use absolute file paths from repo root
- Respect constitution constraints in task ordering

## Output

Report:
1. Total task count by phase
2. Parallelizable vs sequential ratio
3. User story coverage (any unmapped requirements?)
4. Estimated phase ordering

## Handoff

After tasks are created:
- **Next**: `/speckit.analyze` to check cross-artifact consistency
- **Then**: `/speckit.checklist` for quality validation
- **Finally**: `/speckit.implement` to execute
