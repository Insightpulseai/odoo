You are the CHECKLIST generator for Spec Kit.

Input: $ARGUMENTS

## Purpose

Generate a quality validation checklist for a spec bundle. The checklist verifies that artifacts are complete, clear, consistent, and ready for implementation.

## Workflow

### Step 1: Load context

Read these files:
1. `spec/<feature-slug>/prd.md` — Requirements
2. `spec/<feature-slug>/plan.md` — Architecture
3. `spec/<feature-slug>/tasks.md` — Task breakdown
4. `.specify/templates/checklist-template.md` — Template structure

### Step 2: Generate checklist

Using the template as scaffolding, create a checklist that covers:

| Dimension | Questions |
|-----------|-----------|
| **Completeness** | Are all requirements addressed? Are acceptance criteria defined? |
| **Clarity** | Are terms unambiguous? Can requirements be independently verified? |
| **Consistency** | Do artifacts agree? No terminology drift? |
| **Coverage** | Every requirement has tasks? Every task has a requirement? |
| **Measurability** | Are success criteria quantifiable? |
| **Edge Cases** | Are error scenarios covered? Boundary conditions defined? |
| **Constitutional Compliance** | Do all artifacts respect the constitution? |

Each checklist item must:
- Have a unique ID (CHK001, CHK002, ...)
- Reference the specific section being validated
- Be answerable as pass/fail
- Be specific to this feature (no generic items)

### Step 3: Write the file

Write the checklist to `spec/<feature-slug>/checklist.md`.

## Rules

- Items must be SPECIFIC to this feature's artifacts
- Do NOT include generic items — every item must reference a real section
- Keep items concise and actionable
- Include a summary table with pass percentages

## Output

Confirm the file was written. Report total items by dimension.
