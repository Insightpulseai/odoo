# Odoo Copilot — Constitution

> Non-negotiable rules governing all implementation phases.
> This file is the SSOT for architectural constraints.

## 1. Thin Odoo Adapters
Odoo-side modules may normalize context, permissions, tool exposure, and deep links, but must not embed long-running orchestration logic or external channel workflow state.

## 2. n8n Owns Async Orchestration
All AI orchestration, retries, callback routing, conversation state, and channel-specific runtime behavior stay in n8n. Odoo only validates and executes business actions when called.

## 3. Mutable State in ORM Only
Mutable workflow state stays in standard ORM-backed models. No workflow state in reporting views, readonly models, or external stores.

## 4. Readonly Analytics / Reporting
Any analytics/telemetry for copilot usage must use readonly analytics models (`_auto = False`, readonly fields) following Odoo's documented reporting pattern.

## 5. Channel Adapters Are Transport Relays
External productivity channels (Slack, Teams) are thin transport relays into n8n. They verify signatures, extract message/identity, and forward. No business logic, no AI logic, no conversation state.

## 6. Copilot Tools Are Permissioned
All tool executions run under the resolved Odoo user context. Record rules and access rights are enforced by the ORM. No sudo bypasses for business actions.

## 7. RAG Is Citation-First
RAG responses must include source metadata (document title, issuance number, effective date, section reference) suitable for audit/review. No unsourced assertions.

## 8. CE-Safe Boundaries
No Enterprise modules, no IAP, no Odoo.sh dependencies. All modules must install and run on Odoo CE 19.0.

## 9. Reuse Before Invent
Reuse existing Odoo business records, activities, and chatter patterns. Do not create new approval/workflow state machines unless gap analysis proves existing Odoo models cannot cover the workflow.

## 10. Naming Convention
- Product name (UI/docs): **Odoo Copilot**
- Platform family: **AI**
- Technical namespace: `ipai_ai_*`
- Spec slug: `odoo-copilot`
