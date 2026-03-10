# Tasks — Vercel Enterprise+ (Outcome-First)

## T0 — Foundations

- [ ] Define evidence bundle v1 schema (JSON) + hashing rules
- [ ] Implement `platformctl` CLI skeleton (deploy/rollback/evidence/policy/audit/slo)
- [ ] Add CI: lint + unit tests + schema validation

## T1 — Deploy Pipeline

- [ ] Deterministic build runner + artifact store (content-addressed)
- [ ] Preview environment provisioning via API
- [ ] Deployment promotion model (preview -> staging -> prod)

## T2 — Access Governance

- [ ] RBAC model + enforcement middleware
- [ ] SSO (SAML/OIDC) integration
- [ ] SCIM provisioning connector (users/groups)

## T3 — Audit & Evidence

- [ ] Append-only audit log (JSONL) with signing
- [ ] Evidence export command produces signed bundle per deployment
- [ ] Verification tool: `platformctl evidence verify`

## T4 — Observability

- [ ] OTel tracing integration (build + runtime)
- [ ] Runtime logs export + retention policy
- [ ] Metrics pipeline + per-deploy comparison

## T5 — Secure Compute

- [ ] Dedicated egress IP pool abstraction
- [ ] Private connectivity reference pattern (VPC/VPN/peering hooks)
- [ ] Secret retrieval via short-lived tokens + audit

## T6 — Security Perimeter

- [ ] WAF policy-as-code (baseline rules)
- [ ] DDoS/rate-limit controls
- [ ] Bot protection integration hook

## T7 — Release Safety

- [ ] Rolling release controller (percent-based)
- [ ] Canary + auto-halt on regression
- [ ] Instant rollback path w/ verification

## T8 — SLA/SLO & Support

- [ ] SLO definitions + burn rate calculations
- [ ] Probe runner + scheduled probe runs
- [ ] Support runbooks + escalation automation artifacts (API driven)

## T9 — Tier-1 Roadmap

- [ ] Conformance gates (static analysis, dependency scanning, SBOM)
- [ ] AI suggestions engine (advisory only) for policy + incidents
- [ ] Marketplace governance + integration allowlisting
- [ ] Data residency & regional constraints
