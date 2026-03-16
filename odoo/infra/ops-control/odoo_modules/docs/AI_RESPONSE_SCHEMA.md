# IPAI Ask AI - Response Schema & Contracts

This document defines the structured contracts between the Odoo frontend, backend, and external AI service.

## Overview

The AI Copilot uses a structured JSON response format to enable:
- Markdown-rendered message content
- Clickable citations to Odoo records
- Executable actions (create, update, navigate, search)
- Preview diffs for write operations

---

## Request Schema

### `/ask_ai/execute` Endpoint

**Request Payload:**
```json
{
  "conversation_id": 123,
  "prompt": "Create an invoice for partner ABC",
  "context": {
    "model": "res.partner",
    "res_id": 456,
    "res_ids": [456, 457],
    "view_type": "form",
    "action_id": 789,
    "display_name": "Partner ABC"
  },
  "mode": "do"
}
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversation_id` | integer | No | Existing conversation ID. Creates new if not provided. |
| `prompt` | string | Yes | User's natural language input |
| `context` | object | No | Current Odoo context |
| `mode` | string | No | Interaction mode: `ask`, `do`, `explain`. Default: `ask` |

### Context Object

```json
{
  "model": "res.partner",
  "res_id": 123,
  "res_ids": [123, 124, 125],
  "view_type": "form",
  "action_id": 456,
  "display_name": "John Doe",
  "model_name": "Contact",
  "fields": {
    "name": "John Doe",
    "email": "john@example.com",
    "company_id": {
      "id": 1,
      "display_name": "ACME Corp"
    }
  }
}
```

---

## Response Schema

### AI Backend Response Format

The AI backend MUST return this JSON structure:

```json
{
  "message": "I've prepared a draft invoice for Partner ABC...",
  "citations": [
    {
      "model": "res.partner",
      "res_id": 456,
      "label": "Partner ABC",
      "field": "name"
    }
  ],
  "actions": [
    {
      "type": "create",
      "label": "Create Invoice",
      "description": "Creates a new customer invoice",
      "payload": {
        "model": "account.move",
        "values": {
          "partner_id": 456,
          "move_type": "out_invoice"
        }
      },
      "preview_diff": {
        "partner_id": { "old": null, "new": "Partner ABC" },
        "move_type": { "old": null, "new": "Customer Invoice" }
      }
    }
  ],
  "tokens": {
    "prompt": 150,
    "completion": 200
  }
}
```

### Message Content

The `message` field supports GitHub-flavored Markdown:
- Headers (`#`, `##`, `###`)
- Bold (`**text**`)
- Italic (`*text*`)
- Code blocks (``` \`\`\`language ```)
- Inline code (`` `code` ``)
- Lists (ordered and unordered)
- Blockquotes (`> quote`)
- Tables
- Links (`[text](url)`)

---

## Citations Schema

Citations reference Odoo records mentioned in the response.

