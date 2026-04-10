# Pulser Odoo PH — Constitution

> Non-negotiable rules and constraints for Pulser as an Odoo 18 PH copilot backed by Microsoft Foundry.

---

## Invariants

1. **Odoo is system of record.** Pulser reads context from and proposes actions to Odoo, but never becomes the transactional source of truth for records, journals, invoices, or compliance state.
2. **CE only.** No Enterprise module dependencies, no odoo.com IAP calls. OCA modules preferred over custom `ipai_*`.
3. **Thin bridge doctrine.** `ipai_*` modules under Pulser scope are limited to UI surfaces, context extraction, and action adapters. They do not replicate ERP business logic already present in Odoo or OCA.
4. **No autonomous posting.** Pulser may not post to books, submit tax filings, or execute regulatory submissions without explicit human approval.
5. **Approval-gated actions.** High-risk actions always require human approval. The approval gate cannot be bypassed programmatically.
6. **Foundry SDK is primary runtime.** Agent orchestration, evaluations, and tracing use the Foundry SDK project endpoint. OpenAI-compatible client is used for model-shaped interactions only.
7. **PH compliance is first-class.** Philippines tax, document, and regulatory assistance is a primary capability lane, not an afterthought or plugin.
8. **Explainable outputs.** Every recommendation must expose rationale and source context. Fabricated policy or tax guidance when source context is absent is banned.
9. **ACL-safe context.** Pulser must respect Odoo access control lists and record rules. No context leakage across permission boundaries.
10. **Trace everything.** Every prompt, tool call, approval decision, and output must emit trace/log metadata for audit.
