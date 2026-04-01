# Pulser Odoo — Constitution

> Non-negotiable rules and constraints for the Pulser Odoo adapter layer.

---

## Invariants

1. **Odoo is adapter, not authority.** Odoo provides ERP context (Tier 6) and localization mapping (Tier 5), but never determines tax policy.
2. **Every tax action cites dual basis.** Any `ipai.pulser.tax_action_request` that modifies tax configuration must include both `legal_basis_ref` (Tier 1-2) and `execution_model_ref` (Tier 5).
3. **ERP records are Tier 6.** Account moves, journal entries, and partner records are internal transaction context — they never override BIR legal authority.
4. **Localization config is Tier 5.** Tax group mappings, fiscal position configs, and `l10n_ph` references are execution benchmarks — they describe HOW to implement, not WHAT the rules are.
5. **CE only.** No Enterprise module dependencies, no odoo.com IAP calls. OCA modules preferred over custom `ipai_*`.
6. **Read-only default.** `ipai.copilot.tool.executor` operates in `read_only_mode` unless explicitly overridden per-request with approval.
7. **Blocked models enforced.** The `_BLOCKED_MODELS` frozenset in tool_executor.py is non-negotiable — no agent may bypass it.
8. **Exception events are immutable.** Once an `ipai.pulser.tax_exception_event` is created, it cannot be deleted — only resolved with evidence.
9. **ATC codes use official BIR namespace.** All ATC codes must use the WI/WC/WB prefix per BIR RR 11-2018. Legacy W-series accepted for backward compatibility only.
10. **Module naming convention.** All Pulser-related Odoo modules use `ipai_pulser_*` prefix. Tax-specific modules use `ipai_bir_*` or `ipai_pulser_tax_*`.
