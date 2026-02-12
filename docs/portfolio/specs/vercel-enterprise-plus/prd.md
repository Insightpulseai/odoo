# PRD — Vercel Enterprise+ (Outcome-First, Evidence-Driven)

## 0) Summary

Build an enterprise delivery platform that matches and extends the core enterprise outcomes visible in leading platforms—secure compute, rolling releases, WAF/DDoS, RBAC+SSO, observability, and uptime/support commitments—while adding deterministic policy-as-code and compliance evidence export as first-class outputs.

## 1) Goals (Goal-Based Parity)

### Tier-0 (Platform/Service Outcomes) — MUST ship first

1. **SLA & SLO enforcement**
2. **Secure compute & network isolation**
3. **WAF/DDoS baseline**
4. **RBAC + SSO (+ SCIM)**
5. **Auditability & immutable logs**
6. **Observability by default**
7. **Safe releases (rolling/canary/rollback)**
8. **24/7 enterprise support workflow**
9. **Evidence export (machine-readable)**

### Tier-1 (Advanced Outcomes) — AFTER Tier-0

1. **AI-assisted operations** (policy suggestions, incident triage, cost optimization)
2. **Marketplace governance** (approved integrations, SBOM verification)
3. **Multi-region / residency controls**
4. **Conformance gates** (quality/security checks per deploy)

## 2) Non-goals

- Not building a new framework (e.g., Next.js competitor).
- Not replacing IAM, SIEM, or full APM suites—integrate instead.

## 3) Personas

1. **Platform Engineer**: needs guardrails, standardization, and audit evidence.
2. **Security Engineer**: wants enforcement, visibility, and provable controls.
3. **App Team**: wants speed, previews, safe releases, instant rollback.
4. **Compliance/Procurement**: wants exportable evidence, SLA, and support posture.

## 4) Problem statement

Enterprises want the speed of modern frontend delivery with the governance, evidence, and safety controls typically bolted together from many tools. They need an integrated platform where outcomes are provable.

## 5) Product requirements

### 5.1 Delivery & Collaboration

- Git-integrated preview environments for every change.
- Deterministic build pipeline with cached artifacts.
- “Conformance” lane: quality/security checks before promote.

### 5.2 Performance & Runtime

- Global edge delivery with regional routing policies.
- Compute modes: edge functions + regional serverless + optional dedicated runtime.
- Instant revert/rollback controls.

### 5.3 Secure Compute (Tier-0)

- Dedicated egress IP pools and private connectivity patterns.
- Policy enforcement: block public egress for protected services by default (configurable).
- Secret access via short-lived tokens, auditable retrieval.

### 5.4 Security (Tier-0)

- WAF rulesets with policy-as-code.
- DDoS controls and rate limiting.
- Bot management hooks (pluggable).

### 5.5 Identity & Access (Tier-0)

- RBAC model for org/project/env.
- SSO (SAML/OIDC) and SCIM provisioning.
- Fine-grained “production protections”.

### 5.6 Observability (Tier-0)

- Traces/logs/metrics per deploy & runtime; OpenTelemetry export.
- Audit logs for deploys, config changes, access events.

### 5.7 Release Safety (Tier-0)

- Rolling releases (percentage-based rollout, automated halt on regression).
- Canary + feature flag integration (bring-your-own flags supported).

### 5.8 SLA & Support (Tier-0)

- SLA/SLO documents; automated SLO probes and error budget.
- 24/7 support: paging, escalation, incident comms templates.

### 5.9 Evidence Export (Tier-0)

- Export signed evidence bundles:
  - `evidence/deploys/*.json`
  - `evidence/policies/*.rego|.cel`
  - `evidence/audit/*.jsonl` (append-only)
  - `evidence/slo/*.json`
- Evidence bundles are reproducible per release and can be attached to compliance tickets.

## 6) API/CLI Requirements (No UI dependency)

- `platformctl deploy --env prod`
- `platformctl rollback --deployment <id>`
- `platformctl evidence export --deployment <id> --out evidence/`
- `platformctl policy test|apply`
- `platformctl audit tail|export`
- `platformctl slo status|burn`

## 7) Data model (minimal)

- Org, Project, Environment
- Deployment (immutable), Artifact (immutable)
- Policy (versioned), PolicyDecision (append-only)
- AuditEvent (append-only)
- SLO, ProbeRun, Incident

## 8) Acceptance criteria (Tier-0)

- A deployment produces:
  - build artifact checksum
  - policy decisions
  - audit trail
  - runtime metrics snapshot
  - rollback plan + verified rollback command
- Evidence export validates deterministically (hashes match).
- RBAC prevents unauthorized promote-to-prod.
- Canary rollout can auto-halt on SLO regression.

## 9) Open questions (tracked, not blocking)

- Multi-region data residency enforcement (Tier-1).
- Managed vs BYO WAF rulesets (Tier-1).
