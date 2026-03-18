# Kapa-Plus Constitution

## Purpose
Ship a production-grade "docs → answers → actions" assistant platform that is:
- accurate (grounded citations by default),
- observable (every answer/action traceable),
- controllable (policy + RBAC + sandboxed actions),
- portable (embed anywhere; MCP-native).

## Principles
1. **Citations-first UX**: every factual answer must cite sources; "no-cite" is an explicit opt-out.
2. **Deterministic ingestion**: content hashing + versioned indexes; reproducible rebuilds.
3. **Separation of concerns**: ingestion, retrieval, ranking, generation, actions are pluggable.
4. **Tenant isolation**: strict org/project boundaries at storage + retrieval + action layers.
5. **Policy gates**: allowlist tools; per-agent capabilities; least privilege tokens.
6. **Observability is a feature**: traces, evals, deflection, CSAT, and "doc gaps" are first-class.
7. **Multi-surface by default**: docs widget, in-app, Slack/Discord, Zendesk/Intercom, API, MCP.
8. **Low-friction deployment**: single "connect sources → deploy widget" happy path under 30 minutes.
9. **Human-in-the-loop loops**: feedback → correction → re-rank → re-ingest → regression eval.
10. **Open integrations**: OpenAPI + MCP tools + webhooks; avoid lock-in.

## Non-negotiables
- Source attribution stored per chunk + per answer.
- Audit log for all actions, prompts, tool calls, and content versions.
- "Safety by configuration": org admins can disable web, tools, actions, or entire agents.
