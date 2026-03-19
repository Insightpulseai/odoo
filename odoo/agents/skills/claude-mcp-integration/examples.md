# Claude MCP Integration — Examples

## Example 1: Odoo Sales MCP Server

```
MCP Server: odoo-sales
Tools: 6 (4 always loaded, 2 deferred)
Auth: Managed identity → Odoo REST API

Always loaded:
  - odoo_sale_order_list: "List sale orders with filters (state, date range, partner)"
  - odoo_sale_order_get: "Get sale order details by ID including line items"
  - odoo_sale_order_create: "Create new sale order with partner, lines, and pricelist"
  - odoo_sale_order_confirm: "Confirm draft sale order (transitions to 'sale' state)"

Deferred:
  - odoo_sale_report_summary: "Generate sales summary report for date range"
  - odoo_sale_order_cancel: "Cancel sale order with reason (requires manager context)"

Discovery: enabled (search tool for deferred)
```

## Example 2: Azure Key Vault MCP Server

```
MCP Server: azure-keyvault
Tools: 3 (all always loaded — small set)
Auth: Managed identity (zero-secret)

  - azure_keyvault_get_secret: "Retrieve secret value by name from vault"
  - azure_keyvault_list_secrets: "List secret names (not values) with metadata"
  - azure_keyvault_set_secret: "Create or update secret (requires write permission)"

Discovery: disabled (only 3 tools)
```
