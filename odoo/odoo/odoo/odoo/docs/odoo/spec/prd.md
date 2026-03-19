# PRD – InsightPulseAI Odoo 18 CE/OCA Implementation Handbook

**Product:** Documentation portal/handbook
**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## Section 0: Assumptions

### 0.1 Infrastructure Assumptions

| Component | Assumption |
|-----------|------------|
| **Odoo Version** | 18.0 Community Edition (latest stable) |
| **PostgreSQL** | 15.x (Odoo) + Supabase (analytics) |
| **Hosting** | DigitalOcean droplets or DOKS |
| **CI/CD** | GitHub Actions |
| **Container Registry** | GitHub Container Registry (ghcr.io) |

### 0.2 Skill Assumptions

| Audience | Assumed Knowledge |
|----------|-------------------|
| **Finance Users** | Basic Odoo accounting, double-entry concepts |
| **Project Managers** | Project management fundamentals, WBS |
| **Developers** | Python, XML, OCA development patterns |
| **DevOps** | Docker, nginx, PostgreSQL, CI/CD |
| **Analysts** | SQL, Superset, basic data modeling |

### 0.3 Language Assumptions

- **Primary**: English
- **Localization**: Philippine English, PHP currency, PH tax compliance
- **Technical Terms**: Use standard Odoo/OCA terminology

---

## Section 1: App Snapshot

### 1.1 What This Is

The **InsightPulseAI Odoo 18 CE/OCA Implementation Handbook** is a documentation product that:

- Adapts official Odoo 18 documentation for the InsightPulseAI stack
- Provides step-by-step configuration guides for CE/OCA modules
- Maps data flows between Odoo, Supabase, and n8n
- Documents AI agent integration patterns
- Serves as RAG corpus for AI assistants

### 1.2 What This Is Not

- Not a replacement for official Odoo docs (links provided)
- Not end-user training material (separate training docs exist)
- Not Enterprise/SaaS documentation

### 1.3 Target Audiences

| Persona | Primary Use Cases |
|---------|-------------------|
| **Implementer** | Configure Odoo modules, map data flows |
| **Finance User** | Understand accounting workflows, expense processes |
| **Project Manager** | Set up projects, manage timesheets |
| **Developer** | Build ipai_* modules, extend OCA |
| **DevOps Engineer** | Deploy, monitor, troubleshoot |
| **AI Agent** | Query handbook via RAG for user assistance |

---

## Section 2: Page Inventory

### 2.1 Welcome & Architecture (Section 0)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `welcome-overview` | `pages/00-welcome/01-overview.md` | All | Introduce stack components |
| `welcome-architecture` | `pages/00-welcome/02-architecture.md` | Developer, DevOps | System architecture diagram |
| `welcome-environments` | `pages/00-welcome/03-environments.md` | DevOps | Dev/staging/prod setup |
| `welcome-multitenancy` | `pages/00-welcome/04-multitenancy.md` | Developer | RLS and tenant_id patterns |

### 2.2 Finance Workspace (Section 1)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `finance-overview` | `pages/01-finance/01-overview.md` | Finance | Finance module introduction |
| `finance-coa` | `pages/01-finance/02-chart-of-accounts.md` | Finance | Set up PH chart of accounts |
| `finance-invoicing` | `pages/01-finance/03-invoicing.md` | Finance | Customer invoicing workflow |
| `finance-vendor-bills` | `pages/01-finance/04-vendor-bills.md` | Finance | Vendor bill processing |
| `finance-expenses` | `pages/01-finance/05-expenses.md` | Finance | Expense management (TE-Cheq) |
| `finance-reconciliation` | `pages/01-finance/06-reconciliation.md` | Finance | Bank reconciliation |
| `finance-month-end` | `pages/01-finance/07-month-end.md` | Finance | Month-end close process |
| `finance-supabase` | `pages/01-finance/08-supabase-mapping.md` | Developer | Data mapping to Supabase |
| `finance-n8n` | `pages/01-finance/09-n8n-workflows.md` | Developer | Automation workflows |

