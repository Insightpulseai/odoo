# IPAI AI Tools

Built-in tools for AI agents to execute business actions.

## Overview

This module provides a collection of tools that AI agents can execute to perform business actions in Odoo. Each tool is permission-gated, fully audited, and supports dry-run mode for testing.

## Features

- **CRM Tools**: Create, update, and search leads
- **Calendar Tools**: Create, update, and search events
- **Sale Tools**: Create and search sale orders
- **Permission Gating**: Tools tied to Odoo security groups
- **Dry-Run Mode**: Test actions without making changes
- **Full Audit Trail**: Every invocation is logged

## Installation

```bash
# Install via Docker (requires ipai_ai_agent_builder, crm, calendar, sale)
docker compose exec odoo-core odoo -d odoo_core -i ipai_ai_tools --stop-after-init
```

## Available Tools

### CRM Tools

| Tool Key | Description | Required Group |
|----------|-------------|----------------|
| `crm_create_lead` | Create a new CRM lead | Sales / User |
| `crm_update_lead` | Update an existing lead | Sales / User |
| `crm_search_leads` | Search for leads | Sales / User |

### Calendar Tools

| Tool Key | Description | Required Group |
|----------|-------------|----------------|
| `calendar_create_event` | Create a calendar event | Internal User |
| `calendar_update_event` | Update an existing event | Internal User |
| `calendar_search_events` | Search for events | Internal User |

### Sale Tools

| Tool Key | Description | Required Group |
|----------|-------------|----------------|
| `sale_create_order` | Create a sale order | Sales / User |
| `sale_search_orders` | Search for orders | Sales / User |

## Tool Execution Contract

### Permission Gating

Each tool is associated with Odoo security groups. The executor checks:

1. User belongs to required group(s)
2. Company/record rules are satisfied
3. Tool is active

### Audit Logging

Every tool invocation creates a `ipai.ai.tool.call` record with:

- Input parameters (JSON)
- Output result (JSON)
- Status (pending, success, error, dry_run)
- Execution time (ms)
- User and timestamp

### Dry-Run Mode

Tools supporting dry-run validate inputs and return what would happen without making changes:

```python
result = tool.execute(env, input_data, dry_run=True)
# result = {"dry_run": True, "would_create": {...}, "message": "..."}
```

## Creating Custom Tools

1. Create a Python function:

```python
# addons/my_module/tools/my_tools.py
def my_tool(env, input_data, dry_run=False):
    """Tool description."""
    # Validate inputs
    # Execute action
    # Return result dict
```

2. Register the tool:

```xml
<record id="tool_my_tool" model="ipai.ai.tool">
    <field name="key">my_tool</field>
    <field name="name">My Tool</field>
    <field name="description">What this tool does</field>
    <field name="python_entrypoint">my_module.tools.my_tools:my_tool</field>
    <field name="parameters_schema">{...}</field>
    <field name="dry_run_supported" eval="True"/>
</record>
```

3. Assign to topics in your agent configuration.

## Dependencies

- Odoo: `ipai_ai_agent_builder`, `crm`, `calendar`, `sale`

## License

LGPL-3
