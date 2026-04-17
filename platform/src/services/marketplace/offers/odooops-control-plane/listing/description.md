# OdooOps Control Plane

> **DRAFT** — Enterprise parity claims require verification against live modules.

## What it does

OdooOps Control Plane transforms Odoo Community Edition into a full enterprise operations platform with AI-native capabilities. It combines the stability of Odoo CE 18 with OCA community modules and custom InsightPulseAI extensions to deliver enterprise-grade ERP without enterprise licensing costs.

## Key capabilities

### Enterprise parity without enterprise licensing
- 80%+ Odoo Enterprise feature coverage via CE + OCA + custom modules
- Bank reconciliation, financial reporting, asset management, payroll
- Helpdesk, approvals, planning, and timesheet management
- No Odoo Enterprise license required

### AI-native operations
- Built-in AI copilot for natural language ERP interaction
- Document OCR with PaddleOCR for invoice and receipt processing
- Agentic workflows powered by Claude and GPT models
- RAG-based knowledge retrieval over company documents

### Philippine BIR compliance
- Automated BIR form generation (1601-C, 2316, Alphalist, 2550M/Q)
- TRAIN law tax computation
- SSS, PhilHealth, Pag-IBIG contribution calculation
- Month-end closing automation

### Automation and integration
- n8n workflow automation (self-hosted)
- Slack integration for ChatOps
- Apache Superset for BI dashboards
- Microsoft 365 integration (calendar, Teams, Entra ID SSO)

## Architecture

Self-hosted on DigitalOcean with PostgreSQL 16, containerized via Docker. Supports single-tenant dedicated infrastructure for enterprise customers.

## Who it's for

- Philippine businesses needing BIR-compliant ERP
- Finance shared service centers
- Media and advertising agencies
- Professional services firms
- Companies seeking Odoo Enterprise alternatives
