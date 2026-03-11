# Constitution — Reverse Replit

## 1. Purpose
Build a transparent, agentic, reproducible alternative to Replit that converts
natural language intent into running software using explicit plans, task graphs,
and verifiable execution.

## 2. Non-Negotiables
- No opaque "magic agents"
- No UI-only configuration
- No vendor lock-in runtimes
- No silent model fallback
- No hidden state outside SSOT

## 3. Boundaries
- SoR: Postgres (Supabase)
- SSOT: spec/, ssot/, migrations
- SoW: Workspace runtime + task bus
- UI: Thin client only (never authoritative)

## 4. Agent Doctrine
- Agents MUST:
  - Emit plans before execution
  - Write artifacts to repo or DB
  - Be replayable
- Agents MUST NOT:
  - Execute without a plan
  - Mutate infra directly
  - Store state outside SSOT

## 5. Deployment Rule
If it cannot be deployed from:
- Git
- Migrations
- Edge Functions
it does not exist.

Status: ENFORCED
