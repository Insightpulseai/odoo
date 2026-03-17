# Constitution — Vercel Enterprise+ (Outcome-First Platform)

## 1) Purpose

Provide a secure, observable, policy-driven web delivery platform that enables enterprises to ship changes safely and quickly, with deterministic evidence and governance.

## 2) Non-negotiables (Tier-0)

1. **SLO/SLA-first**: explicit SLOs; uptime SLA with measurable enforcement (error budgets, SLO burn alerts).
2. **Secure compute by default**: dedicated egress/ingress options, private connectivity patterns, and isolation controls.
3. **Security meets speed**: WAF + DDoS controls, audit logging, and incident readiness are baseline.
4. **Access governance**: RBAC + SSO + SCIM; least privilege enforced at runtime and deploy time.
5. **Observability by default**: traces/logs/metrics per deploy and runtime; immutable audit trails.
6. **Safe releases**: staged/rolling releases, canaries, and instant rollback with evidence.
7. **24/7 support model**: enterprise support + on-call escalation path with runbooks.
8. **IaC as source of truth**: everything configurable via code/CLI/API (no UI-only state).

## 3) Product boundary (What this is / is not)

- **IS**: a platform product (delivery plane + governance + evidence) spanning build, deploy, edge/runtime, security, and observability.
- **IS NOT**: a web framework, app template library, or a replacement for enterprise IAM providers.

## 4) Principles

- **Outcome parity > feature parity**: capabilities measured by probes and evidence, not module equivalence.
- **Determinism**: identical inputs produce identical deploy artifacts.
- **Evidence-first compliance**: every control produces artifacts (JSON, signed logs, reports).
- **Progressive hardening**: security and compliance improve without blocking shipping.

## 5) Risk posture

- Default: “secure-by-default, configurable-to-stricter”.
- Any control that blocks deploy requires an explicit policy exemption with expiry.

## 6) Compatibility requirements

- Git providers: GitHub/GitLab/Bitbucket via webhook + OIDC.
- App runtimes: Node/Edge containers; static + SSR + API routes.
- Observability: OpenTelemetry export.
- Policy: OPA/Rego and/or CEL-like policy rules.

## 7) Success metrics

- Lead time to production ↓
- Change failure rate ↓
- MTTR ↓
- Evidence completeness ↑
- Supply chain risk ↓
