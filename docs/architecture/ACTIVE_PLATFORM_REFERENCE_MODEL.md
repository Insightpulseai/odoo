# Active Platform Reference Model

> Single-page synthesis of the InsightPulseAI active architecture.
> Aligns three Microsoft reference patterns to the reduced Azure-native stack.
> Updated: 2026-03-25

---

## Reference Patterns

| # | Pattern | Source | Role in IPAI |
|---|---------|--------|-------------|
| 1 | AI-led SDLC | [Azure + GitHub](https://techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896) | Spec Kit → Agent CI → ACA preview |
| 2 | Data Intelligence | [Databricks + Fabric](https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621) | Databricks = lakehouse, Fabric/Power BI = consumption |
| 3 | AI Platform | [Microsoft Foundry](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/microsoft-foundry-an-end-to-end-platform-for-building-governing-and-scaling-ai/4496736) | Foundry = AI build/govern/scale |

---

## Active Stack (8 Planes)

```
┌─ SDLC ──────────────────────────────────────────────────┐
│  spec/ → .github/ → GitHub Actions → ACA preview URLs   │
├─ AI ────────────────────────────────────────────────────┤
│  agents/ (behavior) → Foundry (runtime) → OpenAI/Gemini │
├─ Data ──────────────────────────────────────────────────┤
│  data-intelligence/ → Databricks → Unity Catalog         │
│                            ↓                             │
│                    Power BI / Fabric (consumption only)   │
├─ ERP ───────────────────────────────────────────────────┤
│  odoo/ → addons/ipai/ → PostgreSQL (pg-ipai-odoo)       │
├─ Frontend ──────────────────────────────────────────────┤
│  web/ → Pulser widget, landing, SaaS, public            │
├─ Infrastructure ────────────────────────────────────────┤
│  infra/azure/ → ACA, Front Door, Key Vault, Foundry IaC │
├─ Identity ──────────────────────────────────────────────┤
│  Entra ID → SSO, Agent ID, RBAC, conditional access      │
├─ Governance ────────────────────────────────────────────┤
│  ssot/ + platform/ → intended state, contracts, schemas  │
└──────────────────────────────────────────────────────────┘
```

## Five-Layer Benchmark Model

| Layer | Benchmark Source | Repo Owner | Examples |
| ----- | ---------------- | ---------- | -------- |
| Odoo General | [Odoo /applications/general/](https://www.odoo.com/documentation/19.0/applications/general/) | `odoo/` | Users, companies, calendars, email, IoT, admin |
| Odoo Integrations | [Odoo /applications/general/integrations/](https://www.odoo.com/documentation/19.0/applications/general/integrations.html) | `odoo/` | Payments, tax, bank sync, marketplace |
| Odoo Services | [Odoo /applications/services/](https://www.odoo.com/documentation/19.0/applications/services.html) | `odoo/` | Project, timesheets, planning, field service, helpdesk |
| Odoo Finance | [Odoo /applications/finance/](https://www.odoo.com/documentation/19.0/applications/finance/accounting.html) | `odoo/` | Accounting, tax, expenses, reconciliation, budgets |
| Azure Platform | SAP on Azure patterns | `infra/` | Entra, Foundry, Databricks, Doc Intelligence, KV, ACA, networking, observability |

> Odoo owns application-local workflow truth. Azure owns mission-critical platform substrate.
> Pulser assists both but owns neither.

---

## Active Services

| Service | Plane | Type |
|---------|-------|------|
| Entra ID | Identity | Azure-native |
| Front Door | Infrastructure | Azure-native |
| Container Apps | Infrastructure | Azure-native |
| Key Vault | Infrastructure | Azure-native |
| Container Registry | Infrastructure | Azure-native |
| Odoo CE 19 | ERP | ACA-hosted |
| AI Foundry | AI | Azure-native |
| Azure OpenAI | AI | Azure-native |
| Document Intelligence | AI | Azure-native |
| Databricks | Data | Azure-native |
| Power BI | Data (consumption) | Azure SaaS |
| GitHub + Actions | SDLC | External |
| Azure DevOps | SDLC (target) | Azure-native |
| Gemini API | AI (creative) | External |
| fal | AI (media) | External |
| Cloudflare | DNS | External |
| Zoho | Mail | External |

## Not Active (Retired)

Supabase, n8n, Plane, Shelf, standalone CRM, Keycloak. See `RETIRED_SERVICES.md`.

## Invariants

1. **Databricks is primary** for data engineering. Fabric/Power BI are consumption only.
2. **Foundry is the AI plane.** Agent behavior lives in `agents/`, execution on Foundry.
3. **Spec Kit drives SDLC.** `spec/` → coding agent → quality gate → deploy.
4. **Entra is identity authority.** All services authenticate through Entra.
5. **No retired services in new designs.** Supabase, n8n, Plane, Shelf are not reference architecture.
6. **Pulser UI in `web/`, logic in `agents/`, Odoo module in `addons/ipai/`.**

## Detailed Docs

| Topic | Document |
|-------|----------|
| Active vs retired services | `ACTIVE_PLATFORM_BOUNDARIES.md` |
| Azure target architecture | `AZURE_NATIVE_TARGET_STATE.md` |
| Repo ownership boundaries | `REPO_OWNERSHIP_DOCTRINE.md` |
| Pulser runtime requirements | `PULSER_MINIMAL_RUNTIME.md` |
| Retired service records | `RETIRED_SERVICES.md` |
| Service registry (YAML) | `platform/ssot/services.yaml` |

---

*This is the compressed reference. Expand to the detailed docs above for implementation guidance.*
