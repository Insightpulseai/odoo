# Expense Cash Advance — Constitution

## Non-Negotiable Rules

1. **CE only.** Depends on `base`, `hr`, `hr_expense`, `account`, `mail`. No Enterprise modules.
2. **No SAP integration.** This is a first-party capability. No Concur API, no SAP connectivity.
3. **Accounting idempotency.** All journal entries use idempotency keys. Repeated postings with the same key are no-ops. Implementation: check for existing `account.move` with `ref` matching the idempotency key before creating.
4. **Approval before disbursement.** Cash advance release requires both manager approval and finance approval. No single-person release path.
5. **Receipt evidence required.** Every expense item over the policy threshold must have a receipt attachment. Missing receipt = policy violation flagged.
6. **OCR is bridge-first.** Receipt extraction runs via `ipai_expense_ocr` bridge, never as inline Python OCR. Extraction results include confidence scores.
7. **No EE code reuse.** Do not copy or depend on Odoo Enterprise expense modules.
8. **OCA first when available.** If `OCA/hr-expense` has a mature 19.0 module for advance clearing, adopt it. Do not reinvent what OCA already provides.
9. **Audit trail mandatory.** All state transitions logged via Odoo chatter (`mail.thread`). Approval decisions include approver + timestamp + reason.
10. **Secrets in env vars only.** OCR service credentials live in environment variables (Vercel/DO), never in Odoo DB or git.

---

## Extension Decision Policy (CE vs OCA vs addon vs Bridge)

Before building or extending any capability, follow this decision tree in order:

### A. Can Odoo CE configuration satisfy the requirement?
- Use `ir.config_parameter`, system settings, or built-in module options.
- **If yes** → Configure. No code needed. Document in `ssot/odoo/settings_catalog.yaml`.

### B. Does an OCA module exist for this capability?
- Search `OCA/*` repos and the OCA app store.
- **If yes and mature (19.0 port available)** → Adopt the OCA module. Pin version in `.gitmodules` or `requirements.txt`. Do not fork or vendor — use `_inherit` overrides if customization is needed.
- **If yes but no 19.0 port** → Mark `[NEEDS PORT]`. File an OCA issue or initiate a port. Use a temporary `ipai_*` shim if blocking, but plan to migrate when port lands.

### C. Is a custom Odoo addon the right approach?
- Only if A and B are exhausted.
- **Naming**: `ipai_<domain>_<feature>` (e.g. `ipai_hr_expense_liquidation`).
- **Must**: follow OCA quality standards (pre-commit, manifest, README, tests).
- **Must not**: duplicate functionality available in OCA.

### D. Does the capability require an external service?
- AI/ML inference, OCR, vector search, or any non-Odoo runtime.
- **If yes** → Bridge-first architecture. The Odoo addon (`ipai_*`) is a thin connector; heavy logic runs in the external service.
- **Bridge contract**: `contracts/tools/TOOL_SPEC_TEMPLATE.md` (preview → approval → commit; audit envelope; idempotency key).

### E. Tie-breakers
- **EE parity feature** → Prefer OCA path (even partial) over custom addon. Document gap in `ssot/parity/`.
- **AI/ML capability** → Always Bridge (Rule 6: OCR is bridge-first).
- **Accounting entries** → Always custom addon with idempotency (Rule 3).
- **Cross-domain integration** → Requires a contract doc per `ssot-platform.md` Rule 9.

### Required artifacts per path

| Path | Required artifact |
|------|-------------------|
| A (Config) | Settings entry in `ssot/odoo/settings_catalog.yaml` |
| B (OCA) | `.gitmodules` pin or `requirements.txt` entry |
| C (Custom addon) | `addons/ipai/ipai_<domain>_<feature>/` with manifest + tests |
| D (Bridge) | Tool spec in `contracts/tools/` + bridge entry in `ssot/bridges/catalog.yaml` |
| E (Parity) | Row in `ssot/parity/ee_to_oca_proof_matrix.yaml` |
