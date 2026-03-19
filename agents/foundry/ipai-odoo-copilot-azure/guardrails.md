# IPAI Odoo Copilot — Guardrails

> Version: 1.0.0
> Last updated: 2026-03-14
> Parent: runtime-contract.md (C-30)

## Safety Guardrails

### G-1: No Unauthorized Actions

The copilot MUST NOT execute Odoo write operations unless:
- `read_only_mode` is explicitly disabled in Settings
- The user has confirmed the action (for `draft_only` mode)
- The action is within the copilot's declared tool contract

**Enforcement**: `foundry_service.py` checks `read_only_mode` before any write path.

### G-2: No PII in Responses

The copilot MUST NOT include personally identifiable information in responses unless:
- The requesting user has ACL access to the underlying Odoo record
- The PII is directly relevant to the user's query
- The response is scoped to the user's own data

**Enforcement**: Odoo ACL layer + Foundry system prompt instructions.

### G-3: No Unsupported Claims

The copilot MUST NOT:
- Claim it can execute transactions when in `read_only` mode
- Present draft data as confirmed/committed data
- Provide tax/legal advice without advisory disclaimer

**Enforcement**: System prompt + evaluation rubric (product eval category).

### G-4: Audit Trail

Every copilot interaction MUST produce an audit record containing:
- User identity
- Prompt text
- Response excerpt
- Environment mode
- Whether the request was blocked and why

**Enforcement**: `ipai.copilot.audit` model, written by `_write_audit()` in foundry_service.py.

### G-5: Rate Limiting

- Discuss bot: 2-second minimum between responses
- HTTP API: 10 requests/minute per authenticated user
- Docs widget: 10 requests/minute per IP

**Enforcement**: copilot_bot.py rate check, Express rate limiter, controller validation.

### G-6: Fallback Behavior

On any Foundry API failure:
- Return empty response (never hallucinate)
- Log the failure in audit with `blocked=True`
- Do not retry automatically (avoid amplifying failures)

**Enforcement**: try/except in chat_completion() with audit logging.

## Content Guardrails

### Scope Boundaries

The copilot is authorized to discuss:
- Odoo ERP operations (modules, records, workflows)
- Philippine tax compliance (BIR rules, filing deadlines)
- IPAI platform capabilities and documentation
- General business process guidance

The copilot must refuse to discuss:
- Topics unrelated to business/ERP operations
- Specific legal advice (must add advisory disclaimer)
- Internal system credentials or architecture details
- Other users' data without ACL verification

## Guardrail Testing

Each guardrail maps to evaluation test cases:

| Guardrail | Eval category | Min test cases |
|-----------|--------------|----------------|
| G-1 | actions | 20 |
| G-2 | safety | 15 |
| G-3 | product | 10 |
| G-4 | runtime | 5 |
| G-5 | runtime | 5 |
| G-6 | runtime | 5 |
