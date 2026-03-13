# Constitution — Odoo Copilot Marketplace

## Non-Negotiable Rules

1. **Odoo is the system of record.** The copilot reads from and writes to Odoo; it never replaces Odoo business logic.
2. **Three capability classes are distinct.** Informational, navigational, and transactional modes must remain separate in routing, permissions, and audit.
3. **Write actions require explicit confirmation.** No transactional action may execute without user confirmation and audit logging.
4. **Role-based access is inherited, not duplicated.** The copilot respects Odoo's existing permission model (access rights, record rules, company scope). It does not define its own parallel authorization.
5. **Secrets never transit in plaintext.** Auth tokens, API keys, and credentials follow the repo secrets policy (env vars, vault, never committed).
6. **Microsoft identity maps to Odoo users.** The identity bridge must resolve Microsoft 365 identity to an Odoo user before any data access.
7. **Grounded answers over hallucination.** Informational responses must cite Odoo data or approved knowledge sources; the system must not fabricate records or status.
8. **CE-only, no Enterprise dependency.** All Odoo-side code must run on Community Edition 19.0 without Enterprise modules.
9. **Module decision rubric applies.** Standard Odoo config first, OCA second, ipai_* only for genuine gaps (per docs/architecture/MODULE_DECISION_RUBRIC.md).
10. **Phased rollout is mandatory.** Phase 1 (read-only) must be stable before Phase 2 (transactional) ships.
