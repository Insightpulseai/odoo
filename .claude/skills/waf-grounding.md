# WAF Service Guide Grounding — IPAI Judge Agents
**Source:** Azure Well-Architected Framework Service Guides (April 2026)
**Purpose:** Ground IPAI judge agents (architecture-judge, security-judge, finops-judge,
governance-judge, platform-fit-judge) in authoritative WAF service-specific criteria.
**Scope:** Five services in IPAI's critical path + WAF AI Workload pillar

Judges MUST evaluate against these criteria. Each section maps WAF guidance to IPAI's
actual deployed resources. Deviations are scored as findings.

---

## 1. Azure Cosmos DB for NoSQL (`cosmos-ipai-dev`, East US 2)

**IPAI use:** Foundry Agent Service thread/conversation store (Standard Setup)
**WAF guide:** https://learn.microsoft.com/en-us/azure/well-architected/service-guides/cosmos-db

### Reliability
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Deploy across ≥2 regions | EUS2 (primary) — needs secondary | ⚠️ SINGLE REGION — finding |
| Availability zone support | Enable on `cosmos-ipai-dev` | ⚠️ AZ support — verify |
| Service-managed failover enabled | Required | ⚠️ Verify on account |
| Continuous backup (PITR) | `Continuous7Days` configured in Bicep | ✅ PASS — in deploy script |
| SDK-based access only | Foundry Agent Service uses SDK | ✅ Foundry-managed |
| Consistency level Session | Configured in Bicep | ✅ PASS |

**Judge finding:** Single-region Cosmos is the highest reliability risk. Minimum: add EUS2 → SEA read replica. Dev acceptable; must fix before prod.

### Security
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Disable key-based authentication | Use Entra RBAC only | ⚠️ Verify `disableLocalAuth: true` |
| Private endpoints | Not yet (Week 2 scope) | ⚠️ FINDING — public endpoint in dev |
| Defender for Cosmos DB | Enable after provisioning | ⚠️ NOT ENABLED |
| RBAC data plane access | Foundry project MI → DocumentDB Contributor | ✅ Applied in Bicep |
| Audit control plane logs | Route to `la-ipai-odoo-dev` | ⚠️ Not configured |

**Security judge mandatory finding:** Enable `Defender for Cosmos DB` on `cosmos-ipai-dev` immediately after provisioning — no cost justification for leaving it off.

### Cost Optimization
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Serverless for dev/unpredictable traffic | ✅ `EnableServerless` in Bicep | ✅ PASS |
| Index policy customization | Foundry manages — not directly configurable | N/A |
| Monitor RU consumption | Alert via `appi-ipai-dev` | ⚠️ No RU alert defined yet |
| TTL on expired agent threads | Configure after provisioning | ⚠️ Not yet |

### Operational Excellence
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| IaC deployment | ✅ `foundry-agent-dependencies.bicep` | ✅ PASS |
| Latest SDK | Foundry Agent Service manages | ✅ |
| Diagnostic settings → Log Analytics | Route to `la-ipai-odoo-dev` | ⚠️ Not configured |

---

## 2. Azure Front Door (`afd-ipai-dev`, Global)

**IPAI use:** Global ingress, WAF, TLS termination for `erp.insightpulseai.com`
**WAF guide:** https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-front-door

### Reliability
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Multiple origins per origin group | 7 origin groups, all single-origin currently | ⚠️ No redundant origins (single ACA env) |
| Health probes on all origins | Configured via Bicep | ✅ PASS |
| Same host name on AFD and origin | Verify `erp.insightpulseai.com` passthrough | ⚠️ Verify — host header rewrite risk |
| Routing method: latency/priority | Latency-based (default) | ✅ Appropriate for single-region |
| Timeout configuration | Default 60s — verify for Odoo long requests | ⚠️ Odoo requests may need >60s |

