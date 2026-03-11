# diagramflow

Deterministic diagram pipeline for converting Mermaid to BPMN 2.0 and draw.io with Azure service remapping.

## Features

- **Mermaid → BPMN 2.0**: Convert flowcharts to SAP Signavio-compatible BPMN XML
- **Mermaid → draw.io**: Generate draw.io XML as source of truth
- **Azure Remapping**: Swap Azure services for target stack (DO/Supabase/Odoo)
- **CI Integration**: Drift checking for deterministic builds

## Installation

```bash
cd tools/diagramflow
npm install
npm run build
```

## Usage

### Build Diagrams (Mermaid → BPMN + draw.io)

```bash
# Build all Mermaid files in docs/diagrams
npm run diagram:build

# Or with custom paths
node dist/cli.js build --input src/diagrams --output dist/diagrams
```

### Check for Drift (CI Mode)

```bash
npm run diagram:ci

# Fails if generated files don't match
```

### Remap Azure Services

```bash
# Remap Azure services to DO/Supabase/Odoo stack
node dist/cli.js remap \
  --file diagram.drawio \
  --mapping docs/diagrams/mappings/azure_to_do_supabase_odoo.yaml

# Generate mapping template from existing diagram
node dist/cli.js remap --file diagram.drawio --template
```

## Mermaid Conventions (BPMN-aligned)

```mermaid
flowchart LR

subgraph Pool_Name
  S((Start))        %% Start event
  T1[Task]          %% Task
  G{Decision?}      %% Gateway
  T2[[Service]]     %% Service task
  T3[/User Task/]   %% User task
  E(((End)))        %% End event
end

S --> T1 --> G
G --> |Yes| T2 --> E
G --> |No| T3 --> E
```

### Node Types

| Mermaid Shape | BPMN Element |
|---------------|--------------|
| `((Label))` | Start Event |
| `(((Label)))` | End Event |
| `[Label]` | Task |
| `{Label?}` | Exclusive Gateway |
| `[[Label]]` | Service Task |
| `[/Label/]` | User Task |
| `([Label])` | Timer Event |

### Edge Types

| Mermaid Arrow | BPMN Flow |
|---------------|-----------|
| `-->` | Sequence Flow |
| `-.->` | Message Flow (cross-pool) |
| `-->|Label|` | Labeled Flow |

## Output Files

For each `.mmd` or `.mermaid` file:

- `{name}.bpmn` - BPMN 2.0 XML (Signavio-compatible)
- `{name}.drawio` - draw.io XML (source of truth)
- `export/{name}.png` - PNG export (via CI)
- `export/{name}.svg` - SVG export (via CI)

## Azure Mapping

Tag Azure services in draw.io with `svc=azure.xxx`:

```
[Azure App Service | svc=azure.app_service]
```

Then remap using the CLI:

```bash
node dist/cli.js remap -f diagram.drawio -m mappings/azure_to_do_supabase_odoo.yaml
```

### Supported Azure Services

See `docs/diagrams/mappings/azure_to_do_supabase_odoo.yaml` for full mapping.

| Azure Service | Target |
|--------------|--------|
| App Service | DO App Platform |
| Functions | Supabase Edge Functions |
| AKS | DOKS (DO Kubernetes) |
| SQL Database | Supabase Postgres |
| Storage Account | DO Spaces |
| Event Hub | Supabase Realtime |
| Logic Apps | n8n Workflows |

## CI Integration

The `.github/workflows/diagrams.yml` workflow:

1. Builds the diagramflow tool
2. Converts Mermaid → BPMN/draw.io
3. Checks for drift (fails if out of sync)
4. Exports PNG/SVG on main branch
5. Validates BPMN XML

## Programmatic API

```typescript
import { parseMermaid, toBpmnXml, toDrawioXml } from './dist/index.js';

const src = `
flowchart LR
  S((Start)) --> T[Task] --> E(((End)))
`;

const model = parseMermaid(src);
const bpmn = toBpmnXml(model);
const drawio = toDrawioXml(model);
```

## License

AGPL-3.0
