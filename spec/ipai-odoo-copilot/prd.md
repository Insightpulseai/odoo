# PRD: ipai_odoo_copilot

> **Status**: Draft
> **Product**: Thin Odoo bridge module for a Foundry-backed AI copilot.
> **Constitution**: [constitution.md](constitution.md)

---

## Problem

Finance operators using Odoo CE spend significant time on repetitive
investigative tasks during month-end close, reconciliation, collections,
and variance analysis. They alt-tab between Odoo, spreadsheets, email,
and chat to assemble context that an AI assistant could surface in seconds.

There is no native mechanism in Odoo CE 19 to delegate context-aware
questions to an external AI runtime and render actionable answers inline.

## Goal

Deliver a thin Odoo module (`ipai_odoo_copilot`) that:

1. Lets finance operators ask natural-language questions from within Odoo.
2. Packages the relevant ERP context (active record, user, company, related data).
3. Delegates the question + context to Azure AI Foundry for inference.
4. Renders the answer (text, suggested actions, citations) in the Odoo UI.
5. Logs every interaction for audit and compliance.

The module is a bridge, not a platform. Intelligence lives in Foundry.

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Module installs cleanly | 0 errors on `odoo-bin -i ipai_odoo_copilot --stop-after-init` | CI gate |
| Finance Q&A round-trip | < 5 seconds p95 latency (Odoo to Foundry and back) | Application Insights |
| Audit coverage | 100% of copilot interactions produce an audit record | Unit test + runtime check |
| Read-only default | No Odoo write operations without explicit user confirmation | Security test |
| Graceful degradation | Odoo UI fully functional when Foundry endpoint is unreachable | Integration test |
| User adoption (Release 1) | >= 3 finance operators using copilot weekly within 30 days | Telemetry |

---

## Personas

### Finance Operator

- **Role**: Accountant, AP/AR clerk, finance manager.
- **Context**: Works in Odoo Accounting (journal entries, invoices, payments, reconciliation).
- **Need**: Quick answers about balances, aging, reconciliation status, variance explanations.
- **Constraint**: Must not accidentally post or modify records via copilot.

### Project / PPM User

- **Role**: Project manager, task owner (using `ipai_finance_ppm`).
- **Context**: Works in Odoo Project with finance-linked tasks and milestones.
- **Need**: Status summaries, milestone health, budget vs. actual comparisons.
- **Constraint**: Deferred to Release 2. Not in scope for initial finance-first release.

### System Administrator

- **Role**: IT admin, Odoo technical lead.
- **Context**: Configures module settings, manages policies, monitors audit logs.
- **Need**: Simple admin UI for endpoint configuration, feature flags, action allowlists.
- **Constraint**: Must not require Azure CLI or Foundry console access for basic configuration.

---

## User Stories

1. **As a finance operator**, I want to ask "What invoices are overdue for partner X?" from the Odoo systray and get a contextual answer with links to the relevant records.

2. **As a finance operator**, I want the copilot to suggest reconciliation matches for a bank statement line, showing me the proposed journal entry before I approve it.

3. **As a finance operator**, I want to ask "Why does the P&L variance exceed 10% for cost center Y?" and receive a summary grounded in Odoo data and analytics context.

4. **As a system administrator**, I want to configure the Foundry endpoint URL, enable/disable the copilot per company, and review the audit log from Odoo Settings.

5. **As a finance operator**, I want the copilot to draft a collections follow-up email for overdue invoices, which I can review and send from the Odoo mail composer.

---

## Functional Requirements

### FR-1: Entry Points

The module provides three copilot entry points in the Odoo UI:

| Entry Point | Location | Trigger |
|-------------|----------|---------|
| Systray icon | Top-right system tray | Click opens chat panel |
| Form helper button | Form views (configurable per model) | Click with active record context |
| Chat panel | Slide-out panel on right side | Text input + send |

All entry points share the same underlying copilot service.

### FR-2: Context Packaging

When a copilot request is initiated, the module assembles a context payload:

