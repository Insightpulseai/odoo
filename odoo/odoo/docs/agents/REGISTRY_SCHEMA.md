# Agent Registry Schema Reference

**Date:** 2026-02-20
**Version:** v1 (proposed)
**Status:** DRAFT

---

## Overview

This document defines machine-readable schemas for agent, tool, and knowledge source registries. These schemas enable deterministic routing, permission enforcement, and audit trail generation.

**Registry Files:**
- `agents.yaml` - Agent types, capabilities, routing rules
- `tools.yaml` - Tool declarations, permissions, secret bindings
- `knowledge.yaml` - Knowledge sources, indexing strategies, provenance

**Enforcement:**
- CI validation: JSON Schema compliance
- Runtime enforcement: Registry lookups before execution
- Audit trail: ops.runs, ops.tool_invocations, ops.knowledge_sources

---

## 1. Agent Registry Schema

### 1.1 File: `agents.yaml`

```yaml
schema_version: "v1"
last_updated: "2026-02-20T12:00:00+08:00"

agents:
  - id: "analyzer"
    name: "Analyzer Agent"
    description: "Root cause specialist, evidence-based investigator"
    capabilities:
      - "root_cause_analysis"
      - "systematic_investigation"
      - "pattern_recognition"
    routing_rules:
      keywords: ["analyze", "investigate", "root cause"]
      file_patterns: ["**/logs/*.log", "**/traces/*.json"]
      contexts: ["debugging", "troubleshooting", "incident_response"]
    delegation_policy:
      can_delegate_to: ["performance", "security", "qa"]
      delegation_triggers:
        - condition: "performance_bottleneck_detected"
          delegate_to: "performance"
        - condition: "security_vulnerability_found"
          delegate_to: "security"
    tools:
      allowed: ["Read", "Grep", "Sequential", "Playwright"]
      forbidden: ["Write", "Bash"]  # Read-only investigator
    secrets:
      required: []  # No secrets needed for analysis
    priority: 1  # Higher = selected first when multiple agents match

  - id: "architect"
    name: "Architect Agent"
    description: "Systems design and long-term architecture"
    capabilities:
      - "system_design"
      - "architecture_review"
      - "technical_debt_assessment"
    routing_rules:
      keywords: ["architecture", "design", "scalability"]
      file_patterns: ["**/architecture/**", "**/docs/ADR-*.md"]
      contexts: ["system_design", "refactoring", "architecture_review"]
    delegation_policy:
      can_delegate_to: ["frontend", "backend", "security"]
      delegation_triggers:
        - condition: "frontend_architectural_changes"
          delegate_to: "frontend"
    tools:
      allowed: ["Read", "Sequential", "Context7", "Write", "Edit"]
      forbidden: ["Bash"]  # No direct system execution
    secrets:
      required: []
    priority: 2

  # ... more agents
```

### 1.2 JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["schema_version", "last_updated", "agents"],
  "properties": {
    "schema_version": {"type": "string", "pattern": "^v\\d+$"},
    "last_updated": {"type": "string", "format": "date-time"},
    "agents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "capabilities", "routing_rules", "tools"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "capabilities": {"type": "array", "items": {"type": "string"}},
          "routing_rules": {
            "type": "object",
            "properties": {
              "keywords": {"type": "array", "items": {"type": "string"}},
              "file_patterns": {"type": "array", "items": {"type": "string"}},
              "contexts": {"type": "array", "items": {"type": "string"}}
            }
          },
          "delegation_policy": {
            "type": "object",
            "properties": {
              "can_delegate_to": {"type": "array", "items": {"type": "string"}},
              "delegation_triggers": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["condition", "delegate_to"],
                  "properties": {
                    "condition": {"type": "string"},
                    "delegate_to": {"type": "string"}
                  }
                }
              }
            }
          },
          "tools": {
            "type": "object",
            "required": ["allowed"],
            "properties": {
              "allowed": {"type": "array", "items": {"type": "string"}},
              "forbidden": {"type": "array", "items": {"type": "string"}}
            }
          },
          "secrets": {
            "type": "object",
            "properties": {
              "required": {"type": "array", "items": {"type": "string"}}
            }
          },
          "priority": {"type": "integer", "minimum": 1}
        }
      }
    }
  }
}
```

---

## 2. Tool Registry Schema

### 2.1 File: `tools.yaml`

```yaml
schema_version: "v1"
last_updated: "2026-02-20T12:00:00+08:00"