### Security
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| WAF DefaultRuleSet enabled | ✅ DefaultRuleSet 2.1 on `wafipaidev` | ✅ PASS |
| Bot protection enabled | ✅ BotManager on `wafipaidev` | ✅ PASS |
| Rate limiting rules | ⚠️ Not configured | ⚠️ FINDING |
| Private Link to origins | Premium tier required — not yet | ⚠️ Using service tags + FDID header |
| End-to-end TLS | ✅ HTTPS-only, managed certs | ✅ PASS |
| WAF exclusions for chat prompts | ⚠️ Not configured — chat content trips WAF | ⚠️ FINDING (Foundry baseline requirement) |
| WAF in Detection → Prevention mode | ⚠️ Verify mode | ⚠️ Verify |
| Geo-filtering | Philippine SMB focus — consider restricting | ⚠️ Not configured |

**Security judge mandatory finding:** WAF exclusions for request body fields carrying chat prompts/agent messages are required before deploying Pulser chat surfaces. Chat content (code, SQL, HTML in prompts) triggers OWASP anomaly scoring and causes HTTP 403 on long conversations.

### Cost Optimization
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Standard vs Premium tier | ⚠️ Which tier? Check AFD profile SKU | ⚠️ Premium required for managed WAF rules |
| Caching for static content | Static assets cacheable | ⚠️ Not configured on Odoo static routes |
| Health check on single-origin groups | Disable where only 1 origin | ⚠️ Wasted bandwidth — disable for groups with 1 origin |

### Operational Excellence
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| IaC deployment | ✅ `afd.bicep` in infra/ | ✅ PASS |
| HTTP→HTTPS redirect | ✅ Configured | ✅ PASS |
| Managed TLS certificates | ✅ On `erp.insightpulseai.com` | ✅ PASS |
| WAF + access logs → Log Analytics | ⚠️ Verify diagnostic settings | ⚠️ Verify |
| WAF in Prevention mode after tuning | ⚠️ Verify | ⚠️ |

---

## 3. Azure Database for PostgreSQL Flexible Server (`pg-ipai-odoo`, SEA)

**IPAI use:** Odoo 18 CE SOR — `odoo`, `odoo_staging`, `odoo_dev` databases
**WAF guide:** https://learn.microsoft.com/en-us/azure/well-architected/service-guides/postgresql

### Reliability
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| High availability configuration (Zone-redundant) | ⚠️ Burstable tier — no HA | ⚠️ FINDING — no HA on Odoo DB |
| Geo-redundant backups | ⚠️ Verify backup config | ⚠️ Verify |
| Backup retention ≥7 days | ⚠️ Verify | ⚠️ |
| Test backup/restore strategy | ⚠️ Never documented | ⚠️ FINDING |
| Private endpoint (`pe-pg-ipai-odoo`) | ✅ Private endpoint deployed | ✅ PASS |
| Custom maintenance window | ⚠️ Not configured | ⚠️ Set to off-hours PHT |

**Reliability judge finding:** Burstable Flexible Server with no zone-redundant HA is the Odoo reliability gap. Odoo is the SOR — if PG goes down, all ERP functions stop. Upgrade to General Purpose + Zone-Redundant HA before first paying customer.

### Security
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Entra ID authentication | ✅ Entra auth via MI | ✅ PASS |
| Private Link only | ✅ `pe-pg-ipai-odoo` | ✅ PASS |
| No public network access | ✅ Public access disabled | ✅ PASS |
| Connection throttling | ⚠️ `connection_throttling` parameter — verify | ⚠️ Verify |
| Row-level security | N/A — Odoo manages RLS at application layer | N/A |
| SSL enforcement | ✅ Default on Flexible Server | ✅ PASS |

### Cost Optimization
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Right-size tier | Burstable for dev — correct for current load | ✅ Appropriate for dev |
| Reserved instances for stable compute | ⚠️ After 3 months stable usage | ⚠️ Consider after baseline established |
| Consolidate databases | ✅ 3 DBs on 1 server | ✅ PASS |
| Deploy same region as app | ⚠️ ACA is SEA, PG is SEA | ✅ PASS — co-located |
| Stop server when not needed | Dev only — use start/stop for dev | ⚠️ Not configured |

### Performance Efficiency
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| PgBouncer connection pooling | ⚠️ Not enabled | ⚠️ FINDING — Odoo uses many short-lived connections |
| Query store enabled | ⚠️ Verify | ⚠️ |
| Index tuning | ⚠️ Not configured | ⚠️ |
| Intelligent tuning | ⚠️ Not enabled | ⚠️ |

