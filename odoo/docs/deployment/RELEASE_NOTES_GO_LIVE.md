# GO-LIVE RELEASE MANIFEST (Odoo 18 CE + IPAI)
Date: 2026-01-05
Environment: Production (erp.insightpulseai.com)
Scope: Close + Tax Command Center + Invite-only onboarding + Ask AI provider wiring

---

## 1) Shipped Modules (Go-Live Set)
### Required (core)
- project (Odoo)
- mail (Odoo)
- base_setup (Odoo)
- ipai_project_suite (CE Project Suite + toggles)
- ipai_month_end_closing (Month-end close orchestration)
- ipai_bir_tax_compliance (BIR tax compliance workflow)
- ipai_close_orchestration (workflow/stage-gates for close)
- ipai_ask_ai (Ask AI provider toggle + invite tool + Settings integration)

### Optional (visual)
- ipai_theme_tbwa_backend (TBWA backend branding)
- ipai_web_theme_chatgpt (optional: Chat-like styling)

---

## 2) Features Included (What’s Live)
### A) Close + Tax Project Command Center
- Month-end Close and BIR Tax Filing projects built on:
  - project.project
  - project.task
- Task stages aligned to operational workflow (prep/review/approval/done)
- Stage gates (approval checks) enforce workflow discipline
- Calendar events imported (holidays + deadlines) to anchor timelines
- Ownership standardized:
  - Finance Supervisor = Beng Manalo (beng.manalo@omc.com)

### B) Data Import Pipeline (Workbook → Odoo)
- Workbook generator outputs:
  - Projects CSV
  - Stages CSV
  - Tasks Pass A (parents) CSV
  - Tasks Pass B (children) CSV
  - Calendar Events CSV
- Placeholders are removed prior to import (no <<MAP:...>> tasks)
- Import runs via JSON-RPC importer (session auth; deterministic upserts)

### C) Invite-only Onboarding (Outbound Email Only)
- Goal: invitations + password reset only (no invoicing dependency)
- Works with:
  - Gmail OAuth (Odoo “Use a Gmail Server”), OR
  - SMTP (e.g., Zoho), via Outgoing Mail Server
- Invite flow:
  - Create/Reactivate internal user
  - Send invitation email via reset-password mechanism

### D) Ask AI (Copilot) Foundations
- Provider toggle in Settings:
  - ChatGPT (OpenAI)
  - Google Gemini
- Keys stored as system parameters (no code hardcoding)
- Invite-only controls exposed in Settings:
  - Invite-only flag
  - Allowed domain allowlist
- Admin tool primitive available: invite_user(email, name, groups)

---

## 3) Configuration Toggles (Settings / System Params)
### Ask AI
- ipai.ask_ai.enabled = True
- ipai.ask_ai.provider = openai | gemini
- ipai.ask_ai.openai_api_key = <set in Settings>
- ipai.ask_ai.gemini_api_key = <set in Settings>

### Invite-only policy
- ipai.ask_ai.invite_only = True
- ipai.ask_ai.domain_allowlist = "omc.com,tbwa-smp.com"

### Email (Outbound)
- Outgoing Mail Server configured and active (Gmail OAuth or SMTP)

---

## 4) Acceptance Checks (Go/No-Go)
### A) Platform + modules
- [ ] Odoo container healthy
- [ ] Modules installed/upgraded successfully
- [ ] No missing models for IPAI project suite components

### B) Email invite-only
- [ ] Outgoing mail server exists and is active
- [ ] Send 1 user invite email successfully
- [ ] Send 1 password reset email successfully
- [ ] Mail queue processes (no stuck “Exception” state)

### C) Close/Tax projects present
- [ ] Close project exists (project.project)
- [ ] Tax project exists (project.project)
- [ ] Tasks imported (parents + children)
- [ ] Placeholder scan returns 0 (no <<MAP:...>> remnants)
- [ ] Beng exists as internal user and is assigned to expected approvals/tasks

### D) Ask AI
- [ ] Provider set (openai or gemini)
- [ ] Key present for selected provider
- [ ] Ask AI smoke test returns response (admin-only)
- [ ] If provider/key missing: clear admin error shown (no silent failure)

---

## 5) Operational Notes / Known Gaps (Explicit)
### Included now
- “Command Center” built via dashboards/pivots on project.task + project.project

### Not included yet (future)
- A fully custom single-screen OWL Command Center (widgets + KPI cards + action buttons)
- Full OpenAI App SDK-style embedded chat UI inside Odoo (beyond Settings + provider wiring)
- Full accounting automation scripts (TB import + reconciliations); checklist only

---

## 6) Evidence Artifacts (from this go-live)
- TBWA_OMC_Odoo18_GoLive_Checklist.xlsx
- TBWA_OMC_Odoo18_GoLive_Checklist.csv
- odoo_import_month_end_*.csv (projects/stages/tasks/calendar)
- Patched child tasks CSV (no placeholder emails)
- Patched role_email_map CSV (Finance Supervisor → Beng)
