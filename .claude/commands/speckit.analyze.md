---
description: Cross-artifact consistency and coverage analysis (read-only).
handoffs:
  - label: Generate Checklist
    agent: speckit.checklist
    prompt: Generate a quality checklist for this feature
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

This is a **READ-ONLY** operation. Do NOT modify any files.

1. **Run `{SCRIPT}`** and parse `FEATURE_DIR`.

2. **Load all artifacts**:
   - `spec/<slug>/constitution.md` — Governance
   - `spec/<slug>/prd.md` — Requirements
   - `spec/<slug>/plan.md` — Architecture
   - `spec/<slug>/tasks.md` — Task breakdown

   If any artifact is missing, report which ones are absent and abort gracefully.

3. **Analyze for these categories**:

   | Category | What to Detect |
   |----------|---------------|
   | **Duplications** | Redundant or near-duplicate requirements across artifacts |
   | **Ambiguities** | Vague terms without measurable criteria ("fast", "secure") |
   | **Underspecification** | Requirements/tasks missing acceptance criteria or file paths |
   | **Constitution conflicts** | Violations of non-negotiable principles |
   | **Coverage gaps** | Requirements with no tasks, or tasks with no requirements |
   | **Inconsistencies** | Terminology drift, conflicting directives, ordering issues |

4. **Generate findings table** (max 50 rows):

   | ID | Category | Severity | Location | Summary | Recommendation |
   |----|----------|----------|----------|---------|----------------|
   | F001 | [category] | CRITICAL/HIGH/MEDIUM/LOW | [file:section] | [issue] | [fix] |

5. **Generate coverage matrix**:

   | Requirement | Task IDs | Status |
   |-------------|----------|--------|
   | FR-001 | T005, T006 | Covered |
   | FR-002 | — | **GAP** |

6. **Severity definitions**:
   - **CRITICAL**: Constitution MUST violation, missing core artifact, zero-coverage blocking requirement
   - **HIGH**: Conflicting/duplicate requirement, untestable acceptance criterion
   - **MEDIUM**: Terminology drift, missing NFR coverage
   - **LOW**: Wording improvements, minor redundancy

7. **Report metrics**:
   - Total findings by severity
   - Coverage percentage (requirements with tasks / total requirements)
   - Constitution alignment score (PASS principles / total principles)

## Rules

- **NEVER** modify any files
- **NEVER** hallucinate missing sections
- **NEVER** apply remediation edits without explicit user approval
- Prioritize constitution principles as non-negotiable
- Report facts, not opinions

## Output

Display the analysis report. Recommend next actions:
- CRITICAL/HIGH findings → fix spec artifacts before implementing
- MEDIUM/LOW findings → proceed with awareness

## Handoff

After analysis:
- **If clean**: `/speckit.implement` to execute
- **If issues found**: Fix artifacts, then re-run `/speckit.analyze`