| Field | Source | Required |
|-------|--------|----------|
| `user_id` | `self.env.user` | Yes |
| `company_id` | `self.env.company` | Yes |
| `active_model` | Current model (if form view) | No |
| `active_id` | Current record ID (if form view) | No |
| `active_record_data` | Serialized fields of active record | No |
| `user_groups` | User's security group XML IDs | Yes |
| `user_question` | Free-text question from the user | Yes |
| `session_id` | Copilot session identifier | Yes |
| `locale` | User's language code | Yes |

The context payload is JSON-serialized. Sensitive fields (passwords, tokens)
are never included. The module applies field-level filtering based on the
user's access rights before serialization.

### FR-3: External Runtime Delegation

The module sends the context payload to the configured Foundry endpoint via
HTTPS POST. The request includes:

- Bearer token (Entra ID user-scoped or managed identity token).
- JSON body with the context payload.
- Request timeout configurable via `ir.config_parameter`.

The module does not interpret, transform, or cache the response beyond
what is needed for rendering and audit.

### FR-4: Read-Only Assistance

The default copilot mode is read-only. The assistant may:

- Answer questions with text and citations.
- Surface links to Odoo records (using `web#id=...&model=...` URLs).
- Display tabular summaries of queried data.
- Suggest actions (displayed as buttons) but not execute them.

No Odoo ORM write operations occur in read-only mode.

### FR-5: Approved Action Mediation