```json
{
  "model": "res.partner",
  "res_id": 123,
  "label": "John Doe",
  "field": "name"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | Odoo model name |
| `res_id` | integer | Yes | Record ID |
| `label` | string | Yes | Human-readable label |
| `field` | string | No | Specific field referenced |

**UI Behavior:**
- Rendered as clickable chips below the message
- Clicking navigates to the record form view
- Icon determined by model type

---

## Actions Schema

Actions are executable operations the user can trigger.

### Base Action Structure

```json
{
  "type": "create|update|navigate|search",
  "label": "Button label",
  "description": "What this action does",
  "payload": {},
  "preview_diff": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Action type: `create`, `update`, `navigate`, `search` |
| `label` | string | Yes | Button label text |
| `description` | string | No | Tooltip/description |
| `payload` | object | Yes | Type-specific parameters |
| `preview_diff` | object | No | Before/after preview (for create/update) |

### Action Type: Create

Creates a new record.

```json
{
  "type": "create",
  "label": "Create Invoice",
  "payload": {
    "model": "account.move",
    "values": {
      "partner_id": 123,
      "move_type": "out_invoice",
      "invoice_line_ids": [
        [0, 0, {
          "name": "Product A",
          "quantity": 1,
          "price_unit": 100.00
        }]
      ]
    }
  },
  "preview_diff": {
    "partner_id": { "old": null, "new": "Partner Name" },
    "move_type": { "old": null, "new": "Customer Invoice" }
  }
}
```

### Action Type: Update

Updates existing record(s).

```json
{
  "type": "update",
  "label": "Update Status",
  "payload": {
    "model": "sale.order",
    "res_id": 456,
    "values": {
      "state": "done",
      "note": "Completed by AI"
    }
  },
  "preview_diff": {
    "state": { "old": "draft", "new": "done" },
    "note": { "old": "", "new": "Completed by AI" }
  }
}
```

For bulk updates:
```json
{
  "type": "update",
  "label": "Archive Selected",
  "payload": {
    "model": "res.partner",
    "res_ids": [1, 2, 3],
    "values": {
      "active": false
    }
  }
}
```

### Action Type: Navigate

Opens a record or view.

```json
{
  "type": "navigate",
  "label": "Open Invoice",
  "payload": {
    "model": "account.move",
    "res_id": 789,
    "view_type": "form"
  }
}
```

For search/list views:
```json
{
  "type": "navigate",
  "label": "View All Invoices",
  "payload": {
    "model": "account.move",
    "domain": [["partner_id", "=", 123]],
    "view_type": "list"
  }
}
```

### Action Type: Search

Performs a search and returns results.

```json
{
  "type": "search",
  "label": "Find Overdue",
  "payload": {
    "model": "account.move",
    "domain": [
      ["state", "=", "posted"],
      ["payment_state", "!=", "paid"],
      ["invoice_date_due", "<", "2024-01-01"]
    ],
    "limit": 10,
    "fields": ["name", "partner_id", "amount_total"]
  }
}
```

---

## Preview Diff Schema

Shows before/after values for write operations.

```json
{
  "field_name": {
    "old": "previous value",
    "new": "new value"
  }
}
```

**UI Rendering:**
- `old: null` → Shows as addition (green)
- `new: null` → Shows as removal (red)
- Both present → Shows as change (yellow)

**Example:**
```json
{
  "name": { "old": "Draft Order", "new": "SO-2024-001" },
  "state": { "old": "draft", "new": "sale" },
  "date_order": { "old": null, "new": "2024-01-15" },
  "note": { "old": "Old note", "new": null }
}
```

---

## Interaction Modes

### Ask Mode (`mode: "ask"`)
- Read-only queries
- Explanations and summaries
- No actions should be proposed
- Citations encouraged

### Do Mode (`mode: "do"`)
- Actions can be proposed
- All write actions MUST include `preview_diff`
- User confirmation required before execution

### Explain Mode (`mode: "explain"`)
- Detailed analysis
- Rich citations
- May include navigation actions
- No write actions

---

## Security Constraints

### Blocked Models
The following models are blocked by default and cannot be modified:
- `ir.model`
- `ir.model.fields`
- `ir.rule`
- `ir.config_parameter`
- `res.users`
- `ir.actions.server`

### Validation Rules
1. Model must exist in the Odoo instance
2. User must have appropriate access rights
3. Field values must pass Odoo's validation
4. Relational field IDs must reference valid records

---

## Error Response

When errors occur:

```json
{
  "error": "Description of the error",
  "conversation_id": 123,
  "user_message_id": 456
}
```

Common errors:
- `"No prompt provided"`
- `"Conversation not found"`
- `"AI service timeout. Please try again."`
- `"Actions on ir.model are not allowed"`
- `"You do not have permission to create sale.order records"`

---

## Token Usage

Optional token tracking for cost monitoring:

```json
{
  "tokens": {
    "prompt": 150,
    "completion": 200
  }
}
```

Stored in `ask.ai.message` for analytics.

---

## Example Conversation Flow

**User:** "Show me all unpaid invoices for this customer"

**AI Response:**
```json
{
  "message": "I found **3 unpaid invoices** for Partner ABC with a total of **$1,500.00**:\n\n| Invoice | Date | Amount | Days Overdue |\n|---------|------|--------|---------------|\n| INV/2024/001 | Jan 15 | $500 | 30 |\n| INV/2024/002 | Jan 20 | $750 | 25 |\n| INV/2024/003 | Feb 01 | $250 | 13 |",
  "citations": [
    { "model": "account.move", "res_id": 101, "label": "INV/2024/001" },
    { "model": "account.move", "res_id": 102, "label": "INV/2024/002" },
    { "model": "account.move", "res_id": 103, "label": "INV/2024/003" }
  ],
  "actions": [
    {
      "type": "navigate",
      "label": "View All",
      "payload": {
        "model": "account.move",
        "domain": [["partner_id", "=", 456], ["payment_state", "!=", "paid"]],
        "view_type": "list"
      }
    },
    {
      "type": "navigate",
      "label": "Send Reminder",
      "payload": {
        "model": "mail.compose.message",
        "context": { "default_partner_ids": [456] }
      }
    }
  ]
}
```

---

## Implementation Checklist

### Frontend (OWL)
- [ ] Parse and render markdown content
- [ ] Display citation chips with model icons
- [ ] Render action buttons with type-specific styling
- [ ] Show diff preview on action expansion
- [ ] Execute actions via `/ask_ai/execute_action`
- [ ] Handle streaming responses (future)

### Backend (Odoo)
- [ ] Validate action permissions before execution
- [ ] Apply blocked/allowed model filtering
- [ ] Execute ORM operations safely
- [ ] Return appropriate error messages
- [ ] Log token usage and actions

### AI Service
- [ ] Return valid JSON structure
- [ ] Include `preview_diff` for all write actions
- [ ] Limit citations to relevant records
- [ ] Respect mode constraints (ask vs do vs explain)
- [ ] Handle context-aware responses
