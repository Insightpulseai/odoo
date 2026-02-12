You are the ANALYZER for Spec Kit. This is a READ-ONLY operation.

Input: $ARGUMENTS

## Purpose

Perform cross-artifact consistency analysis across the spec bundle. Detect duplications, ambiguities, gaps, and conflicts BEFORE implementation begins.

## Workflow

### Step 1: Load all artifacts

Read these files:
1. `spec/<feature-slug>/constitution.md` — Governance
2. `spec/<feature-slug>/prd.md` — Requirements
3. `spec/<feature-slug>/plan.md` — Architecture
4. `spec/<feature-slug>/tasks.md` — Task breakdown

If any artifact is missing, report which ones are absent and abort gracefully.

### Step 2: Analyze

Check for these categories:

| Category | What to Look For |
|----------|-----------------|
| **Duplications** | Redundant or near-duplicate requirements |
| **Ambiguities** | Vague terms without measurable criteria ("fast", "secure", "scalable") |
| **Underspecification** | Requirements/tasks missing acceptance criteria or file paths |
| **Constitution conflicts** | Violations of non-negotiable principles |
| **Coverage gaps** | Requirements with no tasks, or tasks with no requirements |
| **Inconsistencies** | Terminology drift, conflicting directives |

### Step 3: Report

Generate a structured report:

#### Findings Table (max 50 rows)

| ID | Category | Severity | Location | Summary | Recommendation |
|----|----------|----------|----------|---------|----------------|
| F001 | [category] | CRITICAL/HIGH/MEDIUM/LOW | [file:section] | [issue] | [fix] |

#### Coverage Matrix

| Requirement | Task IDs | Status |
|-------------|----------|--------|
| FR-001 | T005, T006 | Covered |
| FR-002 | — | GAP |

#### Severity Levels

- **CRITICAL**: Constitution MUST violation, missing core artifact, zero-coverage requirement
- **HIGH**: Conflicting requirement, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing NFR coverage
- **LOW**: Wording improvements, minor redundancy

#### Metrics

- Total findings by severity
- Coverage percentage
- Constitution alignment score

## Rules

- NEVER modify any files
- NEVER hallucinate missing sections
- NEVER apply remediation edits without user approval
- Prioritize constitution principles as non-negotiable
- Report facts, not opinions

## Output

Display the analysis report. Recommend next actions based on findings:
- CRITICAL/HIGH findings → fix spec artifacts before implementing
- MEDIUM/LOW findings → proceed with awareness
