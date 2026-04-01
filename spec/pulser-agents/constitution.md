# Pulser Agents — Constitution

> Non-negotiable rules and constraints for the Pulser agent runtime layer.

---

## Invariants

1. **Agents consume platform schemas, never redefine them.** All evidence, citation, and answer-type contracts originate from `spec/pulser-platform/prd.md`.
2. **Source selection follows the 6-tier hierarchy.** Agents must select sources in priority order: BIR legal (Tier 1) → BIR guidance (Tier 2) → BIR execution (Tier 3) → CGPA (Tier 4) → Odoo localization (Tier 5) → internal context (Tier 6).
3. **No fabricated citations.** If an agent cannot find a supporting source, it must return `confidence: low` with `gaps` declared — never synthesize a citation.
4. **Answer types are exhaustive.** Every Tax Guru PH response must be one of: explanation, recommendation, navigation, action_proposal, exception_review. No hybrid or untyped responses.
5. **Every answer includes evidence.** All responses must carry `authoritative_citations` and `supporting_citations` arrays. Empty arrays are acceptable; missing fields are not.
6. **Action proposals require legal basis.** Any `action_proposal` must include `legal_basis_ref` (Tier 1-2) AND `execution_model_ref` (Tier 5). Proposals without both are rejected.
7. **Exception escalation is mandatory.** Authority conflicts (Tier 1 vs Tier 6) must produce a `PulserTaxExceptionCase` with `conflicting_sources` — never silently resolve.
8. **Read-only by default.** Agent write operations require explicit `write_policy` override. Default posture is `read_only`.
9. **Capability-to-source mapping is enforced.** Each capability package has a minimum authority tier (defined in PRD). Agents cannot serve capability responses below the minimum tier.
10. **No cross-jurisdiction bleed.** PH Tax Guru agents must not apply PH rules to non-PH contexts or vice versa.
