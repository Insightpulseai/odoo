# Agent Pattern Selection — Examples

## Example 1: Code Review Comment

**Task**: Generate a code review comment for a PR diff.

**Assessment**:
1. Single call? Yes — one LLM call with the diff as context can produce a quality review.
2. No need to proceed further.

**Result**: Single call. No workflow needed.

---

## Example 2: Multi-Module Odoo Upgrade

**Task**: Upgrade 10 Odoo modules from 18.0 to 19.0.

**Assessment**:
1. Single call? No — too many independent modules with different migration needs.
2. Sequential? No — modules are largely independent (no cross-module dependency chain).
3. Parallel? Yes — each module can be upgraded independently, results aggregated.

**Result**: Parallel workflow. Aggregation: collect migration reports, identify cross-module conflicts post-merge.

---

## Example 3: Tax Compliance Report Generation

**Task**: Generate a BIR tax compliance report with calculated fields, validation, and formatting.

**Assessment**:
1. Single call? No — multiple data sources, calculation steps, validation.
2. Sequential? Yes — extract data → calculate → validate → format → output.

**Result**: Sequential workflow.

---

## Example 4: Customer Support Triage Agent

**Task**: Handle incoming customer support requests that vary widely in type and complexity.

**Assessment**:
1. Single call? No — request types vary too much.
2. Sequential? No — no fixed step chain.
3. Parallel? No — single request, not independent subtasks.
4. Evaluator-optimizer? No — no iteration criteria.
5. Autonomous agent? Yes — must classify, route, gather info, and adapt based on customer responses.

**Result**: Autonomous agent with routing + tool access + human escalation checkpoint.