**Performance judge finding:** PgBouncer is the highest-leverage performance improvement for Odoo on Azure PG Flex. Odoo's request-per-connection model creates connection exhaustion under load. Enable PgBouncer on `pg-ipai-odoo` before scaling to multiple tenants.

---

## 4. Azure Blob Storage (`stipaidev`, `stipaiagentdev`, SEA)

**IPAI use:** `stipaidev` — Odoo filestore, ADLS layer, app data
          `stipaiagentdev` — Dedicated Foundry Agent Service file store (DO NOT SHARE)
**WAF guide:** https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-blob-storage

### Reliability
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| ZRS redundancy for agent storage | ✅ `Standard_ZRS` in Bicep for `stipaiagentdev` | ✅ PASS |
| GZRS for app storage | ⚠️ `stipaidev` redundancy — verify | ⚠️ Verify |
| Soft delete (blob + container) | ⚠️ Not configured | ⚠️ FINDING |
| Blob versioning | ⚠️ Not enabled | ⚠️ |
| Vaulted backup | ⚠️ Not configured | ⚠️ Consider for compliance |
| Delete lock on agent storage | ✅ `CanNotDelete` in Bicep | ✅ PASS |

**Critical isolation rule (from Foundry reference arch):** `stipaiagentdev` is DEDICATED to Foundry Agent Service. Other workload components MUST NOT use it. Foundry manages containers and lifecycle. Direct access violates the architecture.

### Security
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| No anonymous public access | ✅ `allowBlobPublicAccess: false` in Bicep | ✅ PASS |
| Shared key authorization disabled | ⚠️ Verify `disableLocalAuth` | ⚠️ Verify |
| Private endpoints | ⚠️ Not yet (Week 2 scope) | ⚠️ FINDING for prod |
| Entra RBAC for access | ✅ MI-based access | ✅ PASS |
| TLS 1.2 minimum | ✅ `minimumTlsVersion: TLS1_2` in Bicep | ✅ PASS |
| Defender for Storage | ⚠️ Not enabled | ⚠️ Enable on both accounts |
| Resource Manager lock | ✅ `CanNotDelete` on agent storage | ✅ PASS — add to `stipaidev` too |

### Cost Optimization
| WAF Criterion | IPAI Target | Judge Check |
|---|---|---|
| Lifecycle management policies | ⚠️ Not configured | ⚠️ Add for Odoo filestore (move old attachments to cool) |
| Access tiers | Hot for all — evaluate | ⚠️ Archive old Odoo attachments |
| Disable unused encryption scopes | ⚠️ Verify | ⚠️ |

---

## 5. Application Insights + Log Analytics (`appi-ipai-dev`, `la-ipai-odoo-dev`, SEA)

**IPAI use:** Platform observability — ACA metrics, Odoo traces, agent telemetry, Foundry token usage
**WAF guide:** https://learn.microsoft.com/en-us/azure/well-architected/service-guides/application-insights

### Critical gaps (from WAF AI Workload + Foundry Baseline sessions)
| WAF Criterion | IPAI Status | Judge Check |
|---|---|---|
| Diagnostic settings on Foundry resource | ⚠️ Not routed to `la-ipai-odoo-dev` | ⚠️ FINDING |
| Foundry token usage metrics | ⚠️ Not tracked | ⚠️ FINDING |
| Agent latency P95 alert | ✅ `alert-ipai-agent-latency-p95` exists | ✅ PASS |
| Agent error rate alert | ✅ `alert-ipai-agent-error-rate` exists | ✅ PASS |
| Content Safety blocks alert | ✅ `alert-ipai-content-safety-blocks` exists | ✅ PASS |
| AI Search + Cosmos DB alerts | ⚠️ Not yet (resources new) | ⚠️ Add after Week 1 deploy |
| GenAI monitoring dashboard | ⚠️ No dedicated AI dashboard | ⚠️ Build: groundedness, latency, token cost |
| OTLP exporter → App Insights | ⚠️ `agent_orchestrator.py` has OTLP wired but endpoint not pointing at App Insights | ⚠️ Configure exporter URL |

---

## 6. WAF AI Workload Pillar (Foundry + Claude + Pulser agents)

