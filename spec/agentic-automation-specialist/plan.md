# Plan: Agentic Automation Specialist Implementation

## 1. Foundation

- [x] Create `agents/personas/automation_specialist.md`.
- [x] Create `skills/n8n_workflow_builder.md`.
- [x] Register in `agents/registry/agents.yaml`.

## 2. Spec Kit Standardization

- [x] Draft `constitution.md` (Governance & Ethics).
- [x] Draft `prd.md` (Requirements & Goals).
- [ ] Draft `plan.md` (Technical Architecture).
- [ ] Draft `tasks.md` (Work Breakdown).

## 3. Reference Implementation

- [ ] Design a "Reference Tool" workflow: `ipai_platform__reference_tool__v1`.
  - Trigger: Webhook (with JSON validation).
  - Logic: Mock data processing + Odoo RPC call.
  - State: Emit `pending` -> `success/failed` to Supabase.
- [ ] Export as stable JSON.

## 4. Documentation

- [ ] Update `CLAUDE.md` metadata to include the new capability.
- [ ] Create a README in `infra/n8n/` explaining the "Workflow as Tool" pattern.