### 2.3 Projects & PPM (Section 2)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `ppm-overview` | `pages/02-ppm/01-overview.md` | PM | PPM module introduction |
| `ppm-hierarchy` | `pages/02-ppm/02-hierarchy.md` | PM | Portfolio/Program/Project setup |
| `ppm-wbs` | `pages/02-ppm/03-wbs.md` | PM | WBS and task management |
| `ppm-timesheets` | `pages/02-ppm/04-timesheets.md` | PM | Timesheet entry and approval |
| `ppm-budgets` | `pages/02-ppm/05-budgets.md` | PM, Finance | Budget tracking |
| `ppm-rates` | `pages/02-ppm/06-rate-cards.md` | PM, Finance | Rate card configuration |
| `ppm-supabase` | `pages/02-ppm/07-supabase-mapping.md` | Developer | Data mapping |
| `ppm-analytics` | `pages/02-ppm/08-analytics.md` | Analyst | Superset dashboards |

### 2.4 HR & People Ops (Section 3)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `hr-overview` | `pages/03-hr/01-overview.md` | HR | HR module introduction |
| `hr-employees` | `pages/03-hr/02-employees.md` | HR | Employee master data |
| `hr-recruitment` | `pages/03-hr/03-recruitment.md` | HR | Recruitment workflows |
| `hr-time-off` | `pages/03-hr/04-time-off.md` | HR | Leave management |
| `hr-attendance` | `pages/03-hr/05-attendance.md` | HR | Attendance tracking |
| `hr-supabase` | `pages/03-hr/06-supabase-mapping.md` | Developer | Data mapping |

### 2.5 Retail & Scout (Section 4)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `retail-overview` | `pages/04-retail/01-overview.md` | Retail | Retail integration intro |
| `retail-pos` | `pages/04-retail/02-pos-config.md` | Retail | POS configuration |
| `retail-scout` | `pages/04-retail/03-scout-pipeline.md` | Developer | Scout data ingestion |
| `retail-medallion` | `pages/04-retail/04-medallion.md` | Developer | Bronze/Silver/Gold ETL |
| `retail-saricoach` | `pages/04-retail/05-saricoach.md` | Retail, AI | SariCoach insights |
| `retail-analytics` | `pages/04-retail/06-analytics.md` | Analyst | Superset dashboards |

### 2.6 Inventory & Equipment (Section 5)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `equipment-overview` | `pages/05-equipment/01-overview.md` | Ops | Equipment module intro |
| `equipment-assets` | `pages/05-equipment/02-assets.md` | Ops | Asset registration |
| `equipment-booking` | `pages/05-equipment/03-booking.md` | Ops | Booking workflows |
| `equipment-maintenance` | `pages/05-equipment/04-maintenance.md` | Ops | Maintenance scheduling |
| `equipment-supabase` | `pages/05-equipment/05-supabase-mapping.md` | Developer | Data mapping |

### 2.7 Sales & CRM (Section 6)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `sales-overview` | `pages/06-sales/01-overview.md` | Sales | Sales module intro |
| `sales-crm` | `pages/06-sales/02-crm.md` | Sales | Lead management |
| `sales-quotations` | `pages/06-sales/03-quotations.md` | Sales | Quotation workflows |
| `sales-supabase` | `pages/06-sales/04-supabase-mapping.md` | Developer | Data mapping |

### 2.8 AI Workbench (Section 7)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `ai-overview` | `pages/07-ai/01-overview.md` | Developer | AI integration intro |
| `ai-engines` | `pages/07-ai/02-engine-registry.md` | Developer | Engine architecture |
| `ai-mcp` | `pages/07-ai/03-mcp-server.md` | Developer | MCP server setup |
| `ai-rag` | `pages/07-ai/04-rag-pipeline.md` | Developer | RAG over handbook |
| `ai-agents` | `pages/07-ai/05-domain-agents.md` | Developer | Agent configurations |

