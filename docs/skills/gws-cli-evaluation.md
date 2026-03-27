# Google Workspace CLI (gws) -- Comprehensive Evaluation

> Research date: 2026-03-27
> Repository: https://github.com/googleworkspace/cli
> Version evaluated: 0.22.3
> Relevance: Gmail-to-Odoo add-on, agent skills, MCP integration

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [What is gws CLI](#2-what-is-gws-cli)
3. [Architecture](#3-architecture)
4. [Authentication Model](#4-authentication-model)
5. [AI Agent Skills System](#5-ai-agent-skills-system)
6. [Helper Commands (+ Prefix Pattern)](#6-helper-commands--prefix-pattern)
7. [Apps Script Integration](#7-apps-script-integration)
8. [Gmail Operations](#8-gmail-operations)
9. [MCP Integration](#9-mcp-integration)
10. [Workspace Events API](#10-workspace-events-api)
11. [Crate / Library Architecture](#11-crate--library-architecture)
12. [Security Considerations](#12-security-considerations)
13. [Evaluation for InsightPulseAI](#13-evaluation-for-insightpulseai)
14. [Adoption Recommendation](#14-adoption-recommendation)
15. [Risk Assessment](#15-risk-assessment)
16. [Sources](#16-sources)

---

## 1. Executive Summary

`gws` is a Rust-based, community-maintained CLI that provides a unified interface to all Google Workspace APIs. It dynamically reads Google Discovery Documents at runtime, meaning it automatically supports new APIs and methods without CLI updates. The project has 22.7k stars, 1.1k forks, 95 skill definitions, and releases every 1-2 weeks. It is explicitly designed for both human operators and AI agents.

**Key finding for InsightPulseAI**: `gws` is a strong complement to our existing Gmail add-on but does NOT replace it. The add-on runs in-browser as a Gmail sidebar (Google Apps Script); `gws` runs as a CLI/agent tool on a server or workstation. They serve different execution surfaces. However, `gws script +push` can replace `clasp` for deployment, and the agent skills system aligns with our MCP-first architecture.

**Verdict**: Adopt incrementally. Use `gws script +push` for deployment now. Evaluate agent skills integration for Claude Code workflows. Do not replace the Gmail add-on with gws.

---

## 2. What is gws CLI

### Identity

| Attribute | Value |
|-----------|-------|
| Name | `gws` (Google Workspace CLI) |
| Language | Rust (binary), npm wrapper for distribution |
| npm package | `@googleworkspace/cli` |
| Stars | 22.7k |
| Forks | 1.1k |
| Open issues | 44 |
| License | Apache-2.0 |
| Status | Pre-1.0 (breaking changes expected) |
| Maintainer | Justin Poehnelt (community, not official Google product) |
| Release cadence | Every 1-2 weeks |

### Installation Methods

```bash
# npm (recommended -- includes pre-built native binaries)
npm install -g @googleworkspace/cli

# Homebrew
brew install googleworkspace-cli

# Cargo (build from source)
cargo install --git https://github.com/googleworkspace/cli --locked

# Nix
nix run github:googleworkspace/cli

# GitHub Releases (pre-built binaries for macOS, Linux, Windows)
```

Requires: Node.js 18+, a Google Cloud project, a Google Workspace account.

### What It Covers

Drive, Gmail, Calendar, Sheets, Docs, Chat, Meet, Admin, Tasks, Keep, Classroom, Forms, Slides, People, Apps Script, and any other API registered in Google Discovery Service. New APIs are automatically available without CLI updates.

---

## 3. Architecture

### Two-Phase Parsing

This is the core architectural innovation. Instead of maintaining static command definitions for hundreds of API methods:

1. **Phase 1**: Read `argv[1]` to identify the target service (e.g., `gmail`)
2. **Phase 2**: Fetch the service's Discovery Document (cached 24h), dynamically build a `clap::Command` tree from resources and methods
3. **Phase 3**: Re-parse remaining arguments against the generated command structure
4. **Phase 4**: Authenticate, construct HTTP request, execute

This means `gws` never goes stale. When Google adds a new API method, `gws` picks it up automatically on the next invocation after cache expiry.

### Output Model

All output -- success, errors, metadata -- is structured JSON. This is explicitly designed for agent consumption.

```bash
# NDJSON streaming for paginated results
gws drive files list --params '{"pageSize": 100}' --page-all

# Schema inspection (agents use this to discover parameters)
gws schema drive.files.list
```

### Pagination

| Flag | Purpose | Default |
|------|---------|---------|
| `--page-all` | Fetch all pages, output as NDJSON | off |
| `--page-limit <N>` | Maximum pages to retrieve | 10 |
| `--page-delay <MS>` | Delay between page requests | 100ms |

### Exit Codes

Structured for script/agent branching without parsing output:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error (Google returned 4xx/5xx) |
| 2 | Auth error (credentials missing/invalid) |
| 3 | Validation error (bad arguments, unknown service) |
| 4 | Discovery error (failed to fetch API schema) |
| 5 | Internal error (unexpected failure) |

### Key Flags

| Flag | Purpose |
|------|---------|
| `--dry-run` | Local validation only, no API call |
| `--format <json\|table\|yaml\|csv>` | Output format (JSON default) |
| `--sanitize <template>` | Filter response through Model Armor |
| `--upload <path>` | Multipart file upload |
| `-o / --output <path>` | Write binary response to file |
| `--params '<json>'` | URL/query parameters |
| `--json '<json>'` | Request body |

---

## 4. Authentication Model

### Priority Hierarchy

| Priority | Source | Method |
|----------|--------|--------|
| 1 (highest) | Access token | `GOOGLE_WORKSPACE_CLI_TOKEN` env var |
| 2 | Credentials file | `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` path |
| 3 | Encrypted local credentials | Output from `gws auth login` |
| 4 (lowest) | Plaintext stored credentials | `~/.config/gws/credentials.json` |

### Auth Methods

**Interactive desktop (fastest)**:
```bash
gws auth setup     # Automates Cloud project creation via gcloud
gws auth login     # OAuth browser flow with scope selection
```

**Manual OAuth**:
Download `client_secret.json` from GCP Console, place in `~/.config/gws/`, run `gws auth login`.

**Headless/CI**:
```bash
# On authenticated machine:
gws auth export > credentials.json

# On CI runner:
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=./credentials.json
```

**Service account**:
```bash
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=./service-account-key.json
```

**Pre-obtained token** (for integration with existing OAuth systems):
```bash
export GOOGLE_WORKSPACE_CLI_TOKEN="ya29.a0AfH6SM..."
```

### Credential Security

- Encrypted at rest using AES-256-GCM
- OS keyring integration on macOS (Keychain) and Windows (Credential Manager)
- v0.22.3 hardened to use strict OS keychain instead of fallback encryption files

### Scope Management

Testing-mode OAuth apps are limited to ~25 scopes. The recommended scope preset includes 85+ scopes and will fail for unverified apps. For unverified apps:
```bash
gws auth login -s drive,gmail,sheets    # Select specific scopes
```

The authenticated user must be added as a test user in the GCP OAuth consent screen.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_WORKSPACE_CLI_TOKEN` | Pre-obtained OAuth2 token |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | Path to OAuth/service-account JSON |
| `GOOGLE_WORKSPACE_CLI_CLIENT_ID` | OAuth client ID |
| `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` | Override config directory |
| `GOOGLE_WORKSPACE_CLI_SANITIZE_TEMPLATE` | Default Model Armor template |
| `GOOGLE_WORKSPACE_CLI_SANITIZE_MODE` | `warn` (default) or `block` |
| `GOOGLE_WORKSPACE_CLI_LOG` | Log level for stderr |
| `GOOGLE_WORKSPACE_CLI_LOG_FILE` | JSON log directory with rotation |
| `GOOGLE_WORKSPACE_PROJECT_ID` | GCP project ID override |

---

## 5. AI Agent Skills System

### Overview

The `skills/` directory contains **95 skill definitions** organized into three categories:

| Category | Count | Pattern | Purpose |
|----------|-------|---------|---------|
| Services | ~19 | `gws-<service>` | Core API coverage per Google service |
| Helpers | ~25 | `gws-<service>-<verb>` | Individual + prefix command skills |
| Personas | 10 | `persona-<role>` | Role-based skill bundles |
| Recipes | ~46 | `recipe-<workflow>` | Multi-step workflow compositions |

### Service Skills (gws-*)

Each service skill contains a `SKILL.md` file that instructs AI agents how to use `gws` for that service:

- `gws-gmail` -- Email management (list, read, send, search, labels)
- `gws-drive` -- File operations (list, upload, share, search)
- `gws-calendar` -- Event management (list, create, update, agenda)
- `gws-sheets` -- Spreadsheet operations (read, append, update)
- `gws-docs` -- Document operations (read, write, batch update)
- `gws-chat` -- Chat messaging (spaces, messages)
- `gws-script` -- Apps Script management (create, push, run)
- `gws-forms`, `gws-slides`, `gws-tasks`, `gws-keep`, `gws-meet`
- `gws-classroom`, `gws-admin-reports`, `gws-people`
- `gws-events` -- Workspace Events API subscriptions
- `gws-modelarmor` -- Prompt/response sanitization

### Helper Skills (gws-*-verb)

Individual skills for each + prefix command:

- `gws-gmail-send`, `gws-gmail-reply`, `gws-gmail-reply-all`, `gws-gmail-forward`
- `gws-gmail-triage`, `gws-gmail-watch`, `gws-gmail-read`
- `gws-sheets-append`, `gws-sheets-read`
- `gws-docs-write`
- `gws-chat-send`
- `gws-drive-upload`
- `gws-calendar-insert`, `gws-calendar-agenda`
- `gws-script-push`
- `gws-events-subscribe`, `gws-events-renew`
- `gws-modelarmor-sanitize-prompt`, `gws-modelarmor-sanitize-response`, `gws-modelarmor-create-template`

### Persona Skills

Pre-bundled role-based skill packages:

| Persona | Likely Bundle |
|---------|---------------|
| `persona-exec-assistant` | Gmail + Calendar + Drive + Docs |
| `persona-project-manager` | Tasks + Sheets + Calendar + Chat |
| `persona-sales-ops` | Gmail + Sheets + Calendar + CRM workflows |
| `persona-hr-coordinator` | Forms + Sheets + Calendar + People |
| `persona-it-admin` | Admin + Directory + Security |
| `persona-content-creator` | Docs + Drive + Slides |
| `persona-customer-support` | Gmail + Tasks + Sheets |
| `persona-researcher` | Drive + Docs + Sheets |
| `persona-event-coordinator` | Calendar + Forms + Chat |
| `persona-team-lead` | Chat + Calendar + Tasks + Sheets |

### Recipe Skills (~46 workflows)

Multi-step compositions like:
- Email label/archive automation
- Email-to-task conversion
- Standup report generation
- Meeting prep with agenda + docs
- Weekly digest compilation
- File announcement to Chat spaces
- Contact sync to Sheets
- Shared drive creation

### Installation

```bash
# Install ALL skills (all 95)
npx skills add https://github.com/googleworkspace/cli

# Install specific service skills
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-drive
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-script
```

### Gemini CLI Extension

```bash
gws auth setup
gemini extensions install https://github.com/googleworkspace/cli
```

This grants Gemini CLI agents direct access to all gws commands and skills, leveraging the CLI's credential management. Note: this is Gemini-specific, not Claude-specific.

### Skill File Format (SKILL.md)

Each skill file follows a structured format that tells AI agents:

1. **What the skill does** (description, category)
2. **Prerequisites** (gws binary on PATH, authentication)
3. **Available commands** with parameter schemas
4. **Discovery pattern**: agents use `gws <service> --help` and `gws schema <service>.<resource>.<method>` to explore
5. **Security rules**: never expose secrets, use `--dry-run` for destructive ops, use `--sanitize` for sensitive data

The `gws-shared` skill provides cross-cutting installation and authentication patterns used by all other skills.

---

## 6. Helper Commands (+ Prefix Pattern)

Helper commands use a `+` prefix to visually distinguish them from raw API calls. They are hand-crafted convenience wrappers that handle common workflows with sensible defaults.

### Gmail Helpers

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `gws gmail +send` | Send email | `--to`, `--subject`, `--body`, `--draft` |
| `gws gmail +reply` | Reply with auto-threading | message ID |
| `gws gmail +reply-all` | Reply-all with auto-threading | message ID |
| `gws gmail +forward` | Forward to new recipients | message ID, `--to` |
| `gws gmail +triage` | Unread inbox summary | sender, subject, date |
| `gws gmail +watch` | Stream new emails as NDJSON | real-time |
| `gws gmail +read` | Read message body/headers | message ID |

### Sheets Helpers

| Command | Purpose |
|---------|---------|
| `gws sheets +append` | Add row to spreadsheet |
| `gws sheets +read` | Read cell range |

### Other Service Helpers

| Command | Purpose |
|---------|---------|
| `gws docs +write` | Append text to document |
| `gws chat +send` | Send message to Chat space |
| `gws drive +upload` | Upload file with auto metadata |
| `gws calendar +insert` | Create event |
| `gws calendar +agenda` | Show upcoming events (timezone-aware, 24h cache) |

### Apps Script Helper

| Command | Purpose |
|---------|---------|
| `gws script +push` | Replace all files in Apps Script project with local files |

### Workflow Helpers (Multi-Service)

| Command | Purpose |
|---------|---------|
| `gws workflow +standup-report` | Today's meetings + open tasks |
| `gws workflow +meeting-prep` | Next meeting agenda + linked docs |
| `gws workflow +email-to-task` | Convert Gmail message to Tasks entry |
| `gws workflow +weekly-digest` | Weekly meetings + unread summary |
| `gws workflow +file-announce` | Announce Drive file in Chat space |

### Events Helpers

| Command | Purpose |
|---------|---------|
| `gws events +subscribe` | Subscribe to Workspace Events, stream NDJSON |
| `gws events +renew` | Reactivate subscriptions |

### Model Armor Helpers

| Command | Purpose |
|---------|---------|
| `gws modelarmor +sanitize-prompt` | Scan user prompt through template |
| `gws modelarmor +sanitize-response` | Scan model response through template |
| `gws modelarmor +create-template` | Create Model Armor template |

### Design Principle

From AGENTS.md: helper commands (`+verb` prefix) are restricted to orchestration logic, NOT simple wrappers around single API calls. Agents should use `--params` and `--format/jq` for API parameters and output filtering rather than custom flags.

---

## 7. Apps Script Integration

### The +push Command

`gws script +push` replaces all files in an Apps Script project with local files. This is functionally equivalent to `clasp push` but uses the gws authentication model.

### Full Script API Surface

| Method | Purpose |
|--------|---------|
| `gws script projects create` | Create new blank script project |
| `gws script projects get` | Get project metadata |
| `gws script projects getContent` | Get all project files + metadata |
| `gws script projects updateContent` | Replace project files (what +push wraps) |
| `gws script projects getMetrics` | Execution statistics |
| `gws script projects deployments list` | List deployments |
| `gws script projects deployments create` | Create deployment |
| `gws script projects versions list` | List versions |
| `gws script projects versions create` | Create version |
| `gws script scripts run` | Execute script remotely |
| `gws script processes list` | List user-initiated processes |
| `gws script processes listScriptProcesses` | List script-specific processes |

### Comparison: gws script +push vs clasp push

| Feature | `clasp push` | `gws script +push` |
|---------|-------------|-------------------|
| Auth model | clasp-specific OAuth | gws unified OAuth (shared with all services) |
| File format | `.clasp.json` + `.claspignore` | Unknown (likely similar project config) |
| TypeScript support | Built-in transpilation | Not documented (likely raw GS files only) |
| Deployment | `clasp deploy` | `gws script projects deployments create` |
| Version management | `clasp version` | `gws script projects versions create` |
| Credential storage | `~/.clasprc.json` (plaintext) | AES-256-GCM encrypted + OS keyring |
| Remote execution | `clasp run` | `gws script scripts run` |
| Project creation | `clasp create` | `gws script projects create` |
| Watch mode | `clasp push --watch` | Not documented |
| Ecosystem | Mature, stable, Google-maintained | Pre-1.0, community-maintained |

### Relevance to Our Add-on

Our Gmail add-on (`web/apps/gmail-odoo-addon/`) currently uses:
- `clasp` for deployment (`.clasp.json` with scriptId `1QaH14jbBl7PcvjLXgkzZogh6SzqS_kXoTJ_MzzmavW6CRLMANG24Ko4q`)
- TypeScript sources in `src/` transpiled to `.gs` files
- `.claspignore` for exclusion rules

`gws script +push` could replace `clasp push` with better credential security, but we would need to verify TypeScript transpilation support. If gws only pushes raw `.gs` files, we would need to maintain the TS build step separately.

---

## 8. Gmail Operations

### What Our Add-on Does (Apps Script in Gmail Sidebar)

| Operation | Implementation | Surface |
|-----------|---------------|---------|
| Show sender context | `fetchBridge(API_PATHS.context)` | Gmail sidebar card |
| Create CRM lead | `fetchBridge(API_PATHS.createLead)` | Button in sidebar |
| Create project ticket | `fetchBridge(API_PATHS.createTicket)` | Button in sidebar |
| Log note to chatter | `fetchBridge(API_PATHS.logNote)` | Button in sidebar |
| Open record in Odoo | `openInOdoo()` via OpenLink | Button in sidebar |
| Auth (Entra/Google/API key) | Provider-first OAuth flow | Login card in sidebar |

### What gws Gmail Can Do

| Operation | gws Command | Surface |
|-----------|------------|---------|
| Read email body/headers | `gws gmail +read` | CLI/agent |
| Send email | `gws gmail +send` | CLI/agent |
| Reply with threading | `gws gmail +reply` | CLI/agent |
| Reply all | `gws gmail +reply-all` | CLI/agent |
| Forward | `gws gmail +forward` | CLI/agent |
| Triage (unread summary) | `gws gmail +triage` | CLI/agent |
| Watch for new emails | `gws gmail +watch` (NDJSON stream) | CLI/agent |
| List messages | `gws gmail users messages list` | CLI/agent |
| Get message | `gws gmail users messages get` | CLI/agent |
| Manage labels | `gws gmail users labels *` | CLI/agent |
| Push notifications | `gws gmail users watch/stop` | CLI/agent |

### Key Difference

**Our add-on runs IN Gmail** (sidebar UI, Apps Script runtime, CardService rendering). It provides a native Gmail experience where users click buttons to create Odoo records.

**gws runs OUTSIDE Gmail** (CLI, agent, server-side). It provides programmatic access to Gmail data for automation, batch processing, and agent workflows.

They are complementary, not competitive:
- Add-on = user-facing interactive surface in Gmail
- gws = backend/agent automation surface for Gmail data

### Potential Backend Use

`gws gmail +watch` could replace or complement our n8n Gmail trigger for detecting new emails and routing them to Odoo. The NDJSON streaming model is more efficient than polling.

---

## 9. MCP Integration

### Current State

The README changelog mentions "MCP server support" as a recent feature. The CLI is designed for structured JSON output, which is the native format for MCP tool responses.

### How gws Could Serve as an MCP Tool Server

gws's architecture is naturally MCP-compatible:

1. **Structured JSON output** -- every command returns JSON, which maps directly to MCP tool responses
2. **Schema introspection** -- `gws schema <method>` provides parameter schemas that could generate MCP tool definitions
3. **Deterministic exit codes** -- enable reliable error handling in MCP tool wrappers
4. **`--dry-run`** -- supports the MCP pattern of validation before execution

### Integration Pattern for InsightPulseAI

```
Claude Code Agent
  |
  +-- MCP Tool Server (thin wrapper)
       |
       +-- gws gmail +triage       --> unread email summary
       +-- gws gmail +read         --> email content
       +-- gws drive files list    --> drive listing
       +-- gws sheets +append      --> log data to sheets
       +-- gws script +push        --> deploy Apps Script
       +-- gws calendar +agenda    --> upcoming events
```

Each gws command would be exposed as an MCP tool with:
- Input schema derived from `gws schema <method>`
- Output as raw JSON (gws default)
- Error handling via exit codes

### Overlap with Existing MCP Servers

| Existing MCP Server | gws Equivalent | Overlap |
|---------------------|---------------|---------|
| `claude.ai/Gmail` | `gws gmail *` | High -- both read/draft Gmail |
| `claude.ai/Google_Calendar` | `gws calendar *` | High -- both manage events |
| None | `gws drive *` | New capability |
| None | `gws sheets *` | New capability |
| None | `gws script *` | New capability |
| None | `gws chat *` | New capability |

**Observation**: We already have Gmail and Calendar MCP integrations via Claude.ai remote servers. gws would add Drive, Sheets, Script, Chat, and the full API surface. The question is whether to run gws as a local MCP server or continue using the Claude.ai remote servers for Gmail/Calendar.

### Compact Tool Mode

The changelog references compact tool mode for MCP. This likely means gws can output minimal JSON suitable for MCP tool responses (stripped metadata, just the essential data). This needs further investigation once documented.

---

## 10. Workspace Events API

### What It Does

The Workspace Events API provides real-time event streaming for Google Workspace resources.

```bash
# Subscribe to events on a resource (e.g., a Drive folder, a Chat space)
gws events +subscribe

# Renew an expiring subscription
gws events +renew
```

Events are streamed as NDJSON, meaning each event is a newline-delimited JSON object -- ideal for piping to processing tools.

### Relevance to InsightPulseAI

Our current automation layer uses n8n for event-driven workflows (Gmail triggers, webhook receivers). The Workspace Events API could complement this by providing:

1. **Real-time Gmail notifications** -- instead of polling, subscribe to mailbox changes
2. **Drive change tracking** -- detect when shared documents are modified
3. **Chat activity monitoring** -- track messages in Chat spaces for Odoo routing

### Integration with n8n

n8n could invoke `gws events +subscribe` via an Execute Command node, then process the NDJSON stream. Alternatively, a dedicated agent could maintain subscriptions and forward events to n8n webhooks.

---

## 11. Crate / Library Architecture

### Workspace Structure

```
crates/
  google-workspace-cli/     # The CLI binary crate
  google-workspace/          # The library crate (reusable)
skills/                      # 95 SKILL.md agent definitions
docs/                        # Documentation
scripts/                     # Build and release scripts
.agent/                      # Agent configuration
.claude/                     # Claude Code configuration
.gemini/                     # Gemini CLI configuration
```

### Library Crate: `google-workspace`

| Attribute | Value |
|-----------|-------|
| Version | 0.22.3 |
| Description | Discovery Document types, service registry, HTTP utilities |
| License | Apache-2.0 |

**Core Dependencies**:
- `reqwest` 0.12 (HTTP client with JSON + native TLS)
- `serde` / `serde_json` (serialization)
- `tokio` (async runtime with time + filesystem features)
- `thiserror` + `anyhow` (error handling)
- `tracing` (structured logging)
- `percent-encoding` 2.3.2 (URL encoding)

### Independent Use

The `google-workspace` library crate can be used independently from the CLI. Rust developers can depend on it directly to:
- Parse Google Discovery Documents
- Use the service registry
- Leverage the HTTP utilities for Google API calls
- Build custom Workspace tools without the CLI layer

This is relevant if we ever build Rust-based agent tooling or need low-level Google API access in a custom binary.

---

## 12. Security Considerations

### Credential Encryption

- AES-256-GCM encryption at rest
- OS keyring integration (macOS Keychain, Windows Credential Manager)
- v0.22.3 hardened to prefer strict OS keychain over fallback encryption files
- Priority system ensures pre-obtained tokens (most restrictive) are preferred over stored credentials

### Model Armor Integration

Google Cloud Model Armor can sanitize API responses to defend against prompt injection:

```bash
# Per-command sanitization
gws gmail users messages get --params '...' \
  --sanitize "projects/P/locations/L/templates/T"

# Global default via env var
export GOOGLE_WORKSPACE_CLI_SANITIZE_TEMPLATE="projects/P/locations/L/templates/T"
export GOOGLE_WORKSPACE_CLI_SANITIZE_MODE="warn"  # or "block"
```

Helpers for template management:
```bash
gws modelarmor +create-template    # Create sanitization template
gws modelarmor +sanitize-prompt    # Scan user prompt
gws modelarmor +sanitize-response  # Scan model response
```

### Input Validation (from AGENTS.md)

The CLI explicitly assumes agent-provided inputs can be adversarial:
- Path traversal prevention (3 validators)
- Symlink attack protection
- Percent-encoding for URL path segments
- Resource name validation to prevent injection through identifiers
- CLI arguments treated as untrusted (from agents); env vars treated as trusted (from users)

### OAuth Scope Management

- Testing-mode apps limited to ~25 scopes
- Full scope preset requires app verification (85+ scopes)
- Scope selection via `-s` flag allows minimal-privilege operation
- Each auth session is bound to selected scopes

### Risks

1. **Pre-1.0 status**: Breaking changes expected. Do not build critical infrastructure on unstable APIs.
2. **Community-maintained**: "This is not an officially supported Google product." No SLA, no guaranteed support.
3. **Scope creep**: The 85+ scope preset grants very broad access. Always use minimal scopes.
4. **Credential file exposure**: Despite encryption, the local credential store is a high-value target.

---

## 13. Evaluation for InsightPulseAI

### Can `gws script +push` Replace clasp?

**Partially, yes.** For pushing raw `.gs` files to Apps Script, `gws script +push` is a viable replacement with better credential security. However:

- Our add-on uses TypeScript sources (`src/*.ts`) transpiled to `.gs` files. clasp handles this natively; gws likely does not.
- Recommendation: Keep the TS build step, use `gws script +push` for the final push of `.gs` artifacts. Or keep clasp if TS transpilation is critical.

### Can gws Agent Skills Integrate with Claude Code?

**Yes.** The SKILL.md format is agent-agnostic. The repo already has a `.claude/` directory with Claude Code configuration. Skills can be:

1. Installed into our repo: `npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail`
2. Referenced by Claude Code agents for Workspace operations
3. Used alongside our existing MCP integrations

However, we already have Claude.ai Gmail and Calendar MCP servers. Adding gws skills would create overlapping capabilities. The value-add is for services we lack: Drive, Sheets, Script, Chat.

### Should We Install gws Skills into Our Repo?

**Selectively.** Install skills for services we lack MCP coverage for:

| Skill | Install? | Reason |
|-------|----------|--------|
| `gws-script` + `gws-script-push` | Yes | Replaces clasp workflow |
| `gws-drive` + `gws-drive-upload` | Yes | No current Drive MCP |
| `gws-sheets` + `gws-sheets-append` | Yes | No current Sheets MCP |
| `gws-chat` + `gws-chat-send` | Maybe | Could complement Slack |
| `gws-gmail` + helpers | No | Already have Claude.ai Gmail MCP |
| `gws-calendar` + helpers | No | Already have Claude.ai Calendar MCP |
| `gws-shared` | Yes | Required by all other skills |
| `persona-*` | No | Too broad, not our workflow |
| `recipe-*` | Selective | Evaluate email-to-task, standup-report |

### Can gws Serve as Auth Bridge Between Gmail and Odoo?

**No.** gws authenticates to Google Workspace APIs. Our add-on authenticates to Odoo via a separate OAuth/API-key flow (Entra/Google/local_odoo). These are different auth domains:

- gws auth = user-to-Google (for reading/writing Workspace data)
- Add-on auth = user-to-Odoo (for creating ERP records)

gws cannot replace the Odoo bridge authentication. They solve different problems.

### How Does the Gemini CLI Extension Relate to Our Claude Stack?

**It does not directly apply.** The Gemini CLI extension is for Gemini agents, not Claude agents. However, the underlying SKILL.md format is agent-agnostic, so the skills themselves work with any agent that can read SKILL.md files and execute CLI commands.

### What Is the Overlap with Existing MCP Servers?

See Section 9. Gmail and Calendar overlap with our Claude.ai MCP servers. Drive, Sheets, Script, Chat, Events are net-new capabilities.

---

## 14. Adoption Recommendation

### Phase 1: Now (Low Risk)

| Action | Effort | Value |
|--------|--------|-------|
| Install `gws` globally on dev machines | 5 min | Workspace CLI access |
| Authenticate via `gws auth login -s script` | 5 min | Script API access |
| Test `gws script +push` with our add-on `.gs` files | 30 min | Evaluate clasp replacement |
| Install `gws-shared` + `gws-script` skills | 5 min | Agent skill for deployment |

### Phase 2: Short-term (Medium Risk)

| Action | Effort | Value |
|--------|--------|-------|
| Install `gws-drive` + `gws-sheets` skills | 10 min | New agent capabilities |
| Build thin MCP wrapper for gws commands | 2-4 hours | Local MCP tool server |
| Evaluate `gws gmail +watch` vs n8n Gmail trigger | 1 hour | Real-time email processing |
| Test `gws events +subscribe` for Drive changes | 1 hour | Event-driven automation |

### Phase 3: Later (Higher Risk, Higher Value)

| Action | Effort | Value |
|--------|--------|-------|
| Replace clasp with gws script workflow | 2 hours | Unified credential management |
| Integrate Model Armor for agent safety | 4 hours | Prompt injection defense |
| Build custom recipe skills for Odoo workflows | 1-2 days | Gmail-to-Odoo agent automation |
| Evaluate gws as n8n replacement for Google triggers | 1 day | Architecture simplification |

### Do NOT Adopt

| Action | Reason |
|--------|--------|
| Replace Gmail add-on with gws | Different execution surface (sidebar vs CLI) |
| Replace Claude.ai Gmail/Calendar MCP | Redundant, existing integration works |
| Depend on gws for production pipelines | Pre-1.0, breaking changes expected |
| Install all 95 skills | Noise; install only what we need |
| Use Gemini CLI extension | We use Claude, not Gemini |

---

## 15. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Pre-1.0 breaking changes | Medium | Pin to specific version, test before upgrading |
| Community project (no SLA) | Medium | Maintain fallback to clasp and direct API calls |
| Broad OAuth scopes | High | Always use `-s` flag for minimal scopes |
| Credential file exposure | Medium | Use OS keyring (default in 0.22.3+) |
| Overlap with existing MCP | Low | Install only non-overlapping skills |
| Agent skill format may change | Low | Skills are markdown files; easy to update |
| Discovery Document caching | Low | 24h cache; force refresh if needed |

---

## 16. Sources

| Source | URL | Accessed |
|--------|-----|----------|
| Repository | https://github.com/googleworkspace/cli | 2026-03-27 |
| README.md | https://raw.githubusercontent.com/googleworkspace/cli/main/README.md | 2026-03-27 |
| AGENTS.md | https://raw.githubusercontent.com/googleworkspace/cli/main/AGENTS.md | 2026-03-27 |
| CHANGELOG.md | https://raw.githubusercontent.com/googleworkspace/cli/main/CHANGELOG.md | 2026-03-27 |
| Cargo.toml (workspace) | https://raw.githubusercontent.com/googleworkspace/cli/main/Cargo.toml | 2026-03-27 |
| google-workspace crate | https://raw.githubusercontent.com/googleworkspace/cli/main/crates/google-workspace/Cargo.toml | 2026-03-27 |
| Skills index | https://github.com/googleworkspace/cli/tree/main/skills | 2026-03-27 |
| gws-gmail SKILL.md | https://raw.githubusercontent.com/googleworkspace/cli/main/skills/gws-gmail/SKILL.md | 2026-03-27 |
| gws-script SKILL.md | https://raw.githubusercontent.com/googleworkspace/cli/main/skills/gws-script/SKILL.md | 2026-03-27 |
| gws-shared SKILL.md | https://raw.githubusercontent.com/googleworkspace/cli/main/skills/gws-shared/SKILL.md | 2026-03-27 |
| package.json | https://raw.githubusercontent.com/googleworkspace/cli/main/package.json | 2026-03-27 |
| Skills docs | https://raw.githubusercontent.com/googleworkspace/cli/main/docs/skills.md | 2026-03-27 |

---

*This document is a point-in-time evaluation. gws is pre-1.0 and evolving rapidly. Re-evaluate at v1.0 release or quarterly, whichever comes first.*