When the Foundry runtime returns a suggested action (e.g., "Post this journal
entry", "Send this email"), the module:

1. Checks the action against the admin-configured policy allowlist.
2. If allowed, displays a confirmation dialog showing exactly what will happen.
3. On user confirmation, executes the action via standard Odoo ORM methods.
4. Logs the action execution in the audit trail.

If the action is not in the allowlist, it is displayed as a read-only
suggestion with a note that admin approval is required to enable it.

### FR-6: Auditability

Every copilot interaction produces an `ipai.copilot.audit` record:

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | Many2one | User who initiated the request |
| `session_id` | Char | Copilot session identifier |
| `request_timestamp` | Datetime | When the request was sent |
| `response_timestamp` | Datetime | When the response was received |
| `user_question` | Text | The question asked |
| `assistant_response` | Text | The response received (truncated if > 10KB) |
| `active_model` | Char | Model context (if any) |
| `active_id` | Integer | Record ID context (if any) |
| `action_taken` | Char | Action executed (if any) |
| `action_result` | Selection | success / failure / declined / timeout |
| `provider` | Char | Runtime provider identifier |
| `latency_ms` | Integer | Round-trip latency in milliseconds |
| `company_id` | Many2one | Company context |

Audit records are read-only after creation. Only users in the
`ipai_odoo_copilot.group_copilot_admin` group can view all audit records.
Regular users can view only their own.

### FR-7: Admin Configuration

The module adds a settings section under Odoo Settings > General Settings:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| Copilot Enabled | Boolean | False | Master on/off switch |
| Foundry Endpoint URL | Char | (empty) | HTTPS URL for the Foundry runtime |
| Auth Mode | Selection | `managed_identity` | `managed_identity` or `api_key` |
| API Key | Char (secret) | (empty) | Only used if auth mode is `api_key` |
| Request Timeout (s) | Integer | 30 | Maximum wait for Foundry response |
| Allowed Actions | Text (JSON) | `[]` | JSON array of allowed action identifiers |
| Telemetry Enabled | Boolean | True | Send usage telemetry to Application Insights |
| Max Context Records | Integer | 50 | Maximum related records included in context |

### FR-8: Failure-Safe UX

When the external runtime is unavailable or returns an error:

- The systray icon shows a degraded state indicator (grey dot).
- The chat panel displays: "Copilot is temporarily unavailable. Your ERP continues to work normally."
- No Python exceptions propagate to the Odoo UI.
- The failure is logged as an audit record with `action_result = 'timeout'` or `'failure'`.
- Retry logic: one automatic retry after 2 seconds, then surface the error.

### FR-9: Extensible Provider Contract

The module defines a provider interface (`ipai.copilot.provider` abstract model)
so that the Foundry endpoint can be swapped for another runtime without
modifying the bridge module:

```python
class CopilotProvider(models.AbstractModel):
    _name = 'ipai.copilot.provider'

    def send_request(self, payload):
        """Send context payload, return response dict."""
        raise NotImplementedError

    def validate_config(self):
        """Return True if provider is configured and reachable."""
        raise NotImplementedError
```

The default provider (`ipai.copilot.provider.foundry`) implements the
Azure AI Foundry contract. Additional providers can be added via separate
modules without modifying `ipai_odoo_copilot`.

### FR-10: Finance Q&A

The copilot supports natural-language questions about finance data:

- "What is the AR aging for partner X?"
- "Show me unreconciled bank statement lines for this month."
- "What journal entries were posted today?"
- "What is the cash balance across all bank accounts?"

The module packages the relevant Odoo context (account.move, account.move.line,
account.bank.statement.line, res.partner) and delegates to Foundry for
answer generation. The module does not execute SQL queries or ORM searches
beyond what is needed to assemble the context payload.

### FR-11: Reconciliation Assistance

The copilot assists with bank reconciliation:

- Given a bank statement line, suggests matching journal items.
- Displays proposed matches with confidence indicators.
- On user approval, creates the reconciliation via Odoo's native reconciliation API.
- Never auto-reconciles. Every match requires explicit user confirmation.

### FR-12: Collections Assistance

The copilot assists with collections follow-up:

- Given an overdue invoice or partner, drafts a follow-up email.
- Uses the partner's communication history and payment patterns as context.
- Presents the draft in the Odoo mail composer for review and send.
- Never sends email automatically. The user presses Send.

### FR-13: Variance-Analysis Assistance

The copilot assists with P&L and budget variance analysis:

- Answers questions like "Why is COGS 15% above budget for Q1?"
- Surfaces relevant journal entries, analytic accounts, and cost center data.
- If analytics context is available (Databricks/Power BI), includes governed summaries.
- Presents variance breakdowns as structured text or tables.

### FR-14: Escalation and Routing Metadata

When the copilot cannot fully answer a question or the question involves
a policy decision, the response includes escalation metadata:

| Field | Description |
|-------|-------------|
| `escalation_needed` | Boolean: does this need human review? |
| `escalation_reason` | Why the copilot is escalating |
| `suggested_assignee` | Odoo user or group best suited to handle |
| `priority` | low / medium / high / critical |

The module renders escalation metadata as a callout in the chat panel.
It does not automatically create tasks or notifications (deferred to Release 2).

---

## Non-Functional Requirements

### NFR-1: Thin Footprint

- Module Python code: < 2,000 lines (excluding tests).
- No additional Python dependencies beyond Odoo's standard library and `requests`.
- JS/XML assets: < 500 lines total.
- Database tables: maximum 3 new models.

### NFR-2: Security

- All external requests use HTTPS with TLS 1.2+.
- Bearer tokens are acquired at runtime, never stored in `ir.config_parameter`.
- API keys (if used) are stored as Odoo system parameters marked as secret.
- User context payloads respect Odoo's record rules and field-level ACLs.
- No PII is logged in plaintext in audit records (redaction policy for sensitive fields).

### NFR-3: Latency

- Context packaging: < 200ms for typical finance records.
- Network round-trip to Foundry: target < 3 seconds p50, < 5 seconds p95.
- Total user-perceived latency: < 6 seconds p95.
- Streaming responses (if supported by provider): first token < 1 second.

### NFR-4: Observability

- Structured logging via Python `logging` module (no print statements).
- Telemetry events emitted to Application Insights (if enabled).
- Key metrics: request count, latency histogram, error rate, action execution count.
- Health check endpoint: `/ipai_copilot/health` returns `{"status": "ok"}` or `{"status": "degraded"}`.

### NFR-5: Deployability

- Installs on Odoo CE 19.0 with `--stop-after-init` in < 10 seconds.
- No post-install migration scripts required for fresh install.
- Upgradeable via standard `odoo-bin -u ipai_odoo_copilot`.
- Compatible with Odoo.sh deployment (no Azure-only runtime dependencies).
- Docker image size impact: < 5 MB.

---

## Release 1 Scope (Finance-First)

Release 1 targets finance operators exclusively. Included:

| Feature | FR Reference |
|---------|-------------|
| Systray + chat panel entry points | FR-1 |
| Context packaging for accounting models | FR-2 |
| Foundry delegation (read-only) | FR-3, FR-4 |
| Finance Q&A (AR aging, balances, journals) | FR-10 |
| Reconciliation assistance | FR-11 |
| Collections follow-up drafting | FR-12 |
| Variance-analysis summaries | FR-13 |
| Escalation metadata | FR-14 |
| Full audit logging | FR-6 |
| Admin configuration UI | FR-7 |
| Failure-safe UX | FR-8 |

Release 1 is **read-only by default**. Approved action mediation (FR-5) is
available but ships with an empty allowlist. Admins must explicitly enable
actions they trust.

## Release 2 Scope (Actions + Broader Grounding)

Release 2 extends to approved write actions and deeper grounding:

| Feature | FR Reference |
|---------|-------------|
| Approved action mediation (post JE, send email) | FR-5 |
| Document grounding (attachments, OCR context) | New |
| Project/PPM copilot context | New |
| Helpdesk copilot context | New |
| Automatic task creation from escalation | FR-14 extension |
| Extensible provider contract | FR-9 |
| Streaming response rendering | FR-3 extension |

---

## Scenario Focus

The following scenarios are the primary evaluation targets for Release 1:

### Scenario 1: Month-End Close Q&A

> A finance operator is reviewing the trial balance during month-end close.
> They click the copilot systray icon and ask: "Are there any unposted
> journal entries for March?" The copilot packages the company and period
> context, queries Foundry, and returns a list of 3 draft journal entries
> with links. The operator clicks through and posts them.

### Scenario 2: Bank Reconciliation Assistance

> A finance operator opens a bank statement with 12 unreconciled lines.
> They click the copilot helper button on a statement line and ask:
> "What matches this payment of PHP 45,000 from ABC Corp?" The copilot
> returns 2 candidate invoices with confidence scores. The operator
> confirms the match and the reconciliation is created via Odoo's API.

### Scenario 3: Collections Follow-Up

> A finance operator views a partner with 5 overdue invoices totaling
> PHP 250,000. They ask the copilot: "Draft a follow-up email for this
> partner." The copilot generates a professional email referencing the
> specific invoice numbers and amounts, and opens it in the Odoo mail
> composer for review.

### Scenario 4: Variance Explanation

> A finance manager asks: "Why is the marketing cost center 20% over
> budget this month?" The copilot surfaces the top 5 journal entries
> contributing to the variance, grouped by account, with a plain-language
> summary.

---

## Acceptance Criteria

1. `odoo-bin -i ipai_odoo_copilot --stop-after-init` completes with 0 errors on a clean Odoo CE 19 database.
2. The systray icon appears for users in the `group_copilot_user` group.
3. A question submitted via the chat panel produces an audit record within 10 seconds.
4. When the Foundry endpoint is unreachable, the UI shows a degraded state and no Python tracebacks appear in the Odoo log.
5. The admin configuration UI is accessible under Settings > General Settings > Copilot.
6. All 4 finance scenarios (month-end Q&A, reconciliation, collections, variance) produce contextually relevant responses in a test environment with demo data.
7. No ORM write operations occur unless the user explicitly confirms a suggested action.
8. The module has >= 80% Python line coverage from unit and integration tests.
9. The module passes `flake8`, `black --check`, and `isort --check` with zero violations.
10. The module installs alongside `account_reconcile_oca`, `mis_builder`, and `ipai_finance_ppm` without conflict.

---

*Last updated: 2026-03-22*
