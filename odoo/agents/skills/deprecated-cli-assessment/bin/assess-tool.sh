#!/usr/bin/env bash
# deprecated-cli-assessment: Assess whether a CLI tool is deprecated
# Usage: assess-tool.sh <tool-name>
set -euo pipefail

TOOL="${1:?Usage: assess-tool.sh <tool-name>}"

# Deprecation registry (hardcoded — source of truth in SKILL.md)
case "${TOOL}" in
  odo)
    cat <<'JSON'
{
  "tool": "odo",
  "verdict": "REJECT",
  "reasoning": "odo is officially deprecated by Red Hat. GitHub repository is archived. No IPAI use case requires odo.",
  "canonical_alternative": "Use Databricks CLI for data/ML operations, Azure CLI for infrastructure, Odoo CLI for ERP operations.",
  "exception_details": null
}
JSON
    exit 1
    ;;
  *)
    cat <<JSON
{
  "tool": "${TOOL}",
  "verdict": "NOT_IN_REGISTRY",
  "reasoning": "Tool '${TOOL}' is not in the deprecation registry. Check if it is a canonical tool.",
  "canonical_alternative": null,
  "exception_details": null
}
JSON
    exit 0
    ;;
esac
