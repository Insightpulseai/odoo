---
description: Deep Research Skill — Conduct exhaustive context gathering and output deterministic research artifacts.
---

# Deep Research Skill

You are executing the Deep Research Skill.

## Objective

Convert open-ended "deep research" requests into structured, deterministic outputs. Do not implement code changes during this phase. Your sole output is a set of research artifacts that comprehensively answer the user's questions or scope out an implementation plan.

## Triggers

- `/sc:research`
- "conduct deep research"
- "deep dive into"

## Hand-off Contract

Your research must produce a PRD-ready delta list or explicit spec patch recommendations that another agent (or the user) can immediately implement.

## Required Outputs

Every Deep Research run MUST produce the following artifacts in the relevant specification or workspace directory (e.g. `spec/<feature>/`):

1. **`research.md`**: The primary research document containing technical findings, architectural constraints, and recommendations.
2. **`sources.md`** (or inline citations within `research.md`): Explicit citations to the precise internal files viewed, tools used, or external documents accessed to produce the research.
3. **`findings.json`**: A machine-readable summary of the key findings, open questions, and confidence levels.

## Guardrails (Strict Enforcement)

- **No invented facts**: Do not hallucinate repository internals or Odoo behaviors.
- **Cite sources**: Every claim must be tied to an actual file examined or an external documentation run.
- **Explicit Assumptions**: You MUST include an "Assumptions & Open Questions" section detailing what could not be verified and what decisions are pending user input.
- **Scope Limit**: Stop once the research phase is complete. DO NOT attempt to write application code.

## Execution Procedure

1. Receive input scope, question, and context.
2. Formulate a search plan utilizing exact-text `grep_search`, local semantic queries, or file inspection (`view_file`, `view_code_item`).
3. Compile findings into memory.
4. Draft the structured outputs (`research.md`, `sources.md`, `findings.json`).
5. Terminate and hand execution back to the user or orchestration agent with a summary of outputs.
