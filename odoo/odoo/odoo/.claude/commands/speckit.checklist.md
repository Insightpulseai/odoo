---
description: Generate a quality validation checklist for a spec bundle.
handoffs:
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

1. **Run `{SCRIPT}`** and parse `FEATURE_DIR`.

2. **Load context**:
   - `spec/<slug>/prd.md` — Requirements
   - `spec/<slug>/plan.md` — Architecture
   - `spec/<slug>/tasks.md` — Task breakdown
   - `.specify/templates/checklist-template.md` — Template structure

3. **Generate checklist** covering these dimensions:

   | Dimension | Questions to Answer |
   |-----------|-------------------|
   | **Completeness** | Are all requirements addressed? Acceptance criteria defined? |
   | **Clarity** | Are terms unambiguous? Can requirements be independently verified? |
   | **Consistency** | Do artifacts agree? No terminology drift between spec/plan/tasks? |
   | **Coverage** | Every requirement has tasks? Every task has a requirement? |
   | **Measurability** | Are success criteria quantifiable? |
   | **Edge Cases** | Are error scenarios covered? Boundary conditions defined? |
   | **Constitutional Compliance** | Do all artifacts respect the constitution? |

4. **Each checklist item must**:
   - Have a unique ID (CHK001, CHK002, ...)
   - Reference the specific artifact section being validated
   - Be answerable as pass/fail
   - Be **specific to this feature** (no generic items)

5. **Write the checklist** to `spec/<slug>/checklist.md`.

6. **Run initial validation**: Review each item against the current artifacts.
   - Mark items that pass: `- [x] CHK001 ...`
   - Leave failing items unchecked: `- [ ] CHK002 ...`

7. **Build summary table**:
   ```
   | Dimension | Items | Passed | % |
   ```

## Rules

- Items must be SPECIFIC to this feature's artifacts
- Do NOT include generic boilerplate items
- Every item must reference a real section in a real artifact
- Keep items concise and actionable
- Include a summary table with pass percentages

## Output

Report:
1. File path written
2. Total items by dimension
3. Initial pass/fail counts
4. Overall readiness assessment

## Handoff

After checklist is generated:
- **If all pass**: `/speckit.implement` to execute
- **If failures**: Fix artifacts, re-run `/speckit.checklist`
