# Control Plane UI Policy

> Governs how the ops-console reads and renders platform governance data.
> The ops-console is a **read-only** control-plane surface. YAML registries remain the sole source of truth.

---

## Data Flow

```
YAML Registries (SSOT)
  ├── ssot/org/*.yaml                  → Org-level policies
  ├── ops-platform/ssot/**/*.yaml      → Service/agent/model registries
  ├── agents/foundry/**/*.yaml         → Agent manifests, tools, policies
  └── odoo/ssot/odoo/*.yaml            → Odoo boundary contracts

        ↓ (fs.readFileSync + js-yaml)

Registry Loading Layer
  ├── src/lib/registry/registryPaths.ts    → Path resolution
  └── src/lib/registry/loadYamlRegistry.ts → YAML parsing + error handling

        ↓ (normalize to typed cards)

View Model Mappers
  ├── src/lib/view-models/agents.ts     → AgentCard, ToolCard
  ├── src/lib/view-models/services.ts   → ServiceCard, ModelAliasCard, PolicyCard
  ├── src/lib/view-models/pipelines.ts  → PipelineCard, DocumentClassCard
  └── src/lib/view-models/odoo.ts       → OdooBoundaryCard

        ↓ (JSON via API routes)

Next.js API Routes (server-side)
  ├── /api/agents        → agents + tools from manifests
  ├── /api/services      → Azure service catalog
  ├── /api/deployments   → promotion state + model aliases
  ├── /api/orchestration → document pipelines + doc classes
  └── /api/knowledge     → KB status + boundary contracts + policies

        ↓ (SWR hooks, client-side)

React Pages (Fluent UI)
  ├── /agents            → Agent manifests + tool bindings
  ├── /services          → Azure service catalog + class/ownership
  ├── /deployments       → Promotion state + model deployment aliases
  ├── /orchestration     → Document pipelines + stage ownership
  └── /settings          → Policy summaries + authority docs
```

---

## Page → Registry Source Mapping

| Page | API Route | Primary Registry Sources |
|------|-----------|-------------------------|
| `/agents` | `/api/agents` | `agents/foundry/agents/*.yaml`, `agents/foundry/tools/*.yaml` |
| `/services` | `/api/services` | `ops-platform/ssot/azure/*.yaml`, `ssot/org/*azure*.yaml` |
| `/deployments` | `/api/deployments` | `ops-platform/ssot/foundry/*.yaml` (promotion, models) |
| `/orchestration` | `/api/orchestration` | `ops-platform/ssot/finance/*.yaml`, `ops-platform/ssot/docint/*.yaml` |
| `/knowledge` | `/api/knowledge` | `odoo/ssot/odoo/*.yaml`, `ssot/org/*.yaml` |
| `/settings` | `/api/knowledge` | All policy files across org/agents/ops-platform |

---

## Rules

1. **Read-only by default.** The UI must never write to YAML files. All mutations happen through git commits to the registry files.

2. **YAML registries remain SSOT.** No hidden config in page components, no local storage overrides, no UI-only state that shadows registry data.

3. **No fabricated defaults.** If a registry file is missing or malformed, render the data as `unknown` or show an explicit error. Never invent placeholder values that look like real data.

4. **Every card traces to a file.** Each rendered card/row should include a `sourceFile` reference so operators can trace back to the authoritative YAML.

5. **Missing registry data renders explicitly.** Use `unknown`, `—`, or a warning badge. Never hide missing data behind healthy-looking defaults.

6. **Fail loudly on parse errors.** If a YAML file is malformed, log the error server-side and show a warning in the UI. Don't silently skip.

7. **No runtime health from registries.** Registry data tells you what *should* exist. For runtime health (is a service actually responding?), keep existing health-check endpoints separate and clearly labeled.

8. **Source badge required.** Every page must display its data source (`registry`, `live`, `fallback`, `error`) so operators know what they're looking at.

---

## Adding New Registry Sources

1. Add the directory path to `REGISTRY_PATHS` in `src/lib/registry/registryPaths.ts`
2. Create a view-model mapper in `src/lib/view-models/`
3. Create or update an API route to serve the normalized data
4. Wire the page to the API route via SWR hook
5. Update this document's mapping table

---

## Architecture Constraints

- **Server-side only for fs access.** YAML loading happens in API routes (Node.js server), never in client components.
- **No build-time static generation.** Registry data should be fresh on every request (`force-dynamic`).
- **SWR for client-side caching.** Reasonable refresh intervals (30s–5min) to avoid hammering the filesystem.
- **Graceful degradation.** If registry loading fails, show error state — don't crash the app.

---

*Last updated: 2026-03-16*
