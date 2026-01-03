# PRD: IPAI Copilot (Odoo CE)

**Product**: IPAI Copilot (Odoo CE)
**Target**: v0.?.0
**Status**: Planning

## 1. Problem Statement
Users doing month-end close, BIR filing, and finance ops inside Odoo need instant, contextual help (policies, deadlines, SOPs) without leaving Odoo. Knowledge is currently scattered across external docs and spreadsheets.

## 2. Goals
- **G1**: In-Odoo ChatGPT UI (Systray + Right Panel).
- **G2**: Deployable simple RAG backend (Supabase/Edge Functions).
- **G3**: Seeded Finance Close Knowledge MVP.
- **G4**: Source of Truth drift enforcement.

## 3. User Stories
- **US1**: As Finance Ops, I ask "When is BIR 1601-C due?" and get a cited answer.
- **US2**: As Finance Ops, I ask "What are the close steps?" and get a checklist.
- **US3**: As Admin, I configure the Copilot API URL in Settings.

## 4. UX Requirements
- **Systray**: Chat icon 💬.
- **Panel**: Slide-in from right.
- **Composer**: Chat input with send button.
- **Response**: Markdown text + Citation links.

## 5. Technical Requirements
- **Frontend**: Odoo 18 OWL Component.
- **Backend API**: POST `/copilot/query` (Odoo -> Proxy -> RAG).
- **Data Store**: Supabase `docs.chunks` (pgvector).
- **Ingestion**: Python script `scripts/copilot_ingest.py`.

## 6. API Contract
Request:
```json
{
  "message": "When is the deadline?",
  "odoo": { "db": "...", "uid": 1, "context": {} }
}
```
Response:
```json
{
  "ok": true,
  "answer": "The deadline is...",
  "citations": [{ "title": "BIR SOP", "url": "..." }]
}
```

## 7. CI & Determinism
- **Drift Gate**: Docs -> Manifest -> DB. If docs change, manifest must be regenerated.
- **Spec Gate**: This bundle must exist.
