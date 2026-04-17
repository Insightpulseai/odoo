---
name: pulser-eval
description: Run cross-model evals on the Pulser for Odoo platform. Requires explicit resource_config documentation to ensure comparable results.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(python3 scripts/run_eval.py)
inputs:
  - dataset: String - path to the eval dataset.
  - resource_config: String (e.g., 'high-headroom-v1') - The ACA resource footprint for this eval.
  - odoo_version: String (e.g., '18.0')
---

# pulser-eval

This skill executes high-fidelity evaluations against Odoo 18 CE environments.

## Eval Infrastructure Rule (Anthropic Engineering Blog)
Eval scores are not comparable across different infrastructure configurations.
A 3x ceiling over per-task baseline specs is required to eliminate OOM-skew.

Registration of \`resource_config\` is mandatory.

## Usage
- Trigger: "run evals on the AP flow"
- Required metadata: \`resource_config\`
