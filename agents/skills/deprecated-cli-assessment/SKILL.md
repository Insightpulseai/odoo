# Deprecated CLI Assessment Skill

## Purpose

Assess whether a deprecated CLI tool should be used or rejected. Maintains the deprecation registry, enforces migration paths to canonical alternatives, and evaluates exception criteria.

## Owner

deprecated-tool-reviewer

## Type

Judge — this skill evaluates tool usage requests, it does not execute deprecated tools.

## Deprecation Registry

| Tool | Vendor | Status | Deprecated Since | Canonical Alternative |
|------|--------|--------|-----------------|----------------------|
| odo | Red Hat | Officially deprecated (GitHub archived) | 2024 | Databricks CLI, Azure CLI, Odoo CLI |

## Assessment Flow

1. Identify the deprecated tool being requested
2. Check if it exists in the deprecation registry
3. If registered: DEFAULT = REJECT
4. If exception requested: evaluate against the 5 exception criteria
5. Return structured assessment

## Exception Criteria (ALL must be met)

1. No canonical alternative exists for the specific operation
2. The deprecated tool is the only path to achieve a required business outcome
3. The exception is time-boxed with a migration deadline
4. The exception is documented in `docs/contracts/DEPRECATED_TOOL_EXCEPTIONS.md`
5. A migration plan to the canonical alternative is filed

## Output Format

```json
{
  "tool": "<tool-name>",
  "verdict": "REJECT | EXCEPTION_GRANTED",
  "reasoning": "<why>",
  "canonical_alternative": "<what to use instead>",
  "exception_details": {
    "deadline": "<ISO date if exception>",
    "migration_plan": "<path to plan>",
    "criteria_met": [true, true, true, true, true]
  }
}
```

## odo-Specific Assessment

odo (Red Hat OpenShift Developer CLI) is officially deprecated:
- GitHub repository is archived
- Red Hat recommends alternatives (Podman, kubectl, oc)
- No IPAI use case requires odo
- Verdict: PERMANENT REJECT — no exception pathway exists
- Benchmark reference only: allowed for historical comparison documentation

## Verification

- Assessment produces structured output
- Rejected tools are not present in any CI pipeline or skill dependency
- Exception grants are documented in contracts directory