### 2.9 Integrations (Section 8)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `int-supabase` | `pages/08-integrations/01-supabase.md` | Developer | Supabase patterns |
| `int-n8n` | `pages/08-integrations/02-n8n.md` | Developer | n8n workflow patterns |
| `int-mattermost` | `pages/08-integrations/03-mattermost.md` | Developer | ChatOps setup |
| `int-superset` | `pages/08-integrations/04-superset.md` | Analyst | Analytics integration |
| `int-apis` | `pages/08-integrations/05-external-apis.md` | Developer | External API patterns |

### 2.10 DevOps (Section 9)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `devops-overview` | `pages/09-devops/01-overview.md` | DevOps | Infrastructure intro |
| `devops-digitalocean` | `pages/09-devops/02-digitalocean.md` | DevOps | Droplet setup |
| `devops-docker` | `pages/09-devops/03-docker.md` | DevOps | Docker compose |
| `devops-cicd` | `pages/09-devops/04-cicd.md` | DevOps | GitHub Actions |
| `devops-backup` | `pages/09-devops/05-backup.md` | DevOps | Backup/restore |
| `devops-security` | `pages/09-devops/06-security.md` | DevOps | SSL, firewalls |
| `devops-monitoring` | `pages/09-devops/07-monitoring.md` | DevOps | Observability |

### 2.11 Developer Guide (Section 10)

| page_id | path | audience | main_goal |
|---------|------|----------|-----------|
| `dev-standards` | `pages/10-developer/01-standards.md` | Developer | OCA standards |
| `dev-modules` | `pages/10-developer/02-modules.md` | Developer | ipai_* patterns |
| `dev-security` | `pages/10-developer/03-security.md` | Developer | RLS patterns |
| `dev-testing` | `pages/10-developer/04-testing.md` | Developer | Test framework |
| `dev-migration` | `pages/10-developer/05-migration.md` | Developer | Migration procedures |

---

## Section 3: Page Specs

### 3.1 Finance Overview Page (`finance-overview`)

**Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `hero-card` | Card | Module overview with key stats |
| `modules-table` | Table | CE/OCA modules in scope |
| `differentiators-table` | Table | Stock vs IPAI comparison |
| `engine-callout` | Callout | Related domain engines |
| `workflow-diagram` | Diagram | High-level finance flow |

**Content Sections:**
1. Overview & Purpose
2. Key Differentiators (table)
3. Related Engines (callout)
4. Module Summary (table)
5. Quick Links (navigation)

### 3.2 Invoicing Page (`finance-invoicing`)

**Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `workflow-diagram` | Diagram | Invoice lifecycle |
| `steps-accordion` | Accordion | Step-by-step instructions |
| `supabase-mapping` | Table | Data flow to Supabase |
| `n8n-workflows` | Table | Automation triggers |
| `delta-note` | Callout | Differences from stock Odoo |
| `integration-callout` | Callout | InsightPulseAI integration |

### 3.3 PPM Hierarchy Page (`ppm-hierarchy`)

**Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `hierarchy-diagram` | Diagram | Portfolio → Program → Project |
| `model-table` | Table | Odoo + IPAI models |
| `setup-steps` | Steps | Configuration walkthrough |
| `supabase-schema` | Code | SQL schema definitions |
| `integration-callout` | Callout | Engine integration |

---

## Section 5: Data Model

### 5.1 Core Entities

| Entity | Odoo Model | Supabase Schema.Table | Owner |
|--------|------------|----------------------|-------|
| Company | `res.company` | `core.companies` | Platform |
| Employee | `hr.employee` | `core.employees` | Platform |
| Customer | `res.partner` | `dim.customers` | Domain |
| Vendor | `res.partner` | `rates.vendor_profile` | SRM |
| Product | `product.product` | `scout_dim.products` | Retail |
| Project | `project.project` | `projects.projects` | PPM |
| Invoice | `account.move` | `finance.invoices` | Finance |
| Expense | `hr.expense` | `expense.expenses` | TE-Cheq |
| Timesheet | `account.analytic.line` | `projects.timesheets` | PPM |
| POS Transaction | `pos.order` | `scout_bronze.transactions` | Retail |

