# IPAI Ask AI Assistant

## Overview

AI-powered conversational assistant for Odoo

- **Technical Name:** `ipai_ask_ai`
- **Version:** 18.0.1.1.0
- **Category:** Productivity/AI
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Ask AI Assistant
=====================

An integrated AI-powered conversational assistant that:
- Processes natural language business queries
- Accesses database and business logic contextually
- Returns intelligent responses with real-time data
- Uses message-based architecture via Discuss module
- Provides intuitive chat interface
- **AFC RAG Integration** - Semantic search over AFC Close Manager knowledge base

Features:
- Chat window component with real-time messaging
- Integration with...

## Functional Scope

### Data Models

- **ipai.ask.ai.service** (TransientModel)
  - Ask AI Service
- **afc.rag.service** (AbstractModel)
  - AFC RAG Service
- **res.config.settings** (TransientModel)
  - Fields: 2 defined
- **discuss.channel** (Model)
  - Fields: 1 defined

### Views

- : 1

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `mail` (CE Core)
- `ipai_platform_theme` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_ask_ai --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_ask_ai --stop-after-init
```

## Configuration

### System Parameters

- `afc.supabase.db_host`: db.spdtwktxdalcfigzeqrz.supabase.co
- `afc.supabase.db_name`: postgres
- `afc.supabase.db_user`: postgres
- `afc.supabase.db_password`: CONFIGURE_VIA_ODOO_UI
- `afc.supabase.db_port`: 5432
- `openai.api_key`: CONFIGURE_VIA_ODOO_UI
- `openai.embedding_model`: text-embedding-3-large

## Security

### Security Groups

- `group_ask_ai_user`: User

### Access Rules

*1 access rules defined in ir.model.access.csv*

## Integrations

- OpenAI API / Claude API (AI Assistant)
- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.1.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_ask_ai'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_ask_ai")]).state)'
```

## Data Files

- `security/security.xml`
- `security/ir.model.access.csv`
- `data/ai_channel_data.xml`
- `data/afc_config_params.xml`
- `views/ask_ai_views.xml`
- `views/res_config_settings_view.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
