---
name: pulser-self-heal
description: Authority-integrated skill for pulser-self-heal. Uses model-versioned fallback policies to avoid "dead weight" mitigations on advanced models (Sonnet 4.6+). Maps failures to the IPAI taxonomy.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(python3 scripts/self_heal.py)
---

# pulser-self-heal

This skill implements the IPAI "Managed Agent" self-healing loop, detecting and mitigating failures in the and ERP runtime.

## Model-Versioned Policies (Anthropic Engineering Blog)
Fallback behaviors are versioned by model to eliminate unnecessary resets or "context anxiety" mitigations that may be obsolete on newer models.
- **Sonnet 4.6**: Advanced reasoning — bypasses legacy "reset and retry" for tool-call ambiguity.
- **Opus 4.5**: Legacy — uses full harness reset on timeout.

Policies are selected dynamically based on \`model_version\` metadata.

## Failure Taxonomy
- \`F-POL\`: Policy violation (Gated)
- \`F-TOOL\`: Tool-call logic failure
- \`F-VAL\`: Input validation failure
- \`F-INF\`: Infrastructure/Network failure

## Usage
- "self-heal after Odoo AccessError"
- "mitigate F-INF in the AP sync flow"