### 5.2 Entity Relationships

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   COMPANY    │────▶│   EMPLOYEE   │────▶│   TIMESHEET  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       │                    │                     ▼
       │                    │             ┌──────────────┐
       │                    └────────────▶│   PROJECT    │
       │                                  └──────────────┘
       │                                         │
       ▼                                         ▼
┌──────────────┐                          ┌──────────────┐
│   INVOICE    │◀─────────────────────────│    BUDGET    │
└──────────────┘                          └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   CUSTOMER   │◀────│   POS TXN    │
└──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   PRODUCT    │
                     └──────────────┘
```

### 5.3 Supabase Schema Ownership

| Schema | Owner Engine | Domain |
|--------|--------------|--------|
| `core` | Platform | Infrastructure |
| `finance` | TE-Cheq | Finance Ops |
| `expense` | TE-Cheq | T&E |
| `projects` | PPM | Engagements |
| `rates` | SRM | Rate Cards |
| `scout_bronze` | E1 Data Intake | Raw Retail |
| `scout_silver` | E3 Intelligence | Cleaned Retail |
| `scout_gold` | Retail-Intel | Aggregated |
| `platinum` | E4 Creative | AI Cache |

---

## Section 6: Roles Matrix

### 6.1 Role Permissions by Domain

| Role | Finance | PPM | HR | Retail | Equipment | DevOps |
|------|---------|-----|-----|--------|-----------|--------|
| Super Admin | Full | Full | Full | Full | Full | Full |
| Finance Director | Full | Read | Read | Read | Read | None |
| PPM Manager | Read | Full | Read | None | Read | None |
| HR Manager | Read | Read | Full | None | None | None |
| Store Owner | None | None | None | Own | None | None |
| Developer | Read | Read | Read | Read | Read | Full |
| Analyst | Read | Read | Read | Read | Read | None |

### 6.2 Supabase Role Mapping

| Persona | Supabase Role | Odoo Groups |
|---------|---------------|-------------|
| Finance Director | `finance_director` | `account.group_account_manager` |
| PPM Manager | `ppm_portfolio_mgr` | `project.group_project_manager` |
| HR Manager | `hr_manager` | `hr.group_hr_manager` |
| Store Owner | `sari_store_owner` | `point_of_sale.group_pos_user` |
| Analyst | `readonly` | `base.group_user` |
| Developer | `engine_admin` | `base.group_system` |

---

## Section 7: Edge Cases

### 7.1 Partial CE Parity

| Feature | Status | Workaround |
|---------|--------|------------|
| Studio | No parity | Use proper module development |
| Documents | Partial | Notion + Supabase `doc.*` |
| Helpdesk | OCA parity | Use `helpdesk_mgmt` |
| Planning | Partial | ipai_ppm + Superset |
| Sign | External | DocuSign integration |

### 7.2 PH-Specific Considerations

| Topic | Consideration |
|-------|---------------|
| Tax (VAT/EWT) | PH 12% VAT, withholding tax rules |
| BIR Forms | 2307, 2306, 2316 generation planned for Phase 2 |
| Currency | PHP primary, multi-currency for USD |
| Date Format | Philippine format (MM/DD/YYYY) |
| Holidays | PH public holidays in HR module |

### 7.3 Multi-Tenant Boundaries

| Scenario | Handling |
|----------|----------|
| Cross-tenant data | Blocked by RLS |
| Shared lookups | `core.*` tables without tenant_id |
| Tenant onboarding | Seeding script creates tenant data |
| Tenant isolation | Every query filtered by `core.current_tenant_id()` |

---

## Appendix A: Reference Docs

| Document | Purpose |
|----------|---------|
| [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/) | Official reference |
| [OCA GitHub](https://github.com/OCA) | OCA module source |
| [CE/OCA Mapping](../ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md) | Feature mapping |
| [Technical Architecture](../architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md) | System design |
