# Constitution — IPAI Pulser Visualization Engine
`.specify/constitution.md`
Rev: 2026-04-15 | NON-NEGOTIABLE

---

## Core principles

### 1. Azure-native only
All compute, storage, messaging, and AI inference runs on Azure.
Deprecated: Supabase, Vercel, Cloudflare, n8n, DigitalOcean, nginx.
Never reference deprecated infrastructure in any generated code or config.

### 2. Spec before code
No implementation file is written before its spec and plan are complete.
Every task card links to exactly one spec section. No orphan code.

### 3. Payload-first design
`viz_payload` JSON is the single source of truth for all render targets.
Teams, Odoo, and ops-console consume the same payload — never diverge.
Schema is defined in `platform/contracts/viz-payload.schema.json` and
validated before any render target code is written.

### 4. CLI-verifiable outputs
Every library exposes a CLI interface.
```
pulser-viz render --payload payload.json --target teams   # → adaptive_card.json
pulser-viz render --payload payload.json --target odoo    # → chart.html
pulser-viz render --payload payload.json --target console # → chart.png URL
```
If it cannot be tested via CLI stdin/stdout, it is not an acceptable design.

### 5. TDD non-negotiable
No implementation code before tests. Order: contract test → unit test → implementation.
Minimum coverage: 90% on all viz renderer modules.

### 6. OCA-first for Odoo
`ipai_viz_chatter` delta module inherits from OCA before adding custom logic.
`<list>` always (never `<tree>`). `view_mode="list,form"` always.

### 7. No secrets in git
All API keys, connection strings, and credentials live in `kv-ipai-dev-sea`.
DefaultAzureCredential for all Azure SDK calls — no hardcoded keys.

### 8. Idempotent jobs
Every render job is idempotent. Re-running with same input produces same output.
Idempotency key: SHA-256 of `viz_payload` JSON.

### 9. Audit trail mandatory
Every render job writes to `ipai_agent_run` (Odoo) and `cosmos-ipai-dev`.
`appi-ipai-dev-agent-sea` receives render duration and error telemetry via OTEL.

### 10. Dependency links
Predecessor tasks must complete before successor tasks start.
This applies to both Azure Boards work items and task execution in CI.

---

## Tech stack (locked)

| Layer | Canonical choice |
|---|---|
| Agent runtime | MAF (Microsoft Agent Framework) + Foundry |
| Reasoning model | o3-pro (complex) / gpt-5.4-pro (general) |
| Chart generation | Foundry Code Interpreter → matplotlib/plotly → PNG/SVG |
| Chart storage | `stipaidevagent` blob → AFD `afd-ipai-dev` |
| Teams render | Adaptive Card v1.5 |
| Odoo render | QWeb HTML template + Chart.js CDN |
| ops-console render | React + Chart.js |
| Queue | `sb-ipai-dev-sea` (Service Bus) |
| Schema validation | `platform/contracts/viz-payload.schema.json` (JSON Schema draft-07) |
| CI/CD | Azure Pipelines (`azure-pipelines/`) only |
| Secrets | `kv-ipai-dev-sea` |
| Observability | `appi-ipai-dev-agent-sea` |

---

## Forbidden patterns

- `import os; key = os.environ['KEY']` — use DefaultAzureCredential + Key Vault
- `tree` in Odoo view XML — use `list`
- GitHub Actions — use Azure Pipelines
- Hardcoded subscription IDs or resource names in application code
- Divergent payload schemas per render target — one schema, three renderers
- Synchronous chart generation blocking the agent response thread
