# Odoo Copilot on Azure — Implementation Plan

## Target Deployment Layout

### Azure Control/Runtime

| Service | Role |
|---------|------|
| Microsoft Agent Framework runtime | Agent orchestration, tool registry, publishing |
| Agent Framework hosted on Container Apps or Durable Functions | Managed agent hosting |
| Agent Framework tool registry | Private organizational tools + MCP endpoints |
| Azure API Management | External API gateway |
| Azure Container Apps | Custom runtime host for web/API shells and agent workloads |
| Azure Key Vault | Secrets management (Odoo credentials, DB connections, API keys) |
| Azure Monitor / App Insights | Observability, OpenTelemetry sink |

### Application Boundaries

```
agents/
  odoo-copilot/                        # Odoo-focused agents + finance/compliance sub-agents

packages/
  tool-odoo/                           # Odoo MCP/function tools
  tool-supabase/                       # Control plane access tools
  tool-databricks/                     # Intelligence summary tools
  tool-plane/                          # Workspace/docs retrieval tools
  shared-agent-contracts/              # Typed DTOs, error taxonomy, schemas

apps/
  copilot-web/                         # Optional web shell (Container Apps)
  copilot-api/                         # External API facade (behind API Management)

addons/ipai/
  ipai_copilot_gateway/                # Odoo: API endpoints for agent tools
  ipai_copilot_finance/                # Odoo: finance-specific tool exposure
  ipai_copilot_compliance/             # Odoo: tax/compliance tool exposure
  ipai_copilot_workspace_bridge/       # Odoo: workspace context bridge
```

### Runtime Model

| Component | Hosting | Purpose |
|-----------|---------|---------|
| Agent Framework Agents | Agent Framework on Container Apps or Durable Functions | Managed agent hosting where appropriate |
| Container Apps | Azure Container Apps | Custom app/API shells and supporting services |
| Agent Framework | Embedded in agents | Agent/workflow composition, MCP client, RAG |
| MCP | Tool protocol layer | Tool federation across all backend systems |
| API Management | Azure APIM | Externalized endpoint governance and rate limiting |

---

## Phased Rollout

### Phase 0 — Spec and Contracts (this phase)

**Duration**: Spec only (no code)

| Task | Deliverable |
|------|-------------|
| Define agent/tool contracts | `packages/shared-agent-contracts/` schemas |
| Define action allowlist | Transactional/navigational/informational taxonomy |
| Define grounding sources | Odoo records, Plane docs, Databricks marts |
| Define identity and authorization model | Managed identity + Odoo permission mapping |
| Define capability taxonomy | Constitution.md capability classes |
| Define module split | Thin Odoo modules + external agent code |

### Phase 1 — Odoo Tool Layer

**Goal**: Create the tool interface that agents will use to interact with Odoo.

| Task | Description | Module |
|------|-------------|--------|
| Record lookup tools | Read partner, invoice, expense, project records | `tool-odoo` |
| Approval/action tools | Approve, reject, create activities | `tool-odoo` |
| Deep-link tools | Generate Odoo web client URLs for records | `tool-odoo` |
| Expense/finance tools | Create expense, prepare close worklist | `tool-odoo` |
| Close monitoring tools | List blockers, summarize close status | `tool-odoo` |
| Role-aware auth checks | Map Agent Framework identity → Odoo user → check permissions | `ipai_copilot_gateway` |

**Odoo-side modules created in this phase:**
- `ipai_copilot_gateway` — JSON-RPC/REST endpoints for tool access
- `ipai_copilot_finance` — finance-specific tool endpoints
- `ipai_copilot_compliance` — BIR/tax tool endpoints

### Phase 2 — Agent Framework Runtime

**Goal**: Wire agents, workflows, MCP, and session handling. Host Agent Framework runtime on Azure Container Apps (ASP.NET Core) or Durable Azure Functions for workflow orchestration.

