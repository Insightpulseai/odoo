# Architectural Convergence: Agentic AI, Headless ERP, and Cloud-Native Analytics

> **Pattern**: Agent-orchestrated architecture where Claude Code + VS Code orchestrates Odoo (ERP), Supabase (BaaS), Apache Superset (BI), and Next.js (headless frontend).

---

## 1. Executive Summary

The software engineering landscape is entering a major inflection point: we are moving from human-driven syntax production to **agent-orchestrated architecture and implementation**. In the 2025–2026 cycle, the developer's role is shifting into that of a *systems conductor*—someone who sets intent, defines constraints, and supervises autonomous AI agents that execute complex changes across a heterogeneous stack.

This document presents a technical blueprint for a unified, high-performance workflow that combines **Claude Code** (Sonnet 3.7 / 4.5) with **Visual Studio Code** to orchestrate an enterprise stack built on:

* **Odoo** (ERP and business logic core)
* **Supabase** (Postgres-based backend-as-a-service)
* **Apache Superset** (analytics and BI)
* **Next.js on Vercel** (headless front-end delivery)

The guiding premise is the **"Centaur" engineering model**—human intent plus machine execution. The **Model Context Protocol (MCP)** is the connective tissue that allows the AI agent to interact programmatically with the application layer (Odoo), the data layer (Supabase), and the analytics layer (Superset).

---

## 2. The Agentic Development Environment: Claude Code + VS Code

The foundation of the workflow is the tight coupling of the **IDE** with an **autonomous, tool-using agent**. VS Code provides the visual and ergonomic layer; Claude Code provides long-horizon reasoning, planning, and execution.

### 2.1 Dual-Interface Paradigm: Extension vs CLI

Engineers operate in a hybrid modality:

| Dimension       | VS Code Extension                  | Claude Code CLI                             |
| --------------- | ---------------------------------- | ------------------------------------------- |
| Primary role    | Design & review control plane      | Automation and orchestration engine         |
| Context scope   | Active files / explicit selections | Whole repo / shell / container network      |
| Execution model | Suggests edits                     | Executes commands and scripts               |
| Diff UX         | Native inline editor diffs         | Unified diff in terminal                    |
| Best for        | Complex refactors, HITL approvals  | System setup, migrations, large-scale edits |

#### VS Code Extension: The Control Plane

* **Inline diff rendering** – Proposed edits show as native VS Code diffs for surgical, line-level acceptance.
* **Context priming via @-mentions / Opt+K** – Explicitly attach files, folders, or selections to prompts.
* **Session continuity with CLI** – Resume CLI conversations via `--resume` flag.

#### Claude Code CLI: The Automation Engine

* **Deep file and dependency traversal** – Crawls manifests, imports, and tests to build project-wide models.
* **Terminal sovereignty & self-correction** – Executes a full **Plan → Act → Observe → Rectify** loop autonomously.

### 2.2 Sandboxed Workspace: DevContainers

Running a powerful agent with `--dangerously-skip-permissions` demands a **hard isolation boundary**. DevContainers provide that boundary.

#### Docker-in-Docker Topology

```
DevContainer (agent control plane)
    ↓ Docker socket access
    ├── Odoo container
    ├── Supabase stack (db, auth, rest, realtime, studio)
    ├── Superset container
    └── MCP server containers
```

Key `devcontainer.json` directives:

```json
{
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "runArgs": ["--network=host"],
  "mounts": [
    "source=claude-config,target=/home/vscode/.claude,type=volume"
  ],
  "remoteUser": "vscode"
}
```

#### `CLAUDE.md` as Context Anchor

A dedicated `CLAUDE.md` file acts as a **project constitution** that is loaded automatically at session start:

* **Architecture facts** – Stack composition and component relationships
* **Operational rules** – How to run commands (Docker wrappers, not direct binaries)
* **Coding standards** – OCA guidelines, RLS enforcement, RSC preferences

---

## 3. Backend Core: Odoo + Supabase Convergence

The goal is aligning **Odoo's monolithic ORM-driven ERP** with **Supabase's developer-first Postgres abstraction** into a single **unified data layer**:

* Odoo owns **business logic and invariants**
* Supabase exposes **modern APIs (REST, GraphQL, Realtime)**

### 3.1 Unified Database Architecture

Odoo's database is hosted inside the same Postgres engine managed by Supabase:

```yaml
services:
  db:
    image: supabase/postgres:15
    # Supabase DB config...

  odoo:
    image: odoo:19
    depends_on:
      - db
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DB_USER=odoo
      - DB_PASSWORD=${ODOO_DB_PASSWORD}
```

### 3.2 "Headless" Access Patterns

#### Direct Read APIs via PostgREST

| Operation | Route | Notes |
|-----------|-------|-------|
| **Reads** | Supabase REST/GraphQL | Product catalog, price list, inventory |
| **Writes** | Odoo controllers/XML-RPC | Ensures Python business logic executes |

This strict **read/write separation** keeps Odoo as source of truth for side effects.

#### Realtime Notifications

Supabase Realtime streams changes via Postgres WAL. Frontends subscribe via WebSocket for instant updates (e.g., stock levels).

