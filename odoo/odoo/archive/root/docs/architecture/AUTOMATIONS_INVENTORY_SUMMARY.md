# Automations Inventory Summary
> Generated from normalized SSOT.

## Coverage Disclosure
| Surface | Status |
|---|---|
| odoo_crons | not_scanned |
| supabase_edge_functions | repo-scanned |
| github_actions | repo-scanned |
| pg_cron | not_scanned |
| n8n | not_scanned |

## Total Counts
| Platform | Type | Count |
|---|---|---|
| Supabase | edge-function | 59 |
| GitHub | github-action | 269 |
| n8n | n8n-workflow | 9 |

## Trigger Breakdown (Normalized)
- **http**: 46
- **webhook**: 64
- **cron**: 34
- **push_pr**: 235
- **manual**: 150
- **unknown**: 2
- **mixed**: 30

## Unknown-Status Heatmap
| Status | Count |
|---|---|
| unknown | 337 |

## Scheduled Automations
| Name | Platform | Trigger Node |
|---|---|---|
| cron-processor | Supabase | Scheduled |
| github-waf-assessment | GitHub | Cron: 0 2 * * 1, Manual |
| MCP Jobs Executor | GitHub | Cron: Defined, Manual |
| Azure WAF Parity Gate | GitHub | Cron: Defined, Manual, Push/PR |
| Nightly Integration Audit | GitHub | Cron: Defined, Manual, Push/PR |
| GHAS Security Gates | GitHub | Cron: Defined, Push/PR |
| Ops CI Router (Multi-Signal Scoring + Alerting) | GitHub | Cron: */5 * * * *, Manual |
| Odoo Schema Pipeline | GitHub | Cron: Defined, Manual, Push/PR |
| Sync FigJam Feature Map to GitHub Issues | GitHub | Cron: Defined, Manual |
| Infrastructure Memory Job | GitHub | Cron: Defined, Manual |
| sync-anthropic-skills | GitHub | Cron: 0 3 * * 1, Manual |
| fin-workspace weekly DO inventory sync | GitHub | Cron: 0 18 * * 1, Manual |
| Odoo Editions Parity Seed | GitHub | Cron: 0 0 * * 0, Manual |
| health-smoke | GitHub | Cron: 0 */6 * * *, Manual, Push/PR |
| BIR Forms Registry Scraper | GitHub | Cron: Defined, Manual |
| memory-distill | GitHub | Cron: Defined, Manual, Push/PR |
| EE Parity Test Runner | GitHub | Cron: Defined, Manual, Push/PR |
| infra-waf-assessment | GitHub | Cron: 0 3 * * 1, Manual |
| Auth Smoke Test | GitHub | Cron: 0 */6 * * *, Manual, Push/PR |
| DNS Drift Detection | GitHub | Cron: 0 */6 * * *, Manual |
| Drive Sync | GitHub | Cron: 0 4 * * *, Manual |
| Vendor Backlog Sync (attached repos -> backlog/vendors) | GitHub | Cron: 23 * * * *, Manual, Push/PR |
| Service Health Check (All Services) | GitHub | Cron: */15 * * * *, Manual |
| DO / Sandbox Janitor (TTL Cleanup) | GitHub | Cron: 0 */6 * * *, Manual |
| Infra Memory Job | GitHub | Cron: Defined, Manual |
| Vercel Integrations Diff | GitHub | Cron: 0 8 * * *, Manual |
| Directional Sync Automation | GitHub | Cron: Defined, Manual |
| kb-refresh-scheduled | GitHub | Cron: Defined, Manual |
| Finance Stack Health Check | GitHub | Cron: Defined, Manual |
| parity | GitHub | Cron: 23 3 * * *, Manual, Push/PR |
| Docs Crawler (Daily Refresh) | GitHub | Cron: Defined, Manual |
| Finance PPM - AI Journal Posting (Claude API + Odoo 19) | n8n | scheduleTrigger |
| Finance PPM - BIR Form Generation (Odoo 19 PH) | n8n | scheduleTrigger |
| Finance PPM - Recurrent Alerts (Odoo 19) | n8n | scheduleTrigger |

## Template / Deprecated (Needs Review)
- `[TEMPLATE]` _template-bridge (Supabase)
- `[TEMPLATE]` odoo-template-export (Supabase)
- `[DEPRECATED]` Block deprecated repo references (GitHub)
- `[DEPRECATED]` Terraform - Cloudflare DNS (deprecated) (GitHub)