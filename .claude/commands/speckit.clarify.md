---
description: Resolve ambiguities and open questions in a specification before planning.
handoffs:
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

1. **Identify the spec bundle**:
   - Parse `FEATURE_DIR` from `{SCRIPT}` output, or use user-provided slug
   - Read `spec/<slug>/prd.md` (the specification to clarify)
   - Read `spec/<slug>/constitution.md` (governance constraints)

2. **Scan for ambiguities** in the specification:

   | Category | What to Look For |
   |----------|-----------------|
   | Vague terms | "fast", "secure", "scalable", "user-friendly", "efficient" |
   | Missing boundaries | Ranges, limits, thresholds not defined |
   | Undefined actors | Roles or personas not specified |
   | Implicit assumptions | Dependencies or prerequisites not stated |
   | Conflicting requirements | Items that contradict each other |
   | Missing error handling | What happens when things go wrong |
   | Untestable criteria | Acceptance criteria that can't be verified |

3. **Generate clarification questions** (maximum 10 per session):

   For each ambiguity, produce:

   ```markdown
   ## Question [N]: [Topic]

   **Location**: `spec/<slug>/prd.md` §[section]
   **Issue**: [What is ambiguous]

   | Option | Answer | Implications |
   |--------|--------|--------------|
   | A | [First option] | [Impact on feature] |
   | B | [Second option] | [Impact on feature] |
   | C | [Third option] | [Impact on feature] |

   **Recommended**: [Option letter] — [Why this is the default]
   ```

4. **Prioritize questions**: Blockers first, scope > security > UX > technical details.

5. **Wait for user responses** before modifying any files.

6. **Apply resolutions**:
   - If user provides answers: update `spec/<slug>/prd.md` with clarified requirements
   - Add a `## Clarifications` section at the bottom with Q&A log
   - Replace all `[NEEDS CLARIFICATION]` markers with resolved text

7. **If user defers**: Mark items as `[DEFERRED: reason]` in the spec.

## Rules

- Ask **specific** questions with **concrete options** — never open-ended
- Group related questions together
- Maximum 10 questions per session
- Do NOT change the spec without user input
- Prioritize: blockers first, nice-to-knows last
- Every question must reference a specific spec section

## Output

List all clarification questions with options. Wait for user input before modifying files.

## Handoff

After clarification:
- **Next**: `/speckit.plan` to create implementation plan
