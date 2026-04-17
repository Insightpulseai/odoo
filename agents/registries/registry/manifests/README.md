# Agent Manifest Registry

Agent manifest registry. Each agent gets a YAML manifest file here.

## Convention

- One manifest per agent
- Filename: `<domain>--<agent-name>.yaml` (double dash separates domain from name)
- All manifests must validate against `schemas/agent/agent-manifest.schema.json`
- Registry index maintained at `ssot/manifests/persona-map.yaml`

## Status

TODO: Register first production agents when runtime integration is ready.