tools:
  - id: "supabase-proxy"
    name: "Supabase Proxy API"
    description: "Proxied access to Supabase Management API"
    type: "edge_function"
    path: "/supabase/functions/supabase-proxy"
    capabilities:
      - "project_management"
      - "database_queries"
      - "edge_function_deployment"
    permission_scope: "service_role"  # Requires service_role key
    secrets:
      required:
        - name: "SUPABASE_SERVICE_ROLE_KEY"
          vault_path: "supabase/service_role_key"
          rotation_cadence: "90d"
      optional: []
    rate_limits:
      requests_per_minute: 60
      requests_per_hour: 1000
    audit_trail:
      emit_to: "ops.tool_invocations"
      include_fields: ["agent_id", "correlation_id", "request_method", "response_status"]
    owner: "platform-team"

  - id: "odoo-rpc"
    name: "Odoo JSON-RPC Client"
    description: "Direct Odoo model/method calls via JSON-RPC"
    type: "http_client"
    path: "internal"  # Not an Edge Function, library usage
    capabilities:
      - "model_read"
      - "model_write"
      - "method_call"
    permission_scope: "user_scoped"  # Uses user's Odoo session
    secrets:
      required:
        - name: "ODOO_DB"
          vault_path: "odoo/database_name"
          rotation_cadence: "never"  # Database name is not a secret
        - name: "ODOO_URL"
          vault_path: "odoo/url"
          rotation_cadence: "never"
      optional:
        - name: "ODOO_API_KEY"
          vault_path: "odoo/api_key"
          rotation_cadence: "180d"
    rate_limits:
      requests_per_minute: 120
      requests_per_hour: 5000
    audit_trail:
      emit_to: "ops.tool_invocations"
      include_fields: ["agent_id", "model", "method", "args", "response_status"]
    owner: "odoo-team"

  # ... more tools
```

### 2.2 JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["schema_version", "last_updated", "tools"],
  "properties": {
    "schema_version": {"type": "string", "pattern": "^v\\d+$"},
    "last_updated": {"type": "string", "format": "date-time"},
    "tools": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "type", "capabilities", "permission_scope", "audit_trail"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "type": {"type": "string", "enum": ["edge_function", "http_client", "subprocess", "mcp_server"]},
          "path": {"type": "string"},
          "capabilities": {"type": "array", "items": {"type": "string"}},
          "permission_scope": {"type": "string", "enum": ["anon", "user_scoped", "service_role"]},
          "secrets": {
            "type": "object",
            "properties": {
              "required": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["name", "vault_path", "rotation_cadence"],
                  "properties": {
                    "name": {"type": "string"},
                    "vault_path": {"type": "string"},
                    "rotation_cadence": {"type": "string", "pattern": "^(\\d+d|never)$"}
                  }
                }
              },
              "optional": {"type": "array"}
            }
          },
          "rate_limits": {
            "type": "object",
            "properties": {
              "requests_per_minute": {"type": "integer"},
              "requests_per_hour": {"type": "integer"}
            }
          },
          "audit_trail": {
            "type": "object",
            "required": ["emit_to", "include_fields"],
            "properties": {
              "emit_to": {"type": "string"},
              "include_fields": {"type": "array", "items": {"type": "string"}}
            }
          },
          "owner": {"type": "string"}
        }
      }
    }
  }
}
```

---

## 3. Knowledge Registry Schema

### 3.1 File: `knowledge.yaml`

