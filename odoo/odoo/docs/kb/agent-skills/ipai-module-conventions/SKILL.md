---
name: ipai_module_conventions
description: InsightPulse AI custom module conventions and EE parity patterns
category: platform
priority: critical
version: "1.0"
---

# IPAI Module Conventions

## Module Philosophy
```
Config → OCA → Delta (ipai_*)
```
1. Config: Use Odoo built-in configuration first
2. OCA: Use vetted community modules second
3. Delta: Only create ipai_* for truly custom needs

## Naming Convention
Pattern: ipai_<domain>_<feature>
Examples:
- ipai_finance_ppm (finance domain, PPM feature)
- ipai_ai_copilot (AI domain, copilot feature)
- ipai_bir_tax_compliance (BIR domain, tax compliance)
- ipai_slack_connector (integration connector)

## Domain Prefixes
| Domain | Prefix | Examples |
|--------|--------|---------|
| AI/Agents | ipai_ai_*, ipai_agent_* | ipai_ai_core, ipai_ai_copilot |
| Finance | ipai_finance_* | ipai_finance_ppm |
| HR | ipai_hr_* | ipai_hr_payroll_ph |
| BIR Compliance | ipai_bir_* | ipai_bir_tax_compliance |
| Integrations | ipai_*_connector | ipai_slack_connector |
| Design/Theme | ipai_theme_*, ipai_design_* | ipai_design_system |

## EE Parity Pattern
Target: >=80% Enterprise Edition feature parity via CE + OCA + ipai_*
Formula: CE + OCA + ipai_* = Enterprise Parity
NEVER license Odoo Enterprise or use odoo.com IAP services.

## Thin Bridge Philosophy
ipai_* modules should be thin bridges, not monoliths:
- Inherit OCA models, don't duplicate
- Add fields/methods, don't replace
- Use _inherit, not _name (extend, don't fork)
- Minimal Python, leverage XML data/views

## Stack Rules
- CE Only: No Enterprise modules, no odoo.com IAP
- Database: Odoo uses local PostgreSQL, NOT Supabase
- Supabase: Only for n8n workflows, task bus, external integrations
- Domain: insightpulseai.com (never .net)
- Hosting: Azure Container Apps (never DigitalOcean — deprecated)

## Task Completion
Every Odoo task produces:
1. Module changes (code/views/data)
2. Install/update script
3. Health check verification
