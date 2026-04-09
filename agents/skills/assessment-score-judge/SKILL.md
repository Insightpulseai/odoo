# Assessment Score Judge

## Purpose

Score assessment answers and evidence using the internal harness rubric.

This skill evaluates the quality and maturity of each answer using:
- WAF core scoring
- workload overlay scoring
- transformation-readiness scoring
- confidence and downgrade rules

It is a scoring skill, not a drafting skill.

## When to use

Use this skill when:
- a draft answer pack exists
- evidence has already been gathered
- a domain, pillar, or phase needs scoring
- you need a structured score plus downgrade rationale

## Inputs

Required:
- answer pack from `assessment-answer-drafter`
- evidence pack from `assessment-evidence-harvester`
- scoring rubric from `ssot/assessment/scoring_rubric.yaml`

Optional:
- target overlay
- target persona
- prior score for comparison

## Output contract

For each item, return:

- `domain`
- `raw_score`
- `confidence`
- `evidence_quality`
- `downgrade_reasons`
- `blockers`
- `recommendations`
- `follow_up_work`

## Core scoring model

### Score scale

- `0` absent
- `1` ad hoc
- `2` present only
- `3` present and partly governed
- `4` governed and mostly proven
- `5` governed, proven, repeatable

### Confidence scale

- `low`
- `medium`
- `high`

### Evidence quality

- `weak`
- `mixed`
- `strong`

## Judging rules

### 1. Score the evidence, not the intent

Do not score based on architecture aspirations.

### 2. Apply downgrade rules aggressively

Common downgrades:
- no owner
- no test evidence
- unmanaged runtime dependency
- policy/control exists but is undocumented
- claim depends on portal-created drift

### 3. Separate posture from confidence

A domain may have a moderate score but low confidence if the evidence is incomplete or drift-heavy.

### 4. Flag blockers separately from recommendations

A blocker prevents a materially stronger answer.
A recommendation improves maturity but is not necessarily blocking.

## Scoring procedure

### Step 1 -- Score core maturity

Assess whether the answer is:
- absent
- ad hoc
- present
- partly governed
- mostly proven
- repeatable

### Step 2 -- Score evidence quality

Judge how strong the supporting evidence is.

### Step 3 -- Score confidence

Judge how safe it is to rely on the score.

### Step 4 -- Emit downgrade reasons

Always state why the score was not higher.

### Step 5 -- Emit next actions

Return the shortest useful set of actions that would increase score or confidence.

## Overlay handling

### Workload overlays

Overlay scores should challenge:
- workload fit
- operating model completeness
- architecture pattern alignment
- workload-specific blind spots

### Transformation overlay

Transformation scoring should evaluate:
- visibility
- alignment
- governance
- execution readiness
- continuous improvement

## Important rule

A control that is only **present** should usually score at **2** unless there is clear evidence of governance and proof.

## Refusal / escalation conditions

Escalate instead of scoring strongly when:
- evidence pack is missing
- the answer contradicts the evidence
- the score appears inflated relative to the downgrade rules