| Task | Description |
|------|-------------|
| Scaffold Agent Framework runtime | Create agent definitions with tool bindings |
| Add MCP connectivity | Register tool-odoo, tool-supabase, tool-databricks, tool-plane as MCP servers |
| Add session/state handling | Conversation context, multi-turn workflows |
| Add workflows for multi-step tasks | Approval chains, expense lifecycle, close monitoring |
| Add structured output contracts | Typed responses for all tool results |
| Add OpenTelemetry instrumentation | Traces, metrics, spans for all agent actions |

### Phase 3 — Grounding and Intelligence

**Goal**: Connect knowledge sources for informational capabilities.

| Task | Description | Source |
|------|-------------|--------|
| Connect Plane docs/wiki | RAG over workspace documents | Plane API |
| Connect Odoo attachments | RAG over approved document sources | Odoo `ir.attachment` |
| Connect Databricks summarized marts (OPTIONAL — defer if not ready) | Pre-computed analytics, forecasts, anomalies | Databricks SQL |
| Add citation engine | All informational answers include source citations | Agent Framework RAG |
| Add grounding policy | Define what can/cannot be grounded | Constitution |

### Phase 4 — Publication and Channels

**Goal**: Make the copilot available through multiple surfaces.

| Task | Description |
|------|-------------|
| Register agent in Agent Framework catalog | Register in Agent Framework agent catalog |
| Prepare Microsoft 365 Copilot path | Configure publication for M365 Copilot |
| Prepare Teams path | Configure bot/messaging integration |
| Expose stable APIs | API Management facade for programmatic access |
| Build web shell (optional) | Container Apps hosted web UI |

### Phase 5 — Governance and Hardening

**Goal**: Production readiness with security, evaluation, and deployment gates.

| Task | Description |
|------|-------------|
| Least-privilege identities | Managed identity for all service-to-service |
| Telemetry redaction | Ensure sensitive data not logged |
| Evaluation suite | Automated tests for tool contracts, grounding quality |
| Production deployment gates | CI/CD with approval gates for agent updates |
| Security review | Penetration testing, permission audit |

---

## Module Split Detail

### Odoo-Side Thin Modules

| Module | Purpose | Exposes |
|--------|---------|---------|
| `ipai_copilot_gateway` | Central API gateway for copilot tool access | JSON-RPC endpoints, auth middleware |
| `ipai_copilot_finance` | Finance-specific tool endpoints | Expense, invoice, close, approval tools |
| `ipai_copilot_compliance` | Tax/compliance tool endpoints | BIR filing status, compliance gates |
| `ipai_copilot_workspace_bridge` | Workspace context bridge | Activity feed, notification dispatch |

**Boundary rule**: These modules contain NO agent logic. They expose typed API endpoints that the external agent code calls via MCP/HTTP.

### Non-Odoo Code

| Package | Purpose | Location |
|---------|---------|----------|
| `tool-odoo` | MCP server wrapping Odoo API calls | `packages/tool-odoo/` |
| `tool-supabase` | MCP server for control plane queries | `packages/tool-supabase/` |
| `tool-databricks` | MCP server for analytics summaries | `packages/tool-databricks/` |
| `tool-plane` | MCP server for workspace/docs retrieval | `packages/tool-plane/` |
| `shared-agent-contracts` | Typed schemas, error taxonomy, DTOs | `packages/shared-agent-contracts/` |
| `odoo-copilot` | Agent definitions, workflows, composition | `agents/odoo-copilot/` |

---

## Cross-References

- `spec/azure-target-state/` — Azure infrastructure baseline
- `spec/integration-control-plane/` — Supabase ctrl.* schema
- `docs/architecture/CANONICAL_ENTITY_MAP.yaml` — entity ownership map
- `docs/architecture/INTEGRATION_BOUNDARY_MODEL.md` — system pair boundaries
- `spec/odoo-approval-inbox/` — approval tools source
- `spec/odoo-tne-control/` — expense tools source
- `spec/close-orchestration/` — close monitoring tools source
- `spec/odoo-bir-filing-control/` — compliance tools source
