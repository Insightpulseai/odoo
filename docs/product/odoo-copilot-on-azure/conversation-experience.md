# Conversation Experience

> Defines the copilot conversation lifecycle, launcher behavior, settings, thread continuity, and expiry policy within the Odoo web client.

---

## Thread Lifecycle

A copilot conversation thread is a sequence of user messages and assistant responses stored in `ipai.copilot.thread` and its child `ipai.copilot.message` records.

### Create

A new thread is created when:

1. The user clicks the copilot launcher and sends their first message.
2. The user explicitly starts a new conversation via the "New conversation" button in the copilot panel.
3. The previous thread has expired (see Expiry Policy below).

On creation, the thread captures:

| Field | Value | Purpose |
|-------|-------|---------|
| `user_id` | Current `res.users` record | Thread ownership |
| `company_id` | User's current company | Multi-company scoping |
| `create_date` | Server timestamp | Lifecycle tracking |
| `last_activity` | Server timestamp | Expiry calculation |
| `context_model` | Active model when thread was created | Contextual grounding |
| `context_res_id` | Active record ID (if viewing a form) | Contextual grounding |
| `state` | `active` | Lifecycle state |
| `language` | User's `lang` preference | Response language |

### Continue

An existing thread continues when:

1. The user sends a new message within the same thread.
2. The user returns to the copilot panel and their most recent active thread is still valid (not expired).
3. The user navigates to a different Odoo view -- the thread persists across page navigation (see Thread Continuity).

On each new message, `last_activity` is updated to the current server timestamp.

### Expire

A thread transitions to `expired` state when:

1. The time elapsed since `last_activity` exceeds the configured expiry duration.
2. The user explicitly closes the thread via the "End conversation" action.
3. The user logs out (see Single Logout Behavior).

Expired threads are read-only. The user can view their history but cannot append new messages. Starting a new conversation creates a fresh thread.

---

## Launcher Behavior

The copilot launcher is the entry point for conversations within the Odoo web client.

### Default Appearance

- **Position**: Floating button in the bottom-right corner of the Odoo web client.
- **Icon**: Pulser brand icon (defined in `ipai_odoo_copilot/static/src/img/`).
- **Label**: "Ask Pulser" (visible on hover).
- **State indicator**: A subtle dot indicates whether the copilot backend is reachable (green = connected, gray = unavailable).

### Activation

- **Click**: Opens the copilot panel as a slide-out drawer on the right side of the viewport.
- **Keyboard shortcut**: `Ctrl+Shift+P` (configurable) opens the panel and focuses the input field.
- **URL parameter**: `?copilot=open` opens the panel on page load (used for deep links from M365).

### Panel Layout

```
+------------------------------------------+
|  Pulser                    [New] [Close]  |
+------------------------------------------+
|                                          |
|  [Assistant] Here is the summary of      |
|  your open invoices for March...         |
|                                          |
|  [User] Show me the overdue ones         |
|                                          |
|  [Assistant] You have 3 overdue          |
|  invoices:                               |
|  - INV/2026/0039 (PHP 45,000)           |
|  - INV/2026/0041 (PHP 62,000)           |
|  - INV/2026/0042 (PHP 38,000)           |
|                                          |
+------------------------------------------+
|  [Type your message...]        [Send]    |
+------------------------------------------+
|  Settings | History                      |
+------------------------------------------+
```

### Mobile Behavior

On viewports narrower than 768px, the copilot panel opens as a full-screen overlay instead of a side drawer. The launcher button remains in the bottom-right corner. Tap-outside-to-close is disabled on mobile to prevent accidental dismissal.

---

## Settings

Users configure their copilot experience through the Settings tab at the bottom of the copilot panel.

| Setting | Options | Default | Scope |
|---------|---------|---------|-------|
| Language | User's available languages in Odoo | User's `lang` field | Per-user |
| Verbosity | `concise`, `standard`, `detailed` | `standard` | Per-user |
| Domain focus | `all`, `accounting`, `sales`, `hr`, `inventory` | `all` | Per-user, per-thread |
| Sound notifications | On / Off | Off | Per-user |
| Show copilot launcher | On / Off | On | Per-user |
| Auto-context | On / Off | On | Per-user |

### Auto-Context

When enabled, the copilot automatically includes the user's current Odoo context (active model, record ID, list filters) in the prompt sent to Foundry. This allows responses like "this invoice" to resolve correctly without the user specifying which record they mean.

When disabled, the copilot operates in a context-free mode where the user must explicitly reference records by name or number.

### Verbosity Levels

| Level | Behavior |
|-------|----------|
| `concise` | Short answers, no explanations, tables preferred over prose |
| `standard` | Balanced responses, brief explanations, structured output |
| `detailed` | Full explanations, step-by-step reasoning, citations to Odoo help docs |

