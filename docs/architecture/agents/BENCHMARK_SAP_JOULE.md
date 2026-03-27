# Agent Factory vs SAP Joule

The Agent Factory is designed to provide stronger transactional guardrails and more explicit operational controls than a conversational assistant baseline such as SAP Joule, especially for ERP-sensitive workflows in Odoo.

Where Joule is primarily optimized around conversational UX and task assistance, the hardened Agent Factory is optimized around transactional integrity, fail-closed execution, and operational safety.

## 1) Transactional (Create / Update / Delete)

Joule emphasizes conversational task completion with human review.

The hardened Agent Factory is designed for fail-closed correctness in bounded workflows. If an agent attempts a sensitive Odoo action such as deleting a purchase order or creating an invoice, that action can be blocked when evaluation confidence, evidence requirements, or policy contracts are not satisfied.

The Supervisor is designed for single-writer idempotent transition issuance under documented lock and topology assumptions, reducing the risk of duplicate transactional issuance in ERP workflows.

## 2) Navigational (Find / Route / Progress Work)

Joule emphasizes role-aware navigation to relevant processes.

The Agent Factory provides task routing, stage-aware agent passports, and bounded lease/claim behavior so complex Odoo workflows can be decomposed and routed across specialized agents. This is particularly useful for multi-step ERP flows such as lead-to-quote, quote-to-order, and order-to-delivery.

Routing and lease controls are intended to bound duplicate handling, stale claims, and recovery behavior under the deployment assumptions declared in the runtime contracts.

## 3) Informational (Search / Summarize / Ground)

Joule emphasizes grounded answers and enterprise information retrieval.

The Agent Factory applies evidence-oriented evaluation. For tasks that require grounded informational output, evidence references are part of the promotion contract. If the output cannot satisfy the evidence contract, the pipeline rejects or quarantines the result instead of promoting it as trusted completion.

This makes the system better suited to finance-sensitive or audit-sensitive Odoo workflows where unsupported summaries are operationally risky.

## Why this is a stronger benchmark for Odoo-sensitive execution

The Agent Factory is not just a chat surface. It is a governed execution pipeline.

| Dimension | SAP Joule-style baseline | Hardened Agent Factory |
|---|---|---|
| Trust model | Human review emphasized | Fail-closed promotion and execution gates for bounded workflows |
| Execution integrity | Conversation-centric task assistance | Idempotency- and evidence-oriented controls for finance-sensitive workflows |
| Operational safety | Platform-managed operational model | Topology- and contract-gated release model |
| Governance | Vendor-governed product model | Repo- and SSOT-governed contract model |

## Conclusion

By moving the Agent Factory to a ready-for-conditional-production-release state, we have built the control framework required to let AI agents interact with sensitive Odoo workflows with bounded risk, fail-closed gates, and explicit runtime assumptions.

The result is not merely an assistant that can talk about work. It is a contract-first pipeline designed to execute bounded work safely, reject ambiguous outputs, and preserve operational discipline across ERP-sensitive flows.