**Source:** https://learn.microsoft.com/en-us/azure/well-architected/ai/
**IPAI use:** All Pulser agents, Foundry Agent Service, Claude claude-sonnet-4-6, Odoo MCP tools

### Reliability
| WAF Criterion | IPAI Status | Judge Check |
|---|---|---|
| Agent state isolated from workload data | ✅ Dedicated `cosmos-ipai-dev` + `stipaiagentdev` | ✅ PASS (after Week 1 deploy) |
| Model deployment: data-zone standard + spillover | ⚠️ Standard regional deployment only | ⚠️ Add data-zone or global deployment |
| No shared resources between agent service and app | ✅ Dedicated accounts enforced | ✅ PASS |
| DR plan for agent conversations | ✅ PITR on Cosmos (`Continuous7Days`) | ✅ PASS |
| Agent definitions as code | ⚠️ YAML stubs, not full pipeline | ⚠️ FINDING |

### Security
| WAF Criterion | IPAI Status | Judge Check |
|---|---|---|
| Conversation ownership enforcement (BOLA) | ⚠️ NOT IMPLEMENTED | ⚠️ CRITICAL FINDING |
| No prompt injection via client-supplied thread IDs | ⚠️ Not verified | ⚠️ |
| Defender for AI Services on Foundry | ⚠️ Not enabled | ⚠️ FINDING |
| Keyless auth (`DefaultAzureCredential`) | ✅ All ACA services use MI | ✅ PASS |
| No API keys in code or git | ✅ Key Vault + MI | ✅ PASS |
| Content Safety | ⚠️ No Content Safety resource | ⚠️ FINDING |

### Cost Optimization
| WAF Criterion | IPAI Status | Judge Check |
|---|---|---|
| Monitor token usage per model deployment | ⚠️ Not tracked in dashboards | ⚠️ |
| Restrict playground to non-prod | ⚠️ Policy not enforced | ⚠️ |
| Delete stale agents + conversations | ⚠️ No cleanup policy | ⚠️ |
| Right-size model (avoid premium for simple tasks) | ✅ Haiku for simple, Sonnet for complex | ✅ PASS |

### Operational Excellence
| WAF Criterion | IPAI Status | Judge Check |
|---|---|---|
| Agent definitions in source control | ⚠️ Partial — YAML stubs | ⚠️ FINDING |
| CI/CD pipeline for agent deployment | ⚠️ Template exists, not wired | ⚠️ |
| Agent versioning + safe rollout | ⚠️ Release Manager built, not active gate | ⚠️ |
| Test suite for agent behavior | ⚠️ Judge infrastructure built, no runs | ⚠️ FINDING |

---

## Judge scoring weights for IPAI

Based on IPAI's current maturity (startup ISV, pre-first-paying-customer):

| Pillar | Weight | Rationale |
|---|---|---|
| Security | 35% | Co-sell eligibility, first-customer trust |
| Reliability | 25% | SLA definition prerequisite |
| Operational Excellence | 20% | Release Manager gate, agent-as-code |
| Cost Optimization | 15% | Startup credits runway |
| Performance Efficiency | 5% | Premature optimization — defer |

---

## Consolidated CRITICAL findings (judge must flag as BLOCKER)

1. **BOLA vulnerability** — `copilot_gateway.py` does not verify user owns `thread_id` before agent call
2. **PgBouncer not enabled** — Odoo + PG Flex without connection pooling will fail under tenant load
3. **Cosmos DB single-region** — no failover for agent conversation state
4. **Defender for AI Services not enabled** — required for jailbreak/data-leakage detection
5. **WAF exclusions missing** — chat prompt content will trigger HTTP 403 on long conversations
6. **Agent definitions not fully as code** — no reproducible agent deployment from source

## HIGH findings (must fix before prod promotion)

7. PG Flex no HA → zone-redundant HA required before first paying customer
8. Diagnostic settings not routed from Foundry → Log Analytics
9. `stipaidev` missing CanNotDelete lock (only `stipaiagentdev` has it)
10. `connection_throttling` not verified on PG Flex
11. Content Safety resource not provisioned
12. Agent test suite (judges) has zero runtime evidence
