# Enterprise Stack Layers

> 8-layer architecture mapping for InsightPulse AI platform.

## Layer Architecture

```
┌─────────────────────────────────────────────┐
│ Layer 8: AI/ML                              │
│ Workspace agents, copilots, anomaly detect  │
├─────────────────────────────────────────────┤
│ Layer 7: Analytics                          │
│ Superset, Databricks SQL, Gold marts        │
├─────────────────────────────────────────────┤
│ Layer 6: Automation                         │
│ n8n workflows, Slack integrations           │
├─────────────────────────────────────────────┤
│ Layer 5: ERP (System of Truth)              │
│ Odoo CE 19 + OCA + ipai_*                   │
├─────────────────────────────────────────────┤
│ Layer 4: Data Platform                      │
│ Databricks (Unity Catalog), Supabase        │
├─────────────────────────────────────────────┤
│ Layer 3: Infrastructure                     │
│ DigitalOcean, Azure (Databricks hosting)    │
├─────────────────────────────────────────────┤
│ Layer 2: CI/CD                              │
│ GitHub Actions (153 workflows)              │
├─────────────────────────────────────────────┤
│ Layer 1: Source Control                     │
│ GitHub Enterprise (Insightpulseai org)      │
└─────────────────────────────────────────────┘
```

## Layer Details

### Layer 1: Source Control
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Repositories | GitHub (`Insightpulseai/`) | Monorepo: `odoo` (main) |
| Branching | trunk-based (main) | Feature branches for PRs |
| Code review | GitHub PRs | Required for main |
| Spec kits | In-repo (`spec/`) | Architecture SSOT |

### Layer 2: CI/CD
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Build | GitHub Actions | 153 workflows |
| Test | pytest + jest + playwright | Gated on PR |
| Deploy | GitHub Actions → targets | Per deployment matrix |
| Security | Dependabot + CodeQL | Automated scanning |

### Layer 3: Infrastructure
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Compute | DigitalOcean SGP1 | 178.128.112.214 (consolidated) |
| Data compute | Azure (Databricks) | adb-7405610347978231 |
| DNS | Cloudflare | insightpulseai.com |
| Edge | Vercel | Customer-facing web |
| App hosting | DO App Platform | Specialized agents |

### Layer 4: Data Platform
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Lakehouse | Databricks Unity Catalog | Medallion architecture |
| Connectors | Custom SDK (5 sources) | Notion, GitHub, Odoo PG, Azure RG, generic |
| External DB | Supabase (pgvector) | Edge Functions, Realtime |
| OLTP | PostgreSQL 16 (local) | Odoo database |

### Layer 5: ERP (System of Truth)
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Core ERP | Odoo CE 19.0 | CE only, no Enterprise |
| Extensions | OCA modules | Community-vetted |
| Custom | ipai_* modules (43) | Delta only |
| Mail | Mailgun SMTP | mg.insightpulseai.com |

### Layer 6: Automation
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Workflows | n8n (self-hosted) | n8n.insightpulseai.com |
| Messaging | Slack | Replaced Mattermost |
| Notifications | Slack + email | Via Odoo + n8n |
| Scheduling | n8n + Odoo cron | Complementary |

### Layer 7: Analytics
| Component | Implementation | Notes |
|-----------|---------------|-------|
| BI | Apache Superset | superset.insightpulseai.com |
| SQL analytics | Databricks SQL | Gold layer queries |
| Dashboards | Superset + Databricks | Complementary |
| Reporting | Odoo reports + Superset | Operational + analytical |

### Layer 8: AI/ML
| Component | Implementation | Notes |
|-----------|---------------|-------|
| OCR | PaddleOCR-VL | Self-hosted, no per-scan fees |
| Copilot | ipai_copilot (planned) | NL ERP interaction |
| Search | Semantic (pgvector) | Document grounding |
| ML | Databricks ML | Predictive models |
| Agents | DO App Platform | Specialized AI agents |
