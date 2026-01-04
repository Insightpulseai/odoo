# IPAI AI Studio - ChatGPT App

MCP server that exposes Odoo AI Studio capabilities to ChatGPT.

## Features

- **Natural Language Customization**: Add fields, create automations via chat
- **Data Queries**: Ask questions about your Odoo data
- **Module Management**: Check module status and info
- **Widget UI**: Embedded interface for ChatGPT

## Quick Start

```bash
# Install dependencies
npm install

# Configure environment
export ODOO_BASE_URL="https://your-odoo-instance.com"
export ODOO_DB="your_database"
export ODOO_LOGIN="admin@example.com"
export ODOO_PASSWORD="your_password"

# Start server
npm start
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8787` |
| `ODOO_BASE_URL` | Odoo instance URL | `https://erp.insightpulseai.net` |
| `ODOO_DB` | Database name | `prod` |
| `ODOO_LOGIN` | Admin user email | (required) |
| `ODOO_PASSWORD` | Admin password | (required) |
| `IPAI_API_TOKEN` | Optional API token for public endpoints | |

## Endpoints

- `GET /health` - Health check
- `GET /widget` - Widget HTML
- `POST /mcp` - MCP protocol endpoint

## Tools

### `odoo_ai_studio_process_command`
Process a natural language command.

### `odoo_ai_studio_analyze`
Analyze a command without executing.

### `odoo_ai_studio_create_field`
Create a custom field on a model.

### `odoo_ai_studio_query`
Execute a data query.

### `odoo_module_info`
Get module information.

## ChatGPT Integration

1. Enable Developer Mode in ChatGPT settings
2. Create a new app pointing to your MCP endpoint
3. Use the widget for visual interaction

## Odoo Requirements

This app requires the `ipai_studio_ai` module with API controllers:
- `/ipai_studio_ai/api/process_command`
- `/ipai_studio_ai/api/analyze`
- `/ipai_studio_ai/api/create_field`
- `/ipai_studio_ai/api/query`
- `/ipai_studio_ai/api/module_info`

## License

MIT - InsightPulse AI
