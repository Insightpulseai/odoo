# M365 Copilot Interoperability

> Cross-copilot model for Pulser invocation from Microsoft 365 Copilot.
> Benchmarked against the SAP Joule + M365 Copilot cross-surface pattern and
> the Microsoft 365 Agents SDK declarative agent model.

---

## Overview

Pulser operates as a **plugin agent** that M365 Copilot can invoke when a user
asks ERP-related questions within the Microsoft 365 surface (Teams, Outlook,
Word, Excel, or the M365 Copilot chat). This follows the host-assistant
invocation model where M365 Copilot is the **host** and Pulser is the
**assistant**.

The user does not need to switch to Odoo to ask a question. M365 Copilot
routes ERP-domain prompts to Pulser, which executes against Odoo and returns
results in a format the host can render.

---

## Host-Assistant Invocation Model

### Invocation Flow

```
User (in Teams/Outlook/M365 Chat)
  |
  v
M365 Copilot (host)
  | Detects ERP-domain intent
  | Routes to Pulser plugin
  v
Pulser Plugin (declarative agent)
  | Validates user identity (Entra token)
  | Maps Entra user to Odoo user
  | Executes tool against Odoo/Databricks
  v
Pulser returns structured response
  |
  v
M365 Copilot (host)
  | Renders response in host surface
  | Applies render class rules
  v
User sees result in Teams/Outlook/M365 Chat
```

### Registration

Pulser is registered as a declarative agent in the Microsoft 365 Agents SDK
manifest. The manifest declares:

| Manifest field | Value |
|---------------|-------|
| `name` | Pulser |
| `description` | AI assistant for Odoo ERP -- accounts, sales, HR, inventory |
| `capabilities` | `actions` (API plugin), `graphConnectors` (optional) |
| `actions.type` | `OpenApi` |
| `actions.api_endpoint` | `https://erp.insightpulseai.com/api/copilot/m365` |
| `auth.type` | `OAuthSso` |
| `auth.entra_app_id` | Registered app in tenant `402de71a` |

### Invocation Triggers

M365 Copilot routes prompts to Pulser when:

1. The user explicitly invokes Pulser by name ("Ask Pulser about outstanding invoices")
2. The prompt matches ERP-domain keywords registered in the plugin manifest (invoice, purchase order, employee, inventory, journal entry, etc.)
3. The user is in a context where Pulser is pinned (e.g., a Teams channel with Pulser enabled)

---

## Render Classes

Not all Pulser responses can be rendered identically across surfaces. The
render class system defines three levels of fidelity.

### Host-Safe (Markdown Only)

Responses that M365 Copilot can render natively in any surface without
degradation. These are the default for informational and navigational results.

| Content type | Rendering |
|-------------|-----------|
| Plain text answers | Rendered as-is |
| Markdown tables | Rendered as formatted tables |
| Bulleted/numbered lists | Rendered as lists |
| Inline code or identifiers | Rendered with monospace formatting |
| Deep links to Odoo | Rendered as clickable URLs |
| Numeric summaries | Rendered as text with optional Adaptive Card |

**Constraints**: No custom HTML, no iframes, no JavaScript, no Odoo-specific
widgets. Maximum response size: 4,000 tokens (M365 Copilot truncation limit).

### Degraded (Simplified)

Responses where the full Pulser output contains rich content that M365 Copilot
cannot render. The response is automatically simplified to a host-safe subset.

| Full Pulser output | Degraded M365 output |
|-------------------|---------------------|
| Interactive data grid with sorting | Static markdown table (first 20 rows) |
| Chart or visualization | Text summary of key data points + deep link |
| Multi-tab record view | Single-section summary with deep link to full view |
| Form with editable fields | Read-only field summary + "Open in Odoo" link |
| PDF/document preview | Document title + download link |

The degradation rules are defined in the Pulser response formatter. Each tool
declares its `render_class` in the tool registry, and the M365 response adapter
applies the appropriate transformation.

### Native-Only (Redirect to Odoo)

Responses that cannot be meaningfully rendered outside of Odoo. For these, the
M365 surface shows a brief summary and a prominent link to open the full
experience in Odoo.

| Scenario | M365 output |
|----------|-------------|
| Transactional confirmation (create/update/approve) | Summary of proposed action + "Confirm in Odoo" link |
| Multi-step workflow requiring form interaction | "This requires the Odoo form view" + deep link |
| File upload or attachment operations | "Upload this document in Odoo" + deep link |
| Complex reconciliation requiring drag-and-drop | "Open reconciliation in Odoo" + deep link |
| Custom IPAI module UI (non-standard views) | "Open in Odoo" + deep link |

**Design principle**: Transactional actions are never executed from M365 Copilot
without the user confirming in the Odoo-native interface. This ensures the user
sees the full context (record state, related records, warnings) before
confirming a mutation.

---

## Markdown-Safe Output Contract

All Pulser responses routed through M365 Copilot must conform to the
markdown-safe output contract. This ensures consistent rendering across all
M365 surfaces.

### Allowed Markdown Elements

| Element | Supported | Notes |
|---------|-----------|-------|
| Headings (H1-H3) | Yes | H1 reserved for the response title |
| Paragraphs | Yes | |
| Bold, italic | Yes | |
| Inline code | Yes | For record references, field names |
| Code blocks | Yes | For structured data, limited to 50 lines |
| Unordered lists | Yes | |
| Ordered lists | Yes | |
| Tables | Yes | Maximum 10 columns, 50 rows |
| Links | Yes | Must be HTTPS, absolute URLs only |
| Images | No | Use text descriptions instead |
| HTML tags | No | Stripped by host |
| Embedded iframes | No | Not supported |
| LaTeX/math | No | Use plain text notation |

### Response Structure

Every M365-routed Pulser response follows this structure:

