# Antigravity MCP Configuration

## Overview
This document guides the configuration of Google Antigravity to use your local standard MCP servers (Docker, GitHub, Kubernetes).

## 1. Access Raw Config
In Antigravity: **Agent panel → `...` → MCP Servers → Manage MCP Servers → View raw config**.

## 2. Configuration Template
Use the exact same `command` and `args` that you use in VS Code or Claude Code.

```json
{
  "mcpServers": {
    "ipai-docker-gateway": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "mcp/docker"],
      "env": {}
    },

    "ipai-github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN"
      }
    }
  }
}
```
*(Update arguments above to match your actual local setup).*

## 3. Tool Parity Checklist
Confirm these tools are visible to the agent:

- **Docker**: `list_containers`, `logs`, `exec_command`
- **GitHub**: `get_file_contents`, `list_pull_requests`
- **Kubernetes** (if applicable): `list_pods`, `get_logs`
