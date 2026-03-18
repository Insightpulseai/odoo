# PRD — Cursor Sovereign (Improved Cursor)

## Problem
AI coding tools provide strong UX, but enterprise constraints (data sovereignty, auditability, policy controls, deterministic CI gates, and airgapped deployments) are often second-class.

## Goals
- Cursor-grade agentic coding UX with:
  - Direct-route to enterprise LLMs
  - Self-hostable context/prompt builder
  - Deterministic "Context Snapshot" artifacts
  - Policy-governed agent actions
  - Odoo.sh-grade parity gating integrated into the workflow

## Non-Goals
- Training proprietary models
- Replacing existing CI/CD; we integrate with it
- Building a new editor from scratch (initially)

## Personas
1. **Founder/Architect**: wants speed + governance, minimal manual steps.
2. **Platform Engineer**: needs deterministic gates, audit logs, rollback.
3. **Security Lead**: requires data-classification, retention controls, provenance.
4. **Developer**: wants fast edits, reliable refactors, and fewer broken builds.

## Primary Use Cases
- "Agent refactor PR": agent edits code, updates docs, runs tests, creates PR with gate proofs.
- "Enterprise LLM routing": route prompts to org-managed LLM endpoints with policy constraints.
- "Airgapped mode": no outbound except approved internal endpoints; still usable.
- "Policy enforcement": block disallowed modules/deps, enforce manifests, enforce docs drift and seed drift.

## Functional Requirements

### FR1 — Context Snapshots
- Generate a repo snapshot manifest:
  - Merkle tree hashes + ignore rules
  - Minimal changed-file upload set
  - Optional encryption-at-rest
- Emit: `context.json` + `context.sig` + `ignore_report.json`

### FR2 — Self-hostable Prompt/Context Builder
- Service that:
  - Builds prompts locally or in customer infra
  - Resolves context from snapshots + index
  - Logs redacted traces
- Deployment targets:
  - Docker Compose
  - Kubernetes (later)

### FR3 — Direct-route to Enterprise LLMs
- Support connectors:
  - OpenAI enterprise
  - Azure OpenAI
  - Anthropic enterprise
  - "Generic OpenAI-compatible"
- Enforce:
  - per-project endpoint allowlist
  - model allowlist
  - max tokens / max context
  - data classification gates

### FR4 — Agent Orchestration
- Agent can:
  - edit files
  - run commands
  - propose diffs
  - open PR (optional)
- Must produce run manifest:
  - inputs, tool calls (redacted), outputs, artifacts, final diff

### FR5 — Odoo.sh-grade Parity Gating
Gate categories:
- **Policy gates**: forbidden modules, forbidden links, forbidden paths
- **Integrity gates**: docs drift, seed drift, schema drift
- **Security gates**: secrets scan, dependency scan, SAST
- **Quality gates**: unit/integration tests, lint, build
- **Deploy gates**: smoke tests, health checks, migration safety

### FR6 — Docs as Product
- mkdocs (or equivalent) with Primer-styled tokens
- Docs pages:
  - Architecture
  - Security + threat model
  - Data flow + retention
  - Gating overview + gate catalog
  - Deployment runbooks
  - ADRs

## Non-Functional Requirements
- Deterministic outputs: same inputs -> same snapshot + gate results
- Latency: fast "preflight gate" under 2 minutes for typical PRs (configurable)
- Auditability: immutable run events; retention controls
- Extensibility: plugin API for gates and tool connectors

## Data & Security
- Data classification: public / internal / confidential / restricted
- Outbound control: deny by default; explicit allowlists
- Retention: configurable per tenant/project; delete workflows supported
- Attestations: signed run + gate proofs

## Success Metrics
- % agent PRs merged with zero manual fixups
- Gate failure rate by category (downtrend)
- Mean time to safe refactor (downtrend)
- Security exceptions count (downtrend)

## Risks
- UX vs governance tension
- Indexing scale on monorepos
- Enterprise endpoint heterogeneity
