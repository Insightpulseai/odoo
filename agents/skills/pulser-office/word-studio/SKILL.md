# Word Studio

> Publishable-quality formal document generation from Odoo data and policies.

## Capability

Generate formal documents (DOCX/PDF) grounded in Odoo Documents vault,
approved policy indexes, approval artifacts, and Finance PPM context.

## Grounding sources

1. Odoo Documents — retained source files, evidence packs, approval artifacts
2. Approved policy and knowledge indexes
3. Finance PPM task / milestone / OKR context
4. Active Odoo record context

## Output types

| Type | Description | Example |
|------|-------------|---------|
| PRD / plan bundle | Formal spec and operating document | Feature PRD, implementation plan |
| Policy brief | Concise policy or procedure statement | Expense policy, close procedure |
| Close pack | Reviewer-ready procedural checklist | Month-end close evidence pack |
| Playbook | Operational runbook with steps | Collections playbook, BIR filing guide |
| Publishable brief | External-facing summary | Stakeholder brief, compliance summary |

## Quality gates

- [ ] Page render: clean pagination, no orphan headers
- [ ] Hierarchy: heading levels consistent, table of contents accurate
- [ ] Citations: all claims traced to source documents or Odoo records
- [ ] Signoff: reviewer and approver fields present where required
- [ ] Grounded: content backed by Documents vault or approved knowledge

## Publish gate

1. Content grounded in Odoo / Documents / approved knowledge.
2. Artifact renders cleanly with no overflow, overlap, or broken layout.
3. Reviewer notes resolved and retained copies stored in Odoo Documents.
4. Final output ready to circulate externally without reformatting.

## Dependencies

- `python-docx` — native DOCX generation
- `ipai_odoo_copilot` — Odoo context packaging
- Odoo Documents — retained copy storage and retrieval

## Phase

R1 Foundation → R2 Core → R3 Hardening
