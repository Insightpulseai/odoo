# IPAI Ask AI Assistant

## 1. Overview
AI-powered conversational assistant for Odoo

**Technical Name**: `ipai_ask_ai`
**Category**: Productivity/AI
**Version**: 18.0.1.1.0
**Author**: InsightPulse AI

## 2. Functional Scope

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
- Integration with discuss.channel for persistence
- Context-aware responses based on current model/view
- Support for business queries (customers, sales, etc.)
- **AFC/BIR Compliance Queries** - Philippine tax filing and financial closing
- **RAG-powered answers** - Retrieval-Augmented Generation using pgvector
- Message threading and history
- Mark as read functionality
- Keyboard shortcuts (ESC to close, Enter to send)

Technical Stack:
- OWL Components for reactive chat UI
- Discuss module integration for message storage
- Custom AI service for response generation
- **AFC RAG Service** - pgvector semantic search with Supabase integration
- SCSS styling with IPAI platform tokens

Theming:
- Uses ipai_platform_theme tokens for consistent branding
- No hardcoded colors - all styling via CSS variables
- Automatically inherits brand colors from theme modules

Dependencies:
- psycopg2 (for Supabase vector search)
- OpenAI API (for embeddings - optional, requires configuration)
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `web`
- `mail`
- `ipai_platform_theme`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.ask.ai.service`
- `modelintent.get(model, res.partner)`
- `if model_name == sale.order:`
- `elif model_name == account.move:`
- `if intent.get(filter) == unpaid and model_name == account.move:`
- `if intent.get(filter) == overdue and model_name == project.task:`
- `if model_name == res.partner:`
- `modelintent.get(model, sale.order)`
- `dbICP.get_param(afc.supabase.db_name) or os.getenv(POSTGRES_DATABASE, postgres)`
- `if intent.get(filter) == my_tasks and model_name == project.task:`
- `afc.rag.service`

## 6. User Interface
- **Views**: 5 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_ask_ai --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_ask_ai --stop-after-init
```