```markdown
## [Response Title]

[Natural language answer or summary]

| Column A | Column B | Column C |
|----------|----------|----------|
| data     | data     | data     |

[Deep link to Odoo for full details](https://erp.insightpulseai.com/...)

---
Source: Pulser (Odoo CE 19) | Data as of [timestamp]
```

The footer line provides attribution and freshness context.

---

## Fallback Behavior

When the M365 host cannot render a Pulser response, or when the response
requires native Odoo interaction, the following fallback chain applies:

### Fallback Chain

```
1. Attempt host-safe render
   |
   +-- Success --> Display in M365 surface
   |
   +-- Fail (content too rich) --> Apply degradation rules
       |
       +-- Degraded render acceptable --> Display simplified version
       |
       +-- Cannot degrade meaningfully --> Redirect to Odoo
           |
           +-- Generate deep link URL
           +-- Display: "This requires the full Odoo interface"
           +-- Show: summary card + "Open in Odoo" button
```

### Redirect URL Format

```
https://erp.insightpulseai.com/web#model={model}&view_type={view}&id={id}&action={action_id}
```

For filtered list views:

```
https://erp.insightpulseai.com/web#model={model}&view_type=list&action={action_id}&domain={encoded_domain}
```

### Timeout Handling

| Scenario | Behavior |
|----------|----------|
| Pulser responds within 10 seconds | Normal flow |
| Pulser responds in 10-30 seconds | M365 shows "Checking Odoo..." progress indicator |
| Pulser does not respond within 30 seconds | M365 shows "Odoo is taking longer than expected. Try asking again or open Odoo directly." + deep link |

---

## Audit Boundaries

The cross-surface model introduces a split audit trail. Both systems log their
portion of the interaction.

### M365 Copilot Logs (Microsoft-managed)

| Field | Logged by |
|-------|-----------|
| User identity (Entra UPN) | M365 Copilot |
| Prompt text | M365 Copilot |
| Plugin invocation (Pulser selected) | M365 Copilot |
| Response rendered (host-safe, degraded, redirect) | M365 Copilot |
| Timestamp | M365 Copilot |

### Pulser Logs (InsightPulse AI-managed)

| Field | Logged by |
|-------|-----------|
| Mapped Odoo user_id | Pulser gateway |
| Tool invoked | Pulser gateway |
| Odoo models queried/modified | Pulser tool executor |
| Query results (metadata only, not full data) | Pulser gateway |
| Render class applied | Pulser M365 adapter |
| Timestamp | Pulser gateway |

### Audit Correlation

Both sides log a shared `correlation_id` (UUID) that is passed in the M365
plugin invocation headers. This allows joining the M365 audit trail with the
Pulser audit trail for end-to-end traceability.

---

## Data Residency and Consent

### Data Flow Boundaries

```
+---------------------+          +---------------------------+
| M365 Copilot        |          | Pulser (Azure SEA)        |
| (Microsoft tenant)  |   --->   | (InsightPulse AI tenant)  |
|                     |          |                           |
| Processes:          |          | Processes:                |
| - Prompt text       |          | - Odoo data (PG in SEA)   |
| - Response markdown |          | - Foundry inference        |
| - User identity     |          | - AI Search retrieval      |
+---------------------+          +---------------------------+
```

| Data element | Processed in | Stored in | Retention |
|-------------|-------------|-----------|-----------|
| User prompt | M365 (tenant region) + Pulser (SEA) | M365 audit log + Pulser audit log | Per tenant policy |
| Odoo record data | Pulser (SEA) only | PostgreSQL (SEA) | Indefinite (operational data) |
| AI Search documents | Pulser (SEA) only | Azure AI Search index (SEA) | Per index lifecycle |
| Response text | M365 (tenant region) + Pulser (SEA) | M365 audit log + Pulser audit log | Per tenant policy |
| Foundry inference | Pulser (SEA or East US, per model) | Not persisted (stateless inference) | None |

### Consent Model

| Consent type | Who grants | When |
|-------------|-----------|------|
| M365 Copilot plugin installation | Microsoft 365 admin | Plugin is installed in the tenant admin center |
| Pulser API access (Entra app consent) | Microsoft 365 admin or user (per policy) | First invocation triggers consent prompt |
| Odoo data access | Odoo administrator | User must have an active Odoo account with appropriate groups |
| Foundry model access | Platform administrator | Foundry project RBAC is pre-configured |

### Opt-Out

Individual users can disable Pulser in their M365 Copilot plugin settings.
This prevents M365 Copilot from routing prompts to Pulser but does not affect
direct access to Pulser within the Odoo interface.

---

## Capability Matrix by Surface

| Capability | Odoo (native) | M365 Copilot | Slack |
|------------|:------------:|:------------:|:-----:|
| Informational queries | Full | Full | Limited |
| Navigational deep links | Full | Full (opens Odoo) | Link only |
| Record detail cards | Full (form view) | Degraded (summary card) | Text only |
| Transactional actions | Full | Redirect to Odoo | Not supported |
| Document grounding | Full | Full | Limited |
| Chart/visualization | Full | Degraded (text summary) | Not supported |
| Multi-step workflows | Full | Redirect to Odoo | Not supported |
| File upload | Full | Redirect to Odoo | Not supported |
| Proactive notifications | Push (panel) | Push (activity feed) | Push (message) |

---

## Implementation Status

| Component | Status |
|-----------|--------|
| Pulser native Odoo panel | Active |
| M365 Agents SDK manifest | Planned (Walk stage) |
| Declarative agent registration | Planned (Walk stage) |
| M365 response adapter (render classes) | Planned (Walk stage) |
| Audit correlation (shared correlation_id) | Planned (Walk stage) |
| Slack lightweight integration | Active (read-only queries) |
