# Assessment Calibration

## Purpose

Calibrate the internal assessment output against the likely posture of official Microsoft assessment behavior.

This skill does not claim to reproduce Microsoft's hidden scoring logic.
Its role is to:
- reduce internal optimism
- estimate answer safety
- separate safe vs risky answers
- prepare comparison against official portal output later

## When to use

Use this skill when:
- core scoring is complete
- overlay scoring is complete
- you want a final internal answer pack before the official portal
- you want to estimate where the internal harness may diverge from Microsoft's normalized benchmark

## Inputs

Required:
- scored answer pack
- evidence pack
- official/internal mapping from `microsoft_assessments_map.yaml`
- scoring rubric

Optional:
- prior official assessment export
- prior internal-to-official delta sheet

## Output contract

Return:

- `calibrated_summary`
- `core_score_estimate`
- `overlay_adjustments`
- `confidence_band`
- `safe_answers`
- `risky_answers`
- `unsupported_answers`
- `likely_portal_downgrades`
- `comparison_plan`

## Core rules

### 1. Official portal remains authoritative

Never state or imply that the internal result is equivalent to the official Microsoft result.

### 2. Calibrate downward when in doubt

If evidence is partial, unmanaged, or unproven, bias the calibration toward a lower-confidence or lower-maturity interpretation.

### 3. Prefer comparability over optimism

The goal is not to get the highest internal score.
The goal is to produce answers that will survive comparison with the official portal.

### 4. Separate three classes of answers

- **Safe** -- strong evidence, low risk of downgrade
- **Risky** -- likely acceptable internally, but Microsoft may score lower
- **Unsupported** -- should not be claimed strongly at all

## Calibration procedure

### Step 1 -- Review core score

Inspect the WAF core score for obvious optimism.

### Step 2 -- Review overlays

Check whether overlays reveal hidden weaknesses that should reduce confidence.

### Step 3 -- Produce answer-safety map

Classify each major answer as safe, risky, or unsupported.

### Step 4 -- Estimate likely official downgrade areas

Typical downgrade candidates:
- DR claims without restore-test proof
- security claims without governance proof
- cost claims without Cost Management practice
- operational claims with significant drift
- performance claims without benchmark evidence

### Step 5 -- Define comparison plan

Recommend how to compare internal vs official results once the real portal output exists.

## Comparison model

After the official Microsoft assessment is completed:

1. export official results
2. compare pillar scores
3. compare recommendation themes
4. identify:
   - internal overestimation
   - internal underestimation
   - blind spots unique to the portal
   - blind spots unique to the evidence-based internal review

## Output style

Keep the final calibration output brief and explicit:
- what is safe to say
- what is risky to say
- what still needs proof

## Refusal / escalation conditions

Escalate when:
- core scoring is incomplete
- evidence quality is too low to calibrate responsibly
- the team is trying to use calibration as a substitute for the official assessment