### 3.3 Local Resource Optimization

| Technique | Impact |
|-----------|--------|
| Prune unused Supabase services | Reclaim ~500MB-1GB RAM |
| Threaded Odoo (`workers = 0`) | Avoid multiple Python processes |
| Memory limits in docker-compose | Prevent single service lockup |

---

## 4. Analytics Intelligence: Superset + MCP

Superset turns the stack into a **data-intelligent system**. With MCP, Claude becomes a **data analyst** that can verify code changes against real metrics.

### 4.1 MCP Bridges

#### Odoo MCP Server

```json
{
  "odoo": {
    "command": "docker",
    "args": ["exec", "-i", "odoo-mcp", "mcp-server-odoo"]
  }
}
```

Capabilities:
* `model_search` – Query records (invoices, partners, stock moves)
* `model_inspect` – Fetch schema, fields, relations

#### Superset MCP Server

```json
{
  "superset": {
    "command": "npx",
    "args": ["-y", "superset-mcp"]
  }
}
```

Capabilities:
* `execute_sql` – Run SQL through SQL Lab API
* `list_datasets` – Discover charts, datasets, virtual tables

---

## 5. Headless Frontend: Next.js + Vercel

The frontend is a **headless Next.js application** deployed on **Vercel**.

### 5.1 Integration Logic

| Data Type | Fetch Method | Backend |
|-----------|--------------|---------|
| **Static** (catalogs, CMS) | SSG/ISR via Supabase | Fast, SEO-friendly |
| **Dynamic** (cart, checkout) | Server Actions via Odoo | Business rules preserved |

### 5.2 Vercel Pipeline

* Each branch/PR → Vercel preview deployment
* Environment sync via `npx vercel env pull`
* Claude Code GitHub Actions for automated verification

---

## 6. Synergistic Workflow: Day in the Life

```
1. Initialization & context priming
   └── Load CLAUDE.md, query Superset via MCP, inspect Odoo models

2. Plan mode & checkpointing
   └── Enter plan mode, create checkpoint for rollback

3. TDD implementation
   └── Write failing tests → implement fixes → verify green

4. Git automation
   └── Stage, commit with semantic messages, open PR via gh CLI
```

The human stays in the loop as **architect, reviewer, and conductor**.

---

## 7. VS Code Environments vs Claude Code Capabilities

See [CLAUDE_CODE_WEB.md](../../CLAUDE_CODE_WEB.md) for the full comparison matrix.

### Quick Reference

| Environment | Claude Surface | Best For |
|-------------|----------------|----------|
| **VS Code Desktop + CLI** | Full CLI + extension | Heavy refactors, Docker orchestration, MCP debugging |
| **VS Code Web + Claude Web** | Browser sandbox | Light edits, docs, planning |
| **GitHub Codespaces + CLI** | Full CLI inside container | Cloud-hosted full power |
| **Remote Tunnels + CLI** | Full on remote host | Hybrid local UX, remote compute |

### Recommended Default

1. **Primary**: VS Code Desktop + DevContainer + Claude Code CLI
2. **Cloud variant**: GitHub Codespaces with same `.devcontainer/devcontainer.json`
3. **Browser fallback**: VS Code Web for docs/reviews only

---

## 8. Security Considerations

### `--dangerously-skip-permissions`

Only acceptable **inside the DevContainer boundary**:
* Risk: Destructive commands executed autonomously
* Mitigation: Disposable containers, narrow volume mounts

### Secrets Management

* Supabase keys via environment variables only (never committed)
* Use password manager CLI (e.g., 1Password) for runtime injection

---

## 9. Performance & Token Optimization

### Memory Strategy

```yaml
# docker-compose.yml
services:
  odoo:
    mem_limit: 1024m
  superset:
    mem_limit: 2048m
```

### Token Strategy

* Strict `.claudeignore` excluding `node_modules`, virtualenvs, logs
* Regular `/compact` calls to summarize sessions

---

## 10. Conclusion

By 2026, managing a heterogeneous stack like **Odoo + Supabase + Superset + Next.js** is no longer about juggling tools manually. With **Claude Code, VS Code, DevContainers, MCP, and Vercel**, the developer defines **intent**, and the agent executes across code, infrastructure, and analytics.

This architecture:

* **Compresses setup time** – One DevContainer + Docker stack stands up a full ERP, backend, analytics suite, and frontend locally
* **Raises quality** – Automated testing, analytics-backed verification, MCP-powered introspection
* **Improves economics** – Engineers spend time on domain modeling, not boilerplate

---

## References

1. [Claude Code in VS Code](https://code.claude.com/docs/en/vs-code)
2. [Claude Code CLI Reference](https://www.eesel.ai/blog/claude-code-cli-reference)
3. [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
4. [DevContainers for Claude Code](https://code.claude.com/docs/en/devcontainer)
5. [Supabase Self-Hosting](https://supabase.com/docs/guides/self-hosting/docker)
6. [mcp-server-odoo](https://github.com/ivnvxd/mcp-server-odoo)
7. [superset-mcp](https://github.com/Winding2020/superset-mcp)
8. [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)

---

*Last updated: 2026-01-14*
