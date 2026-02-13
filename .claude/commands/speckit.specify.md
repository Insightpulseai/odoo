---
description: Create or update the feature specification (PRD) from a natural language description.
handoffs:
  - label: Clarify Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec
scripts:
  sh: .specify/scripts/check-prerequisites.sh --paths-only --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/speckit.specify` **is** the feature description. Given that description:

1. **Identify or create the spec bundle**:
   - If user provides a slug: use `spec/<slug>/`
   - If user describes a new feature: derive a slug (lowercase-hyphen, e.g., `ipai-finance-ppm`)
   - Create the directory if it doesn't exist
   - If `{SCRIPT}` was run, parse `FEATURE_DIR` and `FEATURE_SLUG` from output

2. **Load context**:
   - Read `CLAUDE.md` — project-level rules
   - Read `spec/<slug>/constitution.md` — governance constraints (if exists)
   - Read `.specify/templates/spec-template.md` — template structure
   - Read `spec/<slug>/prd.md` — existing spec (if updating)

3. **Parse the feature description**:
   - Extract: actors, actions, data entities, constraints
   - Identify scope boundaries (what's in, what's out)
   - Make informed guesses for unspecified details using domain knowledge
   - Mark with `[NEEDS CLARIFICATION: question]` only for critical decisions (max 3)

4. **Write the specification** to `spec/<slug>/prd.md` following the template:

   **Required sections** (must be completed):
   - **Overview**: 1-3 sentence summary
   - **Problem Alignment**: Problem statement, current state, pain points
   - **User Scenarios**: User stories with acceptance criteria (Given/When/Then)
   - **Functional Requirements**: Each with unique ID (FR-001), priority (P1/P2/P3), linked story
   - **Non-Functional Requirements**: Performance, security, accessibility
   - **Success Criteria**: Measurable, technology-agnostic outcomes
   - **Edge Cases & Error Scenarios**: Boundary conditions

   **Optional sections** (include when relevant):
   - Key Entities
   - Clarifications (populated by `/speckit.clarify`)

5. **Quality validation** after writing:

   For each item, verify:
   - [ ] No implementation details (languages, frameworks, APIs) in requirements
   - [ ] Focused on user value and business needs
   - [ ] All requirements are testable and unambiguous
   - [ ] Success criteria are measurable and technology-agnostic
   - [ ] Acceptance criteria use Given/When/Then format
   - [ ] Edge cases are identified
   - [ ] Scope is clearly bounded

   If items fail: update the spec and re-validate (max 3 iterations).

6. **Handle clarifications** if `[NEEDS CLARIFICATION]` markers remain (max 3):
   - Present each as a question with 2-3 concrete options
   - Wait for user response
   - Update spec with chosen answers

## Rules

- Focus on **WHAT** users need and **WHY** — avoid HOW
- Every requirement MUST have a unique ID (FR-001, NFR-001, etc.)
- Every user story MUST have acceptance criteria
- Do NOT include implementation details — that belongs in `plan.md`
- Validate against constitution before writing (if it exists)
- Maximum 3 `[NEEDS CLARIFICATION]` markers
- Use absolute file paths in all references
- Prefer informed defaults over asking: data retention, performance, error handling

## Output

Report:
1. File path written
2. User stories by priority (P1/P2/P3 counts)
3. Functional requirements count
4. Non-functional requirements count
5. Any `[NEEDS CLARIFICATION]` items remaining

## Handoff

After spec is created:
- **Next**: `/speckit.clarify` to resolve ambiguities (optional)
- **Then**: `/speckit.plan` to create implementation plan
