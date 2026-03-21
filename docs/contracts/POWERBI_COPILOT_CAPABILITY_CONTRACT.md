# Power BI Copilot Capability Contract

> **Status**: Active — Databricks alternative implemented, Fabric path blocked
> **Date**: 2026-03-22
> **Owner**: platform

---

## Decision

Power BI Copilot (native Fabric feature) is **blocked** by licensing.
The platform uses **Databricks AI SQL views** as the copilot alternative.

## Fabric Copilot — Blocked

| Requirement | Our Status | Verdict |
|-------------|-----------|---------|
| Fabric capacity F2+ or Power BI Premium P1+ | **None** — Sponsored subscription | BLOCKED |
| Spending limit removed | Active spending limit | BLOCKED |
| Tenant setting: Azure OpenAI enabled | Not configured | BLOCKED (depends on capacity) |
| Cross-geo data processing (SEA tenant) | Not configured | BLOCKED (depends on capacity) |
| Trial SKU | Explicitly excluded by Microsoft | NOT ELIGIBLE |

**Minimum cost to unblock**: Fabric F2 @ ~$263/mo USD (requires removing spending limit on sponsored subscription).

**Decision**: Do not pursue Fabric capacity at this time. Use Databricks-native AI functions instead.

## Databricks Alternative — Implemented

### Architecture

```
Power BI Desktop/Service
    ↓ DirectQuery (ODBC/JDBC)
Databricks SQL Warehouse (Serverless)
    ↓ ai_query()
External Model Serving Endpoint (ipai-azure-openai)
    ↓ REST
Azure OpenAI (oai-ipai-dev, East US)
    ↓ GPT-4o
AI-enriched response → rendered in Power BI visual
```

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| External endpoint | `resources/endpoints/azure_openai.yml` | Routes `ai_query()` → Azure OpenAI GPT-4o |
| Platinum views | `notebooks/platinum/ai_copilot_views.py` | AI-enabled SQL views for Power BI |
| Deployment job | `resources/jobs/ai_copilot_platinum.yml` | Daily view refresh (01:00 UTC) |
| DAB bundle | `databricks.yml` | Includes `resources/endpoints/*.yml` |

### Platinum Layer Views

| View/Function | Input | AI Output | Power BI Use |
|---------------|-------|-----------|-------------|
| `ai_budget_narrative` | Gold budget vs actual | Variance explanation (2-3 sentences) | Card/text visual |
| `ai_risk_assessment` | Gold risk summary | Structured JSON (severity, category, recommendation) | Table/KPI visual |
| `ai_project_health` | Gold projects | Executive summary + traffic light | Card visual |
| `ai_forecast_commentary` | Gold forecast | Run-rate explanation | Tooltip visual |
| `ask_copilot(question)` | User text | Free-form analysis | Power BI parameter |

### `ask_copilot()` — Ad-hoc Copilot UDF

Power BI can call this function with a parameter binding:

```sql
SELECT platinum.ask_copilot('Which projects are over budget this quarter?')
```

In Power BI, bind to a slicer or text input parameter → renders AI response in a card visual. This replicates the "ask a question" Copilot experience without Fabric capacity.

### Prerequisites

1. **Azure OpenAI deployment**: `gpt-4o` on `oai-ipai-dev` (East US)
2. **Databricks secret scope**: `ipai-ai` with key `azure-openai-key`
3. **SQL Warehouse**: Serverless, Runtime 15.4 LTS+
4. **Unity Catalog**: `{catalog}.platinum` schema

### Deployment

```bash
cd infra/databricks

# Create secret scope (one-time)
databricks secrets create-scope ipai-ai
databricks secrets put-secret ipai-ai azure-openai-key

# Deploy bundle (creates endpoint + job)
databricks bundle deploy -t dev

# Run views job immediately
databricks bundle run ai_copilot_platinum -t dev
```

### Cost Comparison

| Path | Monthly Cost | Copilot Capability |
|------|-------------|-------------------|
| Fabric F2 | ~$263 + consumption | Native Copilot pane, summaries, Q&A |
| Databricks AI SQL | ~$0-30 (serverless per-query) | Custom views, UDF, structured + free-form |
| Power BI Pro only | $10/user | **No copilot** |

Databricks path costs only per-query execution on serverless warehouse + Azure OpenAI token usage. No standing capacity charge.

## Upgrade Path

If Fabric capacity is later procured:

1. Enable tenant settings (Azure OpenAI, cross-geo processing)
2. Assign workspace to F2+ capacity
3. Power BI Copilot activates automatically for reports in that workspace
4. Databricks platinum views remain complementary (structured AI analysis)

## Validation

- [ ] Azure OpenAI `gpt-4o` deployment active on `oai-ipai-dev`
- [ ] Databricks secret scope `ipai-ai` created with API key
- [ ] External endpoint `ipai-azure-openai` serving
- [ ] Platinum views created in Unity Catalog
- [ ] Power BI connected to SQL Warehouse via DirectQuery
- [ ] `ask_copilot()` returns valid response from Power BI

---

*Contract registered in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`*
