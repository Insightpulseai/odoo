# Agents Registry

## SSOT + Generated Artifacts
- **SSOT:** `agents/registry/agents.yaml`
- **Generated:** `agents/registry/agents.json` (LIST SHAPE) + `agents/registry/agents.meta.json`

Regenerate:
```bash
python scripts/agents/generate_agents_json.py
```

Check (CI):
```bash
python scripts/agents/generate_agents_json.py --check
```

CI will fail if YAML changes without regenerated outputs.
