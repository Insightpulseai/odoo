# Agent Router (CLI)

Deterministic router:

- Inputs: capability id + goal + context
- Loads: taxonomy YAML + agent matrix YAML + prompt pack (md)
- Outputs: selected primary agent, support agents, and a fully rendered AGENT RELAY prompt

## Usage

```bash
# Route a request (JSON in, JSON out)
cat request.json | node tools/agent-router/dist/cli.js route

# List capabilities
node tools/agent-router/dist/cli.js list-capabilities

# List agents for a capability
node tools/agent-router/dist/cli.js list-agents --capability odoo_implementation
```

## Config

Defaults assume you have:

- spec/taxonomy/capabilities_consulting_delivery.yaml
- spec/agents/agent_capability_matrix.yaml
- agents/library/ (prompt pack directory)

Override with env:

- AGENT_ROUTER_TAXONOMY
- AGENT_ROUTER_MATRIX
- AGENT_ROUTER_PROMPTS_DIR
