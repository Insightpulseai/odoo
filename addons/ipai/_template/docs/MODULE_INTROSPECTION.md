# Module Introspection

> **Purpose of this file.** Answer why this custom module exists at all.
> Required by `CLAUDE.md` §"Odoo extension and customization doctrine".
> Reviewed at code review. A missing or thin introspection is grounds to reject the module.

## Why this module exists

One-paragraph statement. What problem does it solve that is not already solved?

## Business problem

- Concrete business scenario
- Who is affected
- What breaks or is missing without this module
- Measurable outcome the module produces

## CE 18 coverage checked

Explicit list of Odoo CE 18 features/modules reviewed and why each was insufficient:

| CE feature/module | Reviewed? | Why insufficient |
|---|---|---|
| `<module>` | Yes | <reason> |

## Property-field assessment

**Could this requirement be satisfied by Odoo property fields on an existing parent-scoped record?**

- [ ] Yes — if yes, this module should be retired in favor of property fields.
- [ ] No — explain below why property fields are insufficient.

**Why property fields are insufficient** (if applicable):

- [ ] Requirement is not parent-scoped; needs global schema
- [ ] Requirement needs heavy server-side logic
- [ ] Requirement needs integration contracts
- [ ] Requirement needs reporting at DB level
- [ ] Requirement needs workflow-critical behavior
- [ ] Other: <specify>

## OCA 18 same-domain coverage checked

| OCA module | Repo | Reviewed? | Why insufficient |
|---|---|---|---|
| `<module>` | `OCA/<repo>` | Yes | <reason> |

## Adjacent OCA modules reviewed

Adjacent repos that might have solved this before it became custom:

| Adjacent OCA repo | Reviewed? | Relevant? |
|---|---|---|
| `OCA/<repo>` | Yes | No — <reason> |

## Why CE + property fields + OCA composition was insufficient

Explain why even combining steps 1-5 of the doctrine cannot meet this requirement.

## Why custom code is justified

The authoritative reason. Must survive code review challenge.

## Module type

- [ ] **Bridge** — thin connector between IPAI/external services and Odoo
- [ ] **Overlay** — small opinionated UX/workflow overlay on CE/OCA behavior
- [ ] **Adapter** — environment-specific adapter (PH BIR filing, Zoho SMTP, etc.)
- [ ] **Extension** — genuine domain extension where no OCA equivalent exists

## Functional boundaries

- **Does:** ...
- **Does NOT:** ...
- **Handoff to:** <list downstream modules/services/agents>

## Extension points used

| Technique | Target | Purpose |
|---|---|---|
| `_inherit` | `res.partner` | Add field X |
| View inheritance (XPath) | `res.partner.view_form` | Add tab Y |
| `ir.actions.server` | <name> | <purpose> |
| External API call | <endpoint> | <purpose> |

## Blast radius

- Models touched: ...
- Views modified: ...
- Other modules affected if this module fails: ...
- Recovery path: ...

## Upgrade risk

- Odoo version upgrades: <risk level and why>
- OCA dependency upgrades: <risk level and why>
- Breaking changes monitored via: <CI job | manual review>

## Owner

- Primary: ...
- Backup: ...
- Escalation path: ...

## Retirement / replacement criteria

This module should be retired or merged when:

- [ ] OCA ships an equivalent at <repo>
- [ ] Odoo CE adds native support in version X
- [ ] <other concrete trigger>

On retirement: <migration plan>
