# Pulser MCP Capability Matrix

This matrix defines the authoritative tool plane for the Pulser Assistant, aligning with the Dynamics 365 ERP MCP Server benchmark.

## Architecture Context
- **Transport**: Stateless HTTP / SSE via FastMCP
- **Orchestration**: Microsoft AI Foundry + Agent Framework
- **Execution Layer**: Odoo JSON-RPC + Databricks SQL/Genie

---

## 1. Data Tools (Transactional Plane)
*Mirrors: D365 `data_*` tools for direct record manipulation.*

| Tool Name | Category | Auth Mode | Allowed Clients | Target Workflow | Eval Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `odoo_find_model` | Data | Delegated | Sidecar, Teams | Discovery | Pass |
| `odoo_get_model_fields`| Data | Delegated | Sidecar, Teams | Discovery | Pass |
| `odoo_search_read` | Data | Delegated | All | Search/Reporting | Pass |
| `odoo_get_record` | Data | Delegated | All | Refinement | Pass |
| `odoo_create` | Data (W) | Delegated/Approval | Teams, Dev | Entry | Pending |
| `odoo_write` | Data (W) | Delegated/Approval | Teams, Dev | Updates | Pending |
| `odoo_unlink` | Data (D) | Managed ID | Dev Only | Cleanup | Restricted |

---

## 2. Form & UI Tools (Navigation Plane)
*Mirrors: D365 `form_*` tools for client-bound context.*

| Tool Name | Category | Auth Mode | Allowed Clients | Target Workflow | Eval Coverage |
| :--- | :--- | :--- | : :--- | :--- | :--- |
| `odoo_find_action` | Form | Delegated | Sidecar | Navigation | Pass |
| `odoo_get_view_model` | Form | Delegated | Sidecar | UI-Assists | Pass |
| `odoo_call_method` | Action | Delegated/Approval | All | Business logic | Pass |

---

## 3. Action Tools (Orchestration Plane)
*Mirrors: D365 `api_invoke_action` for headless logic.*

| Tool Name | Category | Auth Mode | Allowed Clients | Target Workflow | Eval Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `odoo_find_server_actions` | Action | Delegated | Teams, Dev | Batch logic | Pass |
| `odoo_invoke_server_action`| Action | Delegated/Approval | Teams, Dev | Promotion/Close | Pending |

---

## 4. Compliance Tools (IPAI Bridge Mode)
*Specific to Philippine BIR compliance (Competitive Moat).*

| Tool Name | Category | Auth Mode | Allowed Clients | Target Workflow | Eval Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `bir_get_2550q_data` | Compliance | Managed ID | Finance Agent | VAT Filing | Pass |
| `bir_get_missing_2307` | Compliance | Managed ID | Finance Agent | WHT Chaser | Pass |
| `bir_prepare_filing_zip` | Compliance | Service Prin. | Filing Bridge | Submission | NEW |

---

## 5. Intelligence Tools (Analytics Plane)
*Mirrors: D365 "Chat with F&O Data" via Databricks/Genie.*

| Tool Name | Category | Auth Mode | Allowed Clients | Target Workflow | Eval Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `databricks_genie_query` | Analytics | Service Prin. | Exec Agent | Decisioning | NEW |
| `databricks_sql_summary` | Analytics | Managed ID | All | Trend Analysis | NEW |

---

## Governance Rules
1. **Safety First**: Any tool marked `(W)` or `(D)` must have mandatory human-in-the-loop approval unless the policy allows for automated small-value mutations.
2. **Authority Split**: No intelligence tool may write directly to the Transactional Plane. All writes must go through the Odoo Action/Data tools.
3. **Traceability**: Every MCP tool execution must emit a trace ID back to the **Pulser Cloud Ops** monitoring plane.
