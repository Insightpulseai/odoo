---
title: "Odoo Copilot User Guide"
kb_scope: "general-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Odoo Copilot User Guide

## Overview

The Odoo Copilot is an AI-powered assistant integrated directly into the Odoo CE 18.0 interface. It helps users navigate the system, answer questions about business data, generate reports, and perform routine actions through natural language commands.

The Copilot is powered by the `ipai_ai_copilot` module and connects to large language models via the MCP (Model Context Protocol) coordination layer.

---

## Operating Modes

The Copilot operates in two distinct modes, each with different capabilities and safety guarantees.

### Advisory Mode (Default)

In Advisory Mode, the Copilot can:

- **Answer questions** about Odoo functionality and configuration
- **Explain data** by reading and summarizing records you have access to
- **Generate reports** by querying data and formatting results
- **Suggest actions** by recommending next steps based on context
- **Draft content** such as email templates, product descriptions, or notes

In Advisory Mode, the Copilot **cannot**:

- Create, modify, or delete any records
- Change system configuration
- Execute workflows or transitions
- Access data outside your permission scope

Advisory Mode is the default because it is safe. The Copilot reads data but never writes. All suggestions require your manual action to implement.

### Action Mode (Explicit Activation)

In Action Mode, the Copilot can additionally:

- **Create records** such as invoices, sales orders, purchase orders
- **Update fields** on existing records
- **Execute actions** like confirming orders, posting journal entries
- **Run automations** such as sending emails or triggering workflows

Action Mode requires:

1. Explicit activation by the user (toggle in the Copilot panel)
2. Confirmation before each destructive or irreversible action
3. Appropriate user permissions (Copilot respects Odoo RBAC)
4. Audit trail logging of all actions taken

**Important**: The Copilot never bypasses access controls. If you cannot perform an action manually, the Copilot cannot perform it for you.

---

## Accessing the Copilot

### From the Odoo Interface

1. **Copilot Panel**: Click the Copilot icon in the top-right toolbar of any Odoo view. A side panel opens for conversational interaction.

2. **Inline Assist**: In form views, hover over a field and click the small AI icon to get contextual help for that specific field.

3. **Report Assist**: In list views and pivot tables, use the "Ask Copilot" button to generate natural language summaries of the displayed data.

4. **Keyboard Shortcut**: Press `Ctrl+Shift+K` (or `Cmd+Shift+K` on macOS) to toggle the Copilot panel from any screen.

### Context Awareness

The Copilot is context-aware. It knows:

- Which Odoo module and view you are currently in
- Which record you are viewing or editing
- Your user role and permissions
- The current company context (for multi-company setups)

This means you can ask questions like "What is the total on this order?" without specifying which order — the Copilot infers it from your current screen.

---

## Common Use Cases

### Accounting and Finance

**Advisory examples:**
- "Show me all unpaid invoices older than 30 days"
- "What is our accounts receivable aging summary?"
- "Explain the journal entries for this invoice"
- "What tax rate applies to this product for domestic sales?"
- "Summarize this month's expenses by category"

**Action examples (requires Action Mode):**
- "Create a credit note for invoice INV/2026/0042"
- "Post all draft journal entries for March 2026"
- "Register a payment of PHP 50,000 against invoice INV/2026/0099"
- "Create a bank reconciliation for BDO account ending March 15"

### Sales and CRM

**Advisory examples:**
- "Show my pipeline by stage with total expected revenue"
- "Which leads have not been contacted in the last 7 days?"
- "What is the win rate for leads from the website channel?"
- "Compare this quarter's quotation volume to last quarter"

**Action examples:**
- "Create a quotation for partner ABC Corp with Product X, quantity 100"
- "Convert this lead to an opportunity and assign it to the Sales team"
- "Send the quotation PDF to the customer via email"
- "Mark this opportunity as won with a revenue of PHP 1,200,000"

### Inventory and Purchasing

**Advisory examples:**
- "Which products are below their reorder point?"
- "Show stock levels for Warehouse Manila"
- "What is the average lead time for supplier XYZ?"
- "List all pending receipts expected this week"

**Action examples:**
- "Create a purchase order for 500 units of SKU-001 from Supplier ABC"
- "Confirm all draft purchase orders for this week"
- "Process the incoming shipment for PO/2026/0015"

### Human Resources

**Advisory examples:**
- "How many employees are in the Engineering department?"
- "Show me all employees whose contracts expire in the next 90 days"
- "What are the leave balances for my team?"

**Action examples:**
- "Create a leave request for March 20-21 (vacation)"
- "Approve all pending leave requests for my direct reports"

---

## Query Language

The Copilot understands natural language in English and Filipino (Tagalog). You do not need to learn specific commands or syntax.

### Tips for Better Results

1. **Be specific about scope**: "Show invoices from January 2026" is better than "Show recent invoices."

