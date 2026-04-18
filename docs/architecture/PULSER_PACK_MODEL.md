# Pulser Pack Model

Canonical sources:
- [`platform/ssot/agents/pulser-pack-matrix.yaml`](../../platform/ssot/agents/pulser-pack-matrix.yaml)
- [`platform/ssot/agents/surface-bindings.yaml`](../../platform/ssot/agents/surface-bindings.yaml)
- [`platform/ssot/agents/context-schema.yaml`](../../platform/ssot/agents/context-schema.yaml)

## Core rule

Pulser is split into:
- one shared core
- shared role packs
- domain packs
- judge packs
- surface bindings

## Authority split

- `agent-platform` owns runtime, policy, hooks, sessions, tool execution, and judge execution
- `agents` owns personas, tasks, pack manifests, and judge manifests
- `platform` owns context schema, surface bindings, and pack-to-surface mappings
- `web` owns surface UX and current-surface hints
- `odoo` owns transactional business truth and guarded tool endpoints

## Split rule

Split a domain pack only when:
- ontology diverges
- toolset diverges
- mutation risk diverges
- judge contract diverges
- tenant/surface isolation diverges

## Related

- Context awareness doctrine: [pulser-context-awareness.md](pulser-context-awareness.md)
- Hook lifecycle SSOT: [`platform/ssot/agents/pulser-hook-lifecycle.yaml`](../../platform/ssot/agents/pulser-hook-lifecycle.yaml)
- Domain packs doctrine: [`platform/ssot/agents/pulser-domain-packs.yaml`](../../platform/ssot/agents/pulser-domain-packs.yaml)
- Agent framework adoption: [agent-framework-adoption.md](agent-framework-adoption.md)
