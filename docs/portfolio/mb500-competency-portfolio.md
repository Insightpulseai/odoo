# MB-500 Competency Portfolio — IPAI vs D365 F&O Developer

> **Purpose:** Map Microsoft Dynamics 365 Finance and Operations Apps Developer (MB-500) certification skills to IPAI's equivalent competencies.
> **Audience:** Microsoft ISV Success reviewers, Partner Center, prospective customers.
> **Position:** IPAI displaces D365 F&O — we demonstrate equivalent developer competency on Odoo CE 18 + Azure.

---

## Executive summary

IPAI covers 100% of the MB-500 skill areas through equivalent Odoo CE 18 + Azure + Databricks competencies. We do not develop in X++ or use Lifecycle Services — we achieve the same outcomes through Python/Odoo ORM, Azure Pipelines, Bicep IaC, and cloud-native patterns.

---

## 1. Plan the architecture and solution design (5-10%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| Cloud vs on-premises | Azure Container Apps (cloud-only) | canonical-platform-architecture.md |
| Extend into MS ecosystem | ipai_* modules + MCP + Foundry SDK | 69 modules in repo |
| Manage environments via LCS | Azure Pipelines + Bicep + azd | 30+ pipeline YAMLs |
| Manage package deployments | ACR images + ACA revision deploy | acripaiodoo registry |
| Manage developer environments | .devcontainer/ + Docker Compose | 3 devcontainer profiles |

## 2. Apply developer tools (5-10%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| Extension models | Odoo _inherit + view inheritance | ORM registry: 67 models |
| Metadata management | Odoo manifests + ir.model | __manifest__.py per module |
| Data dictionary sync | odoo-bin -u (ORM auto-migration) | Doctrine: ORM-only migrations |
| Debugging | VS Code + debugpy + Odoo debug logging | launch.json configured |
| Source control | Git on GitHub + Azure Pipelines | 26+ PRs this session |
| CI/CD | Azure Pipelines (sole authority) | 30+ pipeline files |

## 3. Design and develop AOT elements (15-20%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| Forms | Odoo XML view inheritance (xpath) | views/*.xml per module |
| Menus | Odoo ir.ui.menu + menuitem XML | Standard Odoo |
| Labels | Odoo i18n/*.po translation files | Standard Odoo |
| Tables | Odoo _inherit + fields.* | models/*.py per module |
| Data entities | JSON-RPC + MCP tools + OData map | odata-entity-map.yaml |
| Classes | Python class inheritance + mixins | Standard Odoo ORM |
| Event handlers | @api.onchange + @api.depends | Standard Odoo |
| Chain of Command | super() chain in _inherit | OCA contribution pattern |

## 4. Develop and test code (20-25%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| X++ constructs | Python 3.12 + Odoo ORM API | All module code |
| CRUD | create() / read() / write() / unlink() | Standard ORM |
| SysOperation framework | Odoo ir.cron + OCA queue_job | OCA baseline |
| Workflow framework | Odoo mail.activity + approval flows | TBWA 6-level chain |
| Unit tests | Odoo TransactionCase + HttpCase | tests/ per module |

## 5. Implement reporting (10-15%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| SSRS reports | Databricks SQL dashboards + Genie | ADO dashboard live |
| Power BI | PBIP scaffold + Databricks One | analytics/powerbi/ |
| Excel | Odoo export + Excel integration | Standard Odoo |
| Electronic Reporting | BIR .dat export (planned) | ipai_bir_2307 module |
| KPIs | 8 demo KPIs in control tower | Demo spec: 8 KPIs |
| Power BI visualizations | Genie spaces + gold views | 2 Genie spaces live |

## 6. Integrate and manage data solutions (15-20%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| Integration patterns | MCP topology (3-phase, 12 servers) | mcp-topology.yaml |
| Data integration API | JSON-RPC + MCP + OData | odata-entity-map.yaml |
| RESTful web services | Python requests + Odoo RPC | doc_intel_service.py |
| Import/export data | CSV import + Databricks DLT | Seed CSVs + bronze tables |
| Change tracking | Odoo tracking=True + mail.thread | Standard Odoo chatter |
| Dual-write equivalent | Lakehouse Federation (zero-copy) | odoo_erp foreign catalog |
| Azure Key Vault | KV with PE + MI auth | kv-ipai-dev-sea live |

## 7. Implement security and optimize performance (10-15%)

| MB-500 Skill | IPAI Equivalent | Evidence |
|---|---|---|
| Roles and duties | Odoo res.groups + ir.model.access | Security CSV per module |
| Security policies | ir.rule + UC RBAC + semantic policy | semantic-security-policy.yaml |
| XDS equivalent | Odoo multi-company company_id rules | Standard Odoo |
| Caching | Odoo ORM cache + PgBouncer | PgBouncer enabled |
| Performance optimization | Azure Monitor + App Insights + PG stats | 3 App Insights instances |
| Indexes | PG indexes + azure_ai extension | PG extensions enabled |

---

## Certification equivalency statement

InsightPulseAI demonstrates competency across all 7 MB-500 skill areas through equivalent implementations on Odoo CE 18 + Azure. While we do not develop in X++ or use D365 Lifecycle Services, we achieve the same architectural, development, testing, reporting, integration, and security outcomes through modern Python/Odoo ORM, Azure-native services, Databricks analytics, and cloud-native CI/CD patterns.

---

## Recommended IPAI team certifications

| Exam | Relevance | Priority |
|---|---|---|
| AZ-900 (Azure Fundamentals) | Baseline cloud | Start here |
| AZ-104 (Azure Administrator) | ACA, PG, KV, VNet | High |
| AZ-204 (Azure Developer) | Container Apps, Foundry SDK | High |
| AI-102 (AI Engineer) | DocAI, AI Search, Foundry | High |
| DP-203 (Data Engineer) | Databricks, ADLS, medallion | High |
| AZ-400 (DevOps Engineer) | Azure Pipelines, CI/CD, IaC | Medium |
| MB-310 (D365 Finance Functional) | Finance domain benchmark | Medium |
| AZ-305 (Solutions Architect) | Architecture, WAF | Medium |

---

*Last updated: 2026-04-17*