2. **Name entities clearly**: Use partner names, product codes, or reference numbers when available. "Invoice for ABC Corp" is better than "that invoice."

3. **Specify the output format**: "Show as a table" or "Summarize in bullet points" helps the Copilot format responses usefully.

4. **Use filters**: "Unpaid invoices over PHP 100,000 for Q1 2026" gives precise results.

5. **Ask follow-ups**: The Copilot maintains conversation context. After a query, you can say "Now filter that to just Manila warehouse" without repeating the full question.

### What the Copilot Cannot Do

- **Access external systems**: The Copilot only reads data within Odoo. It cannot query your bank, BIR eFPS, or external websites.
- **Predict the future**: It can show trends and averages, but it does not forecast.
- **Override permissions**: It respects your Odoo access rights strictly.
- **Undo committed actions**: Once a journal entry is posted or an order is confirmed, the Copilot cannot reverse it without creating the appropriate counter-document (credit note, return, etc.).
- **Handle file uploads**: The Copilot works with text. It cannot process uploaded images or PDFs (use the OCR service for that).

---

## Security and Privacy

### Data Access

- The Copilot accesses Odoo data through the same ORM and access control layer as the web interface.
- It never queries the database directly.
- Record rules and access rights apply identically.
- Multi-company security trimming is enforced.

### Audit Trail

- All Copilot interactions are logged in the `ipai.copilot.log` model.
- Action Mode operations create standard Odoo audit log entries via the `auditlog` OCA module.
- Logs include: timestamp, user, query, response summary, actions taken, records affected.

### Data Handling

- Queries are processed via the MCP coordination layer.
- Conversation context is maintained per session and cleared on logout.
- No user data is stored outside the Odoo database and MCP session cache.
- The AI model does not retain conversation data between sessions.

---

## Configuration (For Administrators)

### Enabling the Copilot

The Copilot is enabled by installing the `ipai_ai_copilot` module:

```
odoo-bin -d <database> -i ipai_ai_copilot --stop-after-init
```

### User Permissions

| Group | Advisory Mode | Action Mode | Configuration |
|-------|:------------:|:-----------:|:-------------:|
| Base User | Yes | No | No |
| Copilot User | Yes | Yes | No |
| Copilot Admin | Yes | Yes | Yes |

Assign users to groups via Settings > Users & Companies > Groups.

### Configuration Options

Access via Settings > Technical > AI Copilot:

- **Default Mode**: Advisory or Action (recommended: Advisory)
- **Action Confirmation**: Always, Destructive Only, or Never (recommended: Always)
- **Log Retention**: Days to retain conversation logs (default: 90)
- **Rate Limiting**: Maximum queries per user per hour (default: 100)
- **Allowed Models**: Restrict which Odoo models the Copilot can query

### MCP Connection

The Copilot connects to the MCP coordination service at `mcp.insightpulseai.com`. The connection is configured via environment variables:

- `MCP_ENDPOINT` — MCP service URL
- `MCP_API_KEY` — Authentication key (stored in Azure Key Vault)

These are set at the container level and should never be hardcoded in Odoo configuration.

---

## Troubleshooting

### Copilot Panel Does Not Appear

1. Verify `ipai_ai_copilot` is installed: Settings > Apps > search "copilot"
2. Check user belongs to at least the "Copilot User" group
3. Clear browser cache and reload (`Ctrl+Shift+R`)
4. Check browser console for JavaScript errors

### Copilot Returns "I don't have access to that data"

This means your Odoo user lacks read permission on the queried model. Contact your administrator to review your access rights.

### Copilot Is Slow to Respond

- The MCP service may be experiencing high load. Check `status.insightpulseai.com`.
- Complex queries over large datasets take longer. Try adding date or category filters.
- Network latency can be a factor. The MCP service is hosted in Southeast Asia (Azure southeastasia region).

### Action Mode Is Grayed Out

Your user is not in the "Copilot User" group. Contact your administrator.

### Copilot Gives Incorrect Answers

- Report the issue via the feedback button (thumbs down icon) on the response.
- Include the query and expected answer.
- The Copilot is advisory — always verify critical data against the source records.

---

## Feedback and Improvement

The Copilot improves based on usage patterns and feedback:

- **Thumbs up/down**: Quick feedback on response quality.
- **Correction**: If the Copilot misunderstands, rephrase and the system learns the pattern.
- **Feature requests**: Submit via the #copilot-feedback Slack channel.

---

## Limitations and Disclaimer

The Odoo Copilot is an AI assistant. It can make mistakes. Critical business decisions, financial reports for external filing, and regulatory compliance actions should always be verified by a qualified professional.

The Copilot does not replace:
- Professional accounting judgment
- Legal or tax advice
- BIR filing verification
- Audit procedures

Use it as a productivity tool, not as a sole source of truth.
