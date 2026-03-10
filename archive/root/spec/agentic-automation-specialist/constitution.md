# Constitution: Agentic Automation Specialist

## 1. Governance & Authority

- **Primary Objective**: Workflows must serve as **deterministic tools** for AI agents.
- **SSOT Alignment**: The repository is the System of Record (SSOT) for all workflow definitions. Manual UI edits are non-canonical.
- **Authority**: Automation belongs to the `platform` domain.

## 2. Safety & Security

- **No Hardcoded Secrets**: Secrets (API keys, tokens) must reside in environment variables or vault-backed credentials.
- **RLS Enforcement**: All database interactions (Supabase/Odoo) must respect Row-Level Security.
- **Least Privilege**: Workflows run with minimal scopes required for the task.

## 3. Agentic Design Principles

- **Toolhood**: Workflows must have explicit inputs, outputs, and structured error codes.
- **Idempotency**: Workflows must be safe to retry without side-effect duplication.
- **Observability**: Every run must be logged to `ops.runs` and `ops.run_events`.
- **Reasoning Support**: Error messages must be machine-parsable and descriptive enough for an agent to reason about failure recovery.

## 4. Execution Constraints

- **Supabase First**: Use Supabase primitives (Queues, Realtime, Cron) before introducing external SaaS dependencies.
- **No-UI Default**: Automation must be deployable and testable via CLI/CI.
- **Naming**: `ipai_<domain>__<capability>__v<major>`.
