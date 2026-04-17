# Pulser Platform — Constitution

> Non-negotiable rules and constraints for the Pulser control plane.

---

## Invariants

1. **Platform owns schemas, not behavior.** The platform defines data contracts (PulserTaxRuleSource, TaxEvidenceBundle, etc.) but never executes agent logic directly.
2. **Grounding hierarchy is immutable at runtime.** The 6-tier PH source hierarchy (BIR legal → BIR guidance → BIR execution → CGPA competency → Odoo localization → internal context) cannot be reordered by agents or user preference.
3. **Authority precedence is non-negotiable.** Tier 1 (BIR legal) always overrides Tier 5 (Odoo localization) and Tier 6 (internal context). No exception.
4. **No unsupported legal conclusions.** Any tax determination that lacks Tier 1-2 citation must be flagged as `unsupported` and escalated — never presented as authoritative.
5. **Evidence bundles are append-only.** Once a PulserTaxEvidenceBundle is created, its citations cannot be removed or downgraded — only new citations may be added.
6. **Odoo is adapter, not control plane.** The `odoo` repo provides ERP context and execution, but never governs tax policy, agent orchestration, or grounding hierarchy.
7. **TaxPulse-PH-Pack is bounded.** It is one domain pack within Tax Guru, not the entire sub-agent. It owns PH BIR computation, not cross-jurisdiction reasoning.
8. **Safe action defaults.** All tax actions default to `suggest_only` or `approval_required`. Direct execution only for narrow, reversible, low-risk operations.
9. **Schema changes require spec update.** Any change to evidence schema objects must update `spec/pulser-platform/prd.md` before implementation.
10. **Citation groups are structurally distinct.** `authoritative_citations` (Tier 1-2), `supporting_citations` (Tier 3-4), and `execution_model_citations` (Tier 5) must never be merged into a flat list.
