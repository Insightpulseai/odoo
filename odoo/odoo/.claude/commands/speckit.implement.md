---
description: Execute the implementation plan by processing all tasks defined in tasks.md.
scripts:
  sh: .specify/scripts/check-prerequisites.sh --json --require-tasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Run `{SCRIPT}`** from repo root and parse `FEATURE_DIR` and `AVAILABLE_DOCS`.
   All paths must be absolute.

2. **Check checklists status** (if `spec/<slug>/checklist.md` exists):
   - Count total items, completed `[x]`, and incomplete `[ ]`
   - If any incomplete:
     - Display status table
     - Ask: "Some checklist items are incomplete. Proceed anyway? (yes/no)"
     - Wait for user response before continuing
   - If all complete: proceed automatically

3. **Load implementation context**:
   - **REQUIRED**: Read `spec/<slug>/tasks.md` — task list and execution plan
   - **REQUIRED**: Read `spec/<slug>/plan.md` — tech stack, architecture, file structure
   - **REQUIRED**: Read `spec/<slug>/constitution.md` — governance constraints
   - **IF EXISTS**: Read `spec/<slug>/prd.md` — requirements for validation
   - **IF EXISTS**: Read `spec/<slug>/research.md` — technical decisions and constraints

4. **Parse tasks.md** and extract:
   - Task phases (Setup → Foundational → User Stories → Polish)
   - Task dependencies (sequential vs parallel `[P]`)
   - Task details: ID, description, file paths
   - Execution order from dependency graph

5. **Execute implementation phase by phase**:

   For each phase:
   a. **Announce**: "Starting Phase N: [Name]"
   b. **Execute tasks** in dependency order:
      - Sequential tasks: complete one before starting next
      - Parallel tasks `[P]`: can be executed together
      - For each task:
        1. Read the task description and target file paths
        2. Implement the change following `plan.md` architecture
        3. Follow existing code patterns and style
        4. Mark task complete: `- [x] T001 ...` in `tasks.md`
   c. **Checkpoint**: At phase end, run verification commands from `plan.md`
   d. If checkpoint fails: fix before proceeding to next phase

6. **Implementation rules**:
   - Make the SMALLEST changes that satisfy each task
   - Follow TDD: write tests first if tasks specify test files
   - Prefer editing existing files over creating new ones
   - Follow `Config → OCA → Delta (ipai_*)` for Odoo modules
   - Keep diffs minimal and reviewable
   - Do NOT skip phases or checkpoints
   - Do NOT deviate from the plan without documenting why

7. **Progress tracking**:
   - Update `tasks.md` as tasks complete (mark `[x]`)
   - Update the progress table at the bottom
   - Report progress after each completed phase
   - Halt on non-parallel task failure (report error with context)

8. **Final verification**:
   ```bash
   ./scripts/repo_health.sh
   ./scripts/spec_validate.sh
   ./scripts/check-spec-kit.sh
   ```

9. **Completion report**:

   ### Change Summary
   Brief description of what was implemented.

   ### Files Touched
   | File | Change Type | Lines Changed |
   |------|-------------|---------------|
   | path/to/file | created/modified | +X / -Y |

   ### Verification Evidence
   - [ ] `repo_health.sh` passes
   - [ ] `spec_validate.sh` passes
   - [ ] `check-spec-kit.sh` passes
   - [ ] Tests pass (if applicable)

   ### Commit Message (Draft)
   ```
   feat(scope): short description

   - bullet point 1
   - bullet point 2

   Spec: spec/<slug>/prd.md
   ```

## Rules

- Follow `tasks.md` ordering — respect dependencies
- Make the SMALLEST changes that satisfy each task
- Write tests FIRST (test-first development per tasks.md)
- Do NOT skip phases or checkpoints
- Do NOT deviate from the plan without documenting why
- Update `tasks.md` progress as you complete each task
- Follow existing code patterns and style
- Keep diffs minimal and reviewable
- Prefer editing existing files over creating new ones
- For Odoo: every task produces (1) module changes, (2) install/update script, (3) health check

## Handoff

After implementation:
- Run verification commands
- Commit with OCA-style message
- Push to feature branch