```yaml
schema_version: "v1"
last_updated: "2026-02-20T12:00:00+08:00"

sources:
  - id: "notion-workspace"
    name: "Notion Workspace"
    description: "Primary knowledge base for project docs, specs, meeting notes"
    type: "notion"
    connection:
      integration_token_vault_path: "notion/integration_token"
      workspace_id: "notion_workspace_id_placeholder"
    indexing:
      strategy: "incremental"
      embedding_model: "text-embedding-3-small"  # OpenAI
      chunk_size: 512
      chunk_overlap: 50
      refresh_cadence: "1h"
      last_indexed_at: "2026-02-20T11:00:00+08:00"
      staleness_threshold: "2h"  # Alert if not refreshed in 2h
    provenance:
      track_source_page_id: true
      track_chunk_id: true
      track_confidence_score: true
      emit_to: "ops.knowledge_retrievals"
    owner: "platform-team"

  - id: "google-drive"
    name: "Google Drive (Shared Drives)"
    description: "Financial docs, contracts, templates"
    type: "google_drive"
    connection:
      service_account_vault_path: "google/service_account_key"
      shared_drive_ids: ["drive_id_1", "drive_id_2"]
    indexing:
      strategy: "full_rescan"  # Drive has no incremental API
      embedding_model: "text-embedding-3-small"
      chunk_size: 512
      chunk_overlap: 50
      refresh_cadence: "24h"
      last_indexed_at: "2026-02-19T12:00:00+08:00"
      staleness_threshold: "48h"
    provenance:
      track_source_file_id: true
      track_chunk_id: true
      track_confidence_score: true
      emit_to: "ops.knowledge_retrievals"
    owner: "finance-team"

  # ... more sources
```

### 3.2 JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["schema_version", "last_updated", "sources"],
  "properties": {
    "schema_version": {"type": "string", "pattern": "^v\\d+$"},
    "last_updated": {"type": "string", "format": "date-time"},
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "type", "connection", "indexing", "provenance"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "type": {"type": "string", "enum": ["notion", "google_drive", "slack", "github", "confluence"]},
          "connection": {
            "type": "object",
            "properties": {
              "integration_token_vault_path": {"type": "string"},
              "service_account_vault_path": {"type": "string"},
              "workspace_id": {"type": "string"},
              "shared_drive_ids": {"type": "array", "items": {"type": "string"}}
            }
          },
          "indexing": {
            "type": "object",
            "required": ["strategy", "embedding_model", "refresh_cadence", "staleness_threshold"],
            "properties": {
              "strategy": {"type": "string", "enum": ["incremental", "full_rescan"]},
              "embedding_model": {"type": "string"},
              "chunk_size": {"type": "integer"},
              "chunk_overlap": {"type": "integer"},
              "refresh_cadence": {"type": "string", "pattern": "^\\d+(h|d)$"},
              "last_indexed_at": {"type": "string", "format": "date-time"},
              "staleness_threshold": {"type": "string", "pattern": "^\\d+(h|d)$"}
            }
          },
          "provenance": {
            "type": "object",
            "required": ["emit_to"],
            "properties": {
              "track_source_page_id": {"type": "boolean"},
              "track_source_file_id": {"type": "boolean"},
              "track_chunk_id": {"type": "boolean"},
              "track_confidence_score": {"type": "boolean"},
              "emit_to": {"type": "string"}
            }
          },
          "owner": {"type": "string"}
        }
      }
    }
  }
}
```

---

## 4. Supabase Integration (ops.* Tables)

### 4.1 Proposed Table Schemas

#### `ops.runs` (enhanced)

```sql
create table if not exists ops.runs (
  id uuid primary key default gen_random_uuid(),
  correlation_id text not null,
  agent_id text references agents.registry(id),  -- NEW: FK to agent registry
  task_name text not null,
  status text not null check (status in ('pending', 'running', 'completed', 'failed')),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  metadata jsonb,
  created_at timestamptz not null default now()
);
```

#### `ops.tool_invocations` (new)

```sql
create table if not exists ops.tool_invocations (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references ops.runs(id) on delete cascade,
  tool_id text references tools.registry(id),  -- FK to tool registry
  agent_id text references agents.registry(id),  -- Which agent invoked
  invoked_at timestamptz not null default now(),
  request_method text,
  request_params jsonb,
  response_status int,
  response_body jsonb,
  duration_ms int,
  correlation_id text not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);
