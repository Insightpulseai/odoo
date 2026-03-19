# Copilot Capability Eval Contract

> Defines the maturity rubric, scoring methodology, and promotion gates
> for the Odoo Copilot and Foundry integration capabilities.
>
> SSOT for: `agents/evals/odoo_copilot_target_capabilities.yaml`
> and `agents/evals/foundry_target_capabilities.yaml`

---

## 1. Maturity Rubric (0-4)

| Level | Label | Definition |
|-------|-------|------------|
| 0 | Missing | No code, no design artifact, no stub. Capability does not exist. |
| 1 | Scaffolded | Model/file/contract exists but contains only stubs, empty methods, or placeholder logic. Cannot be invoked end-to-end. |
| 2 | Partial | Core logic implemented. Can be invoked in isolation (unit test or manual call) but has not been validated against a live backend or lacks key integration points. |
| 3 | Operational | Fully implemented and locally testable. All code paths exist, error handling is present, and the capability works when its dependencies are available. Not yet proven in production. |
| 4 | Target | Production-proven. Capability has been validated live, has monitoring/alerting, and meets all acceptance criteria documented in the capability YAML. |

---

## 2. Evidence Requirements by Level

| Level | Required Evidence |
|-------|-------------------|
| 0 | None (absence is the evidence). |
| 1 | File path exists. Stub code or contract YAML present. No functional logic. |
| 2 | File path + functional code. At least one code path exercises the capability. Missing: live validation, full error handling, or integration wiring. |
| 3 | File path + functional code + error handling + local test evidence (unit test, manual invocation log, or `--stop-after-init` proof). Fallback paths implemented. |
| 4 | All of level 3 + production invocation evidence (HTTP logs, audit records, or CI artifact proving live execution). Monitoring dashboard or alert rule exists. |

---

## 3. Domain Weights

Weights reflect relative importance to production readiness. Must sum to 1.0.

| Domain | Weight | Rationale |
|--------|--------|-----------|
| Foundry runtime integration | 0.15 | Core platform dependency |
| Auth and identity | 0.10 | Security gate |
| Tool execution | 0.15 | Primary user-facing capability |
| KB grounding | 0.20 | Differentiating feature; largest surface area |
| Guardrails and read-only enforcement | 0.10 | Safety-critical |
| Observability and tracing | 0.05 | Operational necessity but not blocking MVP |
| Deployment/publish repeatability | 0.10 | Ship confidence |
| Production readiness | 0.10 | Operational maturity |
| Governance / approval readiness | 0.05 | Stage 2 dependency, lower weight for Stage 1 |
| **Total** | **1.00** | |

---

## 4. Scoring Formula

### Per-capability score

```
capability_score = current / target
```

Where `target` is always 4 (the maximum maturity level).

### Per-domain score

```
domain_score = mean(capability_scores in domain)
```

### Overall weighted score

```
overall_score = sum(domain_score_i * weight_i) for all domains
```

Result is a float in [0.0, 1.0].

### Maturity band classification

| Range | Band |
|-------|------|
| 0.00 - 0.24 | missing |
| 0.25 - 0.49 | scaffolded |
| 0.50 - 0.74 | partial |
| 0.75 - 0.89 | operational |
| 0.90 - 1.00 | target |

---

## 5. Blocking-Gap Rules

A capability is a **release blocker** if ALL of the following are true:

1. Its `release_blocker` field is `true` in the capability YAML.
2. Its `current` score is < 3 (below operational).

A domain is **blocked** if it contains at least one blocked capability.

The system is **release-blocked** if any domain is blocked.

Blockers are listed separately from the weighted score. A high weighted
score does NOT override blockers -- both must pass for release.

---

## 6. Promotion Gates

### 0 to 1 (Missing to Scaffolded)
- Create the file/model/contract.
- Register it in the appropriate manifest or registry.
- No functional code required.

### 1 to 2 (Scaffolded to Partial)
- Implement core logic (happy path).
- At least one code path is exercisable.
- May lack error handling, fallbacks, or integration wiring.

### 2 to 3 (Partial to Operational)
- All code paths implemented (happy + error + edge).
- Error handling and fallbacks present.
- Locally testable: unit test, `--stop-after-init`, or manual invocation with evidence.
- Dependencies are identified and gracefully handled when unavailable.

### 3 to 4 (Operational to Target)
- Production invocation evidence (audit log, HTTP log, CI artifact).
- Monitoring or alerting exists for the capability.
- All acceptance criteria from the capability YAML are met.
- At least one sprint of production operation without regression.

---

## 7. Eval Execution

```bash
# Score all capabilities and produce JSON + markdown reports
python agents/evals/score_capabilities.py

# Output:
#   artifacts/evals/odoo_copilot_capability_eval.json
#   artifacts/evals/odoo_copilot_capability_eval.md
```

The scorer reads:
- `agents/evals/odoo_copilot_target_capabilities.yaml`
- `agents/evals/foundry_target_capabilities.yaml`

And applies the weights and rules defined in this contract.

---

## 8. Review Cadence

- **Weekly**: Re-score after any capability-affecting merge.
- **Sprint boundary**: Full review of blocker list and promotion candidates.
- **Pre-release**: All blockers must be resolved. Overall score is informational.

---

*Last updated: 2026-03-15*
