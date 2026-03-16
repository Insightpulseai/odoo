# Plan — Vercel Enterprise+ (Outcome-First)

## Phase 0 — Repository + Interfaces (Week 0–1)

- Create CLI skeleton + API contracts
- Define policy engine interface (OPA/CEL)
- Define evidence bundle format + signing

Deliverables:

- `platformctl` CLI scaffolding
- Evidence schema: `schemas/evidence.bundle.v1.json`

## Phase 1 — Tier-0 Core (Week 1–4)

1. Deploy pipeline (deterministic builds + previews)
2. RBAC/SSO/SCIM baseline
3. Audit log pipeline (append-only)
4. Observability (OTel exporters + runtime logs)
5. Rolling releases + rollback
6. Secure compute primitives (dedicated egress pools + allowlists)
7. WAF baseline rules + DDoS controls
8. SLA/SLO probes + dashboards (API/CLI only)
9. Evidence export + signing

Exit criteria:

- All Tier-0 outcomes pass probes and produce evidence bundles.

## Phase 2 — Tier-1 Enhancements (Week 5–8)

- Conformance pipelines (quality/security gates)
- AI-assisted ops suggestions (non-authoritative)
- Marketplace governance + SBOM verification
- Data residency controls

Exit criteria:

- Tier-1 outcomes measured and reportable.

## Phase 3 — Enterprise Operability (Week 9–12)

- Incident workflow automation
- Support tooling & escalation automation
- Cost controls and budget enforcement
- Compliance report generator (SOC2-ready artifact assembly)

Exit criteria:

- Enterprise readiness review + runbook completeness.
