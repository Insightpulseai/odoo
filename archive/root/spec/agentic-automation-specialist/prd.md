# PRD: Agentic Automation Specialist

## 1. Problem Statement

AI agents currently lack a standardized way to execute complex side-effects (e.g., cross-system data sync, external API calls) that require multi-step logic and error handling. Traditional scripting is often opaque and non-resumable.

## 2. Goals

- Standardize n8n workflow exports as repo-backed artifacts.
- Enable agents to trigger automations as tools.
- Ensure 100% auditability via the `ops.*` control plane.
- Promote idempotency as a first-class citizen.

## 3. Target Systems

- **n8n**: Execution substrate.
- **Supabase**: State management & triggering (Queues/Realtime).
- **Odoo**: Business logic & data source/sink.
- **Slack/Mattermost**: Visibility and alerts.

## 4. Technical Requirements

| Req                | Description                                                    |
| ------------------ | -------------------------------------------------------------- |
| **Tool Schema**    | Every workflow must define a JSON-schema for inputs/outputs.   |
| **State Emission** | Mandatory `HTTP` or `RPC` calls to `ops.runs` at start/finish. |
| **Dedupe Keys**    | Native support for idempotency tokens.                         |
| **Modular Logic**  | Workflows should be granular (one tool, one job).              |

## 5. User Stories

- **As an AI Agent**, I want to trigger a 'stage clone' workflow and get a machine-readable run ID so I can monitor progress.
- **As a Developer**, I want to review workflow changes in Git to ensure no regressions are introduced to the control plane.
- **As an Ops Manager**, I want to see the full lineage of every automated action in the `ops.runs` dashboard.
