---
name: pulser-ga-gate
description: Enforcement gate for General Availability (GA) readiness. Rejects any eval result where resource_config is absent or differs from the baseline.
disable-model-invocation: true
user-invocable: false
allowed-tools: Bash(python3 scripts/validate_ga_gate.py)
---

# pulser-ga-gate

This gate enforces the 41-criteria GA assessment, with a specific focus on evaluation reliability.

## Resource Matching Policy
IPAI requires that all GA-submitted evaluation results use a configuration matched to the baseline.
- If \`resource_config\` is missing: REJECT.
- If \`resource_config\` != baseline (e.g. 'high-headroom-v1'): REJECT.

Any eval comparison without matching resource configuration is invalid due to infrastructure noise skews.

## Checklist
- [ ] 41-criteria compliance.
- [ ] \`resource_config\` presence and match.
- [ ] Evidence package complete.
- [ ] Deterministic verification pass.
