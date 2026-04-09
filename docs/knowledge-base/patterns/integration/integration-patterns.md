# Integration Patterns

## Pattern 1: Document Intelligence → Odoo

**Use case**: Extract data from scanned invoices/receipts and create vendor bills in Odoo.

```
Scanned document → Azure Blob Storage
→ Azure Document Intelligence (prebuilt-invoice model)
→ Extracted fields (vendor, amount, lines, dates)
→ queue_job → Odoo account.move creation
→ Human review (draft state) → Post
```

**Key decisions**:
- Async processing via queue_job (never block on AI inference)
- Create in draft state — human validates before posting
- Store extraction confidence scores for audit
- Map vendor by tax ID or name fuzzy match to res.partner

**Error handling**:
- Low confidence (<70%) → flag for manual entry
- Unknown vendor → create as draft partner, flag for review
- Duplicate detection → check existing drafts by vendor + amount + date

---

## Pattern 2: Odoo → Databricks (Analytics Extract)

**Use case**: Extract Odoo transactional data for analytics, reporting, and ML.

```
Odoo PostgreSQL → JDBC connector → Databricks
→ Bronze layer (raw tables, CDC)
→ Silver layer (cleaned, joined, business logic)
→ Gold layer (aggregated, KPI-ready)
→ Power BI semantic model → Dashboards
```

**Key decisions**:
- JDBC extract (not API) — more efficient for bulk data
- Incremental based on `write_date` column
- Schema mapping maintained in Databricks notebook
- No write-back to Odoo from Databricks

**Tables to extract** (priority):
- `account_move` + `account_move_line` (financial transactions)
- `res_partner` (customers, vendors)
- `product_template` + `product_product` (products)
- `sale_order` + `sale_order_line` (sales)
- `purchase_order` + `purchase_order_line` (procurement)
- `stock_move` (inventory movements)
- `project_task` (project tracking)

---

## Pattern 3: Entra ID → Odoo (Identity Federation)

**Use case**: Single sign-on for Odoo users via Microsoft Entra ID.

```
User → Entra ID login page → OIDC authorization code
→ Odoo auth_oidc module → Token validation
→ User matched by email → Odoo session created
```

**Key decisions**:
- OCA `auth_oidc` module for OIDC integration
- Match users by email (Entra UPN = Odoo login)
- Provisioning: manual or via SCIM (future)
- MFA enforced at Entra ID level
- Groups NOT synced automatically (Odoo groups managed separately)

**Configuration**:
- Entra app registration with redirect URI
- Client ID + secret in Key Vault
- Odoo `auth.oauth.provider` record pointing to Entra endpoints

---

## Pattern 4: Odoo → n8n (Workflow Automation)

**Use case**: Trigger external workflows when Odoo events occur.

```
Odoo event (e.g., SO confirmed) → Webhook to n8n
→ n8n workflow (Slack notification, email, external API)
→ Optional callback to Odoo (update status)
```

**Key decisions**:
- Odoo sends webhook via `base.automation` (server action → webhook)
- n8n receives, processes, and optionally calls back via JSON-RPC
- Idempotency: n8n workflows must handle duplicate webhooks
- Credentials: n8n stores Odoo API credentials, not vice versa

---

## Pattern 5: MCP Tool → Odoo (Agent Access)

**Use case**: AI agents access Odoo data and actions via MCP protocol.

```
AI Agent (Claude Code / Foundry) → MCP Tool Server
→ JSON-RPC / HTTP controller → Odoo API
→ Structured response → Agent action
```

**Key decisions**:
- MCP tools are read-heavy, write-light
- Authentication: dedicated API user with minimal permissions
- Rate limiting on Odoo controller endpoints
- Tool definitions: partner_lookup, invoice_create, journal_query, etc.
- Never expose internal model names in tool interface (abstract)

**Tool examples**:
```yaml
tools:
  - name: lookup_vendor
    description: Find vendor by name or tax ID
    input: {query: string}
    output: {id, name, tax_id, balance}

  - name: create_draft_bill
    description: Create a draft vendor bill
    input: {vendor_id, lines: [{description, amount}]}
    output: {bill_id, state, total}

  - name: get_open_receivables
    description: List unpaid customer invoices
    input: {customer_id?, days_overdue?}
    output: [{invoice_id, customer, amount, due_date, days_overdue}]
```

---

## Pattern 6: Queue-Based Async Processing

**Use case**: Handle long-running operations without blocking users.

```python
# Trigger (synchronous — returns immediately)
def action_process_batch(self):
    for record in self:
        record.with_delay(
            priority=10,
            max_retries=3,
            eta=fields.Datetime.now()
        )._do_heavy_processing()
    return {"type": "ir.actions.client", "tag": "display_notification",
            "params": {"message": "Processing queued", "type": "info"}}

# Worker (async — runs in background)
@job(default_channel="root.heavy")
def _do_heavy_processing(self):
    # Long-running logic here
    # This runs in a separate transaction
    pass
```

**Key decisions**:
- Use OCA `queue_job` module
- Configure channels for priority/concurrency
- Jobs must be idempotent
- Monitor via queue.job list view
- Alert on failed jobs (state = 'failed')
