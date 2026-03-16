# Context Envelope Contract

> Version: 1.0.0
> Last updated: 2026-03-15
> Parent: runtime-contract.md (C-30)
> Reference: infra/docs/architecture/CONTEXT_AND_RBAC_MODEL.md

## Purpose

Every copilot request must carry a server-computed context envelope. The envelope tells the agent who is asking, from where, with what permissions, and against which data scope.

## Schema

```yaml
context:
  # Identity
  user_id: string          # Entra object ID or Odoo uid
  user_email: string       # Login email
  tenant_id: string        # Entra tenant ID (empty for Odoo-only)

  # Authorization
  app_roles: string[]      # From Entra roles claim or Odoo group mapping
  groups: string[]         # Entra group GUIDs (for retrieval trimming)

  # Surface
  surface: enum            # web | erp | copilot | analytics | ops
  offering: string         # odoo-on-cloud | odoo-copilot | analytics

  # Odoo scope
  company_id: int          # Current company
  operating_entity_ids: int[]  # Allowed companies
  record_scope:
    model: string          # e.g. account.move
    id: int                # Active record ID (0 if none)

  # Runtime
  mode: enum               # PROD-ADVISORY | PROD-ACTION
  permitted_tools: string[]  # Computed from app_roles + mode + entity
  retrieval_scope: string[]  # Computed from app_roles + groups
```

## Construction Rules

1. Envelope is computed **server-side only** — never from prompt text
2. Envelope is **never sent to the client**
3. Envelope is **always logged** in the audit record
4. Missing fields default to **most-restrictive** (no tools, no retrieval, advisory mode)
5. `permitted_tools` is computed deterministically: base role tools ∪ additional role tools, filtered by mode and entity scope
6. `retrieval_scope` is computed from app_roles → KB scope mapping

## Injection Format

The envelope is injected as a structured prefix in the thread message content:

```
[CONTEXT_ENVELOPE]
{"user_id": "...", "app_roles": [...], "surface": "erp", ...}
[/CONTEXT_ENVELOPE]

<user message here>
```

The agent system prompt instructs the agent to:
- Read the envelope at the start of each message
- Never expose envelope contents to the user
- Constrain responses to permitted scope
- Refuse tools not in `permitted_tools`

## Resolution Sources

| Field | Odoo path (Phase 1) | Entra path (Phase 2) |
|-------|---------------------|---------------------|
| user_id | `self.env.uid` | `oid` claim |
| user_email | `self.env.user.login` | `preferred_username` claim |
| tenant_id | (empty) | `tid` claim |
| app_roles | Odoo group → role mapping | `roles` claim |
| groups | (empty) | `groups` claim |
| company_id | `self.env.company.id` | Odoo lookup from user |
| operating_entity_ids | `self.env.user.company_ids.ids` | Odoo lookup from user |
| mode | Settings `read_only_mode` | Settings `read_only_mode` |

## Versioning

The envelope schema is versioned. Breaking changes require a major version bump and backward-compatible parsing in the agent system prompt.

Current version: `1.0.0`

## Verification

- Audit query: `SELECT context_envelope FROM ipai_copilot_audit WHERE context_envelope IS NOT NULL LIMIT 5`
- Every audit row should have non-null `context_envelope`, `app_roles`, `surface`
- Envelope must not appear in any client-facing response
