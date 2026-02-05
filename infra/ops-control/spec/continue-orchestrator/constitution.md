# spec/continue-orchestrator/constitution.md

## Product name
Continue Orchestrator (an improved, enterprise-grade + reproducible layer on top of Continue)

## Context
Continue today spans:
- Mission Control for Agents/Tasks/Workflows + integrations
- CLI with TUI + headless modes for CI/CD automation
- Config-driven agents (config.yaml) composed from models/rules/tools (MCP servers)
- Built-in secrets management + resolution semantics
- Metrics to track runs, PR outcomes, interventions
- Org governance roles (admin/member)

Continue Orchestrator adds: **policy-as-code, deterministic/replayable runs, stronger execution sandboxing, and end-to-end auditability** without breaking the existing UX.

## Principles (non-negotiables)
1. **Reproducibility first**  
   Every agent run is replayable: same inputs ⇒ same tool calls (or explainably different) with immutable artifacts.
2. **Policy gates everything**  
   Repo/org policies decide what an agent may read/write, which tools it may call, when human approval is required.
3. **Least surprise UX**  
   Existing Continue surfaces (IDE/CLI/Mission Control) remain familiar; Orchestrator appears as "Run Controls + Ledger".
4. **Separation of concerns**  
   - Config describes *intent* (models/rules/tools).  
   - Policy describes *permission + guardrails*.  
   - Runtime records *what happened* (ledger).
5. **First-class automation**  
   Headless mode remains the canonical automation surface for CI/CD & cron/webhooks.
6. **Secret-safe by default**  
   Secrets remain in Mission Control + local env sources; configs reference via mustache notation.

## Non-goals
- Replacing Continue's IDE extensions or CLI UI.
- Building a new SCM (GitHub remains primary for PR-based workflows).
- Becoming a generic workflow engine (we focus on AI dev workflows only).

## Security & governance constraints
- Mandatory role separation:
  - Admins can manage org configs/secrets/policies; members can run agents within policy.
- Mandatory "write fences":
  - Any PR creation, branch pushes, secret reads, or external tool execution requires explicit policy allowance.
- Immutable audit logs:
  - Run Ledger is append-only; deletions are tombstoned, not removed.

## Operational constraints
- Must support the existing integrations model (GitHub/Slack/Sentry/Snyk/etc.).
- Must work with existing Continue Workflows (cron/webhook triggers).
- Must surface reliability + intervention rates (extends Metrics).

## Definition of done
- A run can be reproduced end-to-end (inputs/config/policy/tool I/O captured).
- Policies can deny/allow specific tool calls, file paths, repos, and PR actions.
- Every PR created by an agent includes evidence: tests run, diffs, reasoning summary, provenance hash.
- Rollout does not break existing config.yaml usage or Mission Control workflows.
