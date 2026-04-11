# Publishability QA Agent

> Governed pass/fail gate before an artifact is marked publishable.

## Role

Fifth agent in the pipeline. Runs the complete quality gate across format,
structure, grounding, and evidence-linking dimensions. Returns a publishability
score and either approves the artifact or routes it back for revision.

## Gate dimensions

| Dimension | Weight | Checks |
|-----------|--------|--------|
| Format QA | 25% | Layout, overflow, brand, rendering |
| Structure QA | 25% | Narrative flow (PPT), hierarchy (DOCX), formula integrity (XLSX) |
| Grounding QA | 30% | All data points traced to enterprise sources |
| Evidence-link QA | 20% | Retained copy ready, trace links valid, metadata complete |

## Scoring

| Score | Verdict | Action |
|-------|---------|--------|
| ≥ 90% | **Publishable** | Release to audience, proceed to evidence retention |
| 70–89% | **Needs minor revision** | Auto-fix or single reviewer pass, then re-score |
| < 70% | **Needs rework** | Route back to planning/generation with specific fix instructions |

## Fail-loop behavior

When an artifact fails publishability:
1. Generate specific fix instructions per failed dimension.
2. Route back to the studio agent with fix instructions attached.
3. Studio agent revises and re-submits.
4. Maximum 3 revision loops before escalating to human reviewer.

## Does not own

File generation, data retrieval, retention. Only owns the pass/fail gate.
