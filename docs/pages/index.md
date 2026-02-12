# InsightPulse AI — Odoo 19 CE Platform

Documentation portal for the `odoo` monorepo — the InsightPulse AI ERP platform built on Odoo 19 CE + OCA.

## Quick Links

- [Getting Started](getting-started.md) — Clone, bootstrap, and run the dev environment
- [Architecture](architecture.md) — High-level system overview
- [Developer Guide](developer-guide.md) — Conventions, branching, testing, CI
- [Modules](modules.md) — IPAI modules and OCA addons
- [Deployment Timeline](deployment-timeline.md) — Actual deployment milestones with dates
- [EE Parity Gate](ee-parity-gate.md) — Enterprise Edition parity assessment
- [Runbooks](runbooks.md) — Operational procedures

## Stack Overview

| Component | Technology |
|-----------|------------|
| **ERP** | Odoo 19 CE + OCA |
| **Database** | PostgreSQL 16 |
| **Automation** | n8n |
| **Chat** | Slack |
| **External DB** | Supabase |
| **BI** | Apache Superset |
| **OCR** | ipai_ocr_gateway (Tesseract/GCV/Azure) |
| **AI** | ipai_ai_agent_builder (ChatGPT/Gemini) |
| **Mail** | Zoho Mail SMTP |
| **Hosting** | DigitalOcean |
| **Domain** | `insightpulseai.com` |
| **Docs** | GitHub Pages + Primer design system |

## Repository Structure

```
odoo/
├── addons/           # Odoo modules (ipai_*, OCA)
├── apps/             # Node.js applications
├── packages/         # Shared packages
├── spec/             # Spec bundles (PRD, plans)
├── scripts/          # Automation scripts
├── docker/           # Docker configurations
├── docs/             # Documentation
├── mcp/              # MCP servers
└── .github/          # CI/CD workflows
```

## What Ships Now (2026-02-11)

| Module | Description |
|--------|-------------|
| `ipai_finance_ppm` | Clarity PPM parity — WBS, logframe, analytic integration |
| `ipai_finance_ppm_umbrella` | Full seed: 9 employees, 22 BIR forms, 36 closing tasks, RACI |
| `ipai_ocr_gateway` | Multi-provider OCR (Tesseract, Google Vision, Azure) |
| `ipai_ai_agent_builder` | AI agents with topics, tools, RAG (Joule parity) |
| `ipai_ops_mirror` | Supabase SSOT sync for ops data |
| `ipai_bir_tax_compliance` | 36 eBIRForms with automated computation |
| `ipai_month_end` | SAP AFC-style month-end with PH holiday awareness |

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/Insightpulseai/odoo/issues)
- **Wiki**: [Internal runbooks and notes](https://github.com/Insightpulseai/odoo/wiki)