Verbosity is passed as a system prompt parameter to Foundry. It does not affect which tools are available.

---

## Thread Continuity Across Page Navigation

### Behavior

When the user navigates within the Odoo web client (e.g., from the invoice list to an invoice form), the copilot panel state is preserved:

1. The panel remains open if it was open before navigation.
2. The current thread and its message history remain visible.
3. If auto-context is enabled, the `context_model` and `context_res_id` are updated to reflect the new view.

### Implementation

Thread state is stored in the browser's `sessionStorage` under the key `ipai_copilot_thread_id`. The copilot OWL component reads this value on mount and resumes the thread if it is still active.

Page navigation within the Odoo SPA does not destroy the copilot component. Full page reloads (rare in Odoo 19's SPA architecture) trigger a re-mount, but the thread ID is recovered from `sessionStorage`.

### Cross-Tab Behavior

Each browser tab maintains its own thread. Opening Odoo in a new tab starts with no active thread. Thread IDs are not synchronized across tabs.

---

## Conversation Expiry Policy

### Default Expiry

Threads expire after **8 hours** of inactivity (measured from `last_activity`). This default is based on the SAP Joule benchmark of a single workday session.

### Configurable Expiry

Administrators can adjust the expiry duration via System Parameters:

| Parameter | Default | Unit |
|-----------|---------|------|
| `ipai_copilot.thread_expiry_hours` | `8` | Hours |
| `ipai_copilot.max_thread_age_hours` | `72` | Hours |

- `thread_expiry_hours`: Inactivity timeout. Reset on each message.
- `max_thread_age_hours`: Absolute maximum thread lifetime regardless of activity. After this, the thread is force-expired.

### Expiry Check

The expiry check runs at two points:

1. **On thread resume**: When the copilot panel loads and attempts to resume a thread from `sessionStorage`, it checks `last_activity` against the current time. If expired, the thread is marked `expired` and a new thread is offered.
2. **Cron job**: A scheduled action (`ipai_copilot.cron_expire_threads`) runs every hour to mark stale threads as `expired` in bulk. This handles threads abandoned without explicit closure.

---

## Multiple Active Threads

A user may have multiple threads in `active` state simultaneously. This occurs when:

1. The user starts a new conversation without closing the previous one.
2. The user accesses the copilot from different contexts (e.g., one thread about invoices, another about HR).

### Thread Switching

The History tab in the copilot panel lists all active and recent expired threads for the current user. Each entry shows:

- First message (truncated to 80 characters)
- `last_activity` timestamp
- `context_model` label (e.g., "Invoices", "Expenses")
- State badge (`active` or `expired`)

Clicking an active thread switches the panel to that thread. Clicking an expired thread opens it in read-only mode.

### Thread Limit

A maximum of **10 active threads** per user is enforced. If the user attempts to create an 11th, the oldest active thread is automatically expired. This limit is configurable via `ipai_copilot.max_active_threads`.

---

## Single Logout Behavior

When a user logs out of Odoo:

1. All active threads for that user are marked as `expired` with `close_reason=logout`.
2. The `sessionStorage` copilot state is cleared.
3. Thread message history is preserved in the database for audit purposes.
4. On next login, the user starts with no active thread. They can view their previous threads via History.

If the user's Entra session is revoked (e.g., by an administrator), the Odoo session becomes invalid on the next request. The copilot panel detects the invalid session and shows a "Session expired. Please log in again." message.

---

## Conversation History and Audit Trail

### User-Facing History

Users can access their conversation history through the History tab. History shows threads from the last 90 days (configurable via `ipai_copilot.history_retention_days`).

### Audit Trail

All copilot messages are stored with:

| Field | Purpose |
|-------|---------|
| `thread_id` | Parent thread reference |
| `role` | `user` or `assistant` |
| `content` | Message text |
| `tool_calls` | JSON array of tools invoked (if any) |
| `create_date` | Server timestamp |
| `token_count` | Approximate token usage for the message |

Transactional actions triggered via copilot are additionally logged in `ipai.copilot.audit.log` (see `copilot-auth-boundaries.md`).

### Retention

| Data Type | Retention | Configurable |
|-----------|-----------|-------------|
| Active thread messages | Until thread expires | Via expiry settings |
| Expired thread messages | 90 days | `ipai_copilot.history_retention_days` |
| Audit log entries | 365 days | `ipai_copilot.audit_retention_days` |
| Purged after retention | Hard delete via cron | `ipai_copilot.cron_purge_history` |

Audit log entries are retained independently of thread messages and are subject to longer retention periods for compliance.

---

*Last updated: 2026-03-28*
