# Agent Library Prompt Pack (Odoo / Apps / Web)

What you get:

- prompts/agents/\*.md : role prompts with strict output contracts
- prompts/router/\*.md : router + dispatcher prompts
- router/agent_router.yaml : routing rules + tool policy
- router/router.ts : deterministic router implementation (no UI assumptions)
- schemas/\*_/_.yaml : reusable tax + compliance taxonomy, locale overlays, and mappings
- schemas/evidence/form_evidence_bundle.schema.json : form-level evidence bundle spec

Design choices:

- "Structured Outputs" style: require `additionalProperties:false`, strict keys, and deterministic sections
- Safety posture: isolate untrusted text, validate structured fields, and use evals/trace grading