```

#### `ops.knowledge_retrievals` (new)

```sql
create table if not exists ops.knowledge_retrievals (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references ops.runs(id) on delete cascade,
  source_id text references knowledge.registry(id),  -- FK to knowledge registry
  query_text text not null,
  source_page_id text,  -- Notion page ID
  source_file_id text,  -- Drive file ID
  chunk_id text,
  confidence_score decimal(3, 2),  -- 0.00-1.00
  retrieved_at timestamptz not null default now(),
  correlation_id text not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);
```

---

## 5. Validation Scripts

### 5.1 Schema Validator (Python)

```bash
#!/usr/bin/env python3
# scripts/ci/validate_agent_registry.py

import yaml
import jsonschema
import sys

def load_schema(schema_path):
    with open(schema_path) as f:
        return yaml.safe_load(f)

def validate_registry(registry_path, schema_path):
    registry = load_schema(registry_path)
    schema = load_schema(schema_path)
    try:
        jsonschema.validate(instance=registry, schema=schema)
        print(f"✅ {registry_path} is valid")
        return 0
    except jsonschema.ValidationError as e:
        print(f"❌ {registry_path} validation failed: {e.message}")
        return 1

if __name__ == "__main__":
    exit_code = 0
    exit_code |= validate_registry("agents.yaml", "schemas/agents.schema.json")
    exit_code |= validate_registry("tools.yaml", "schemas/tools.schema.json")
    exit_code |= validate_registry("knowledge.yaml", "schemas/knowledge.schema.json")
    sys.exit(exit_code)
```

### 5.2 CI Workflow Integration

```yaml
# .github/workflows/agent-registry-validation.yml
name: Agent Registry Validation

on:
  pull_request:
    paths:
      - 'agents.yaml'
      - 'tools.yaml'
      - 'knowledge.yaml'
      - 'schemas/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate registries
        run: python scripts/ci/validate_agent_registry.py
```

---

## 6. Usage Patterns

### 6.1 Agent Selection Flow

```python
# pseudocode
def select_agent(task_context, file_patterns, keywords):
    registry = load_yaml("agents.yaml")
    candidates = []

    for agent in registry["agents"]:
        score = 0

        # Keyword matching
        if any(kw in keywords for kw in agent["routing_rules"]["keywords"]):
            score += 10

        # File pattern matching
        if any(matches_pattern(fp, file_patterns) for fp in agent["routing_rules"]["file_patterns"]):
            score += 5

        # Context matching
        if task_context in agent["routing_rules"]["contexts"]:
            score += 8

        candidates.append((agent["id"], score + agent.get("priority", 0)))

    # Sort by score, highest first
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0] if candidates else "default"
```

### 6.2 Tool Permission Check

```python
def check_tool_permission(agent_id, tool_id):
    agents_registry = load_yaml("agents.yaml")
    agent = find_agent_by_id(agents_registry, agent_id)

    if tool_id in agent["tools"]["forbidden"]:
        raise PermissionError(f"Agent {agent_id} forbidden from using {tool_id}")

    if tool_id not in agent["tools"]["allowed"]:
        raise PermissionError(f"Agent {agent_id} not allowed to use {tool_id}")

    return True
```

### 6.3 Knowledge Provenance Tracking

```python
async def retrieve_with_provenance(query, source_id, run_id):
    source = find_knowledge_source(source_id)
    chunks = await vector_search(query, source["indexing"]["embedding_model"])

    for chunk in chunks:
        await supabase.from_("ops.knowledge_retrievals").insert({
            "run_id": run_id,
            "source_id": source_id,
            "query_text": query,
            "source_page_id": chunk.metadata.get("page_id"),
            "chunk_id": chunk.id,
            "confidence_score": chunk.score,
            "correlation_id": current_correlation_id()
        })

    return chunks
```

---

## 7. Cross-References

- **Assessment:** `docs/agents/REGISTRY_ASSESSMENT.md`
- **Spec bundle:** `spec/agent-registry/` (to be created)
- **SSOT policy:** `spec/odoo-ee-parity-seed/constitution.md` (Article: Supabase SSOT)
- **Migration guide:** TBD (to be created in Phase 2)
