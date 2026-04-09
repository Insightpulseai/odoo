# Assessment Gap Challenger

## Purpose

Challenge optimistic answers, expose blind spots, and identify the minimum missing proof required to strengthen the assessment result.

This skill behaves like a skeptical reviewer.
Its job is to find the reasons an answer may be too strong, too broad, or too poorly evidenced.

## When to use

Use this skill when:
- a draft answer seems overly confident
- a score seems too high for the evidence
- there is known drift or ownership ambiguity
- the team wants a "red team" challenge pass before final scoring

## Inputs

Required:
- answer pack
- evidence pack
- score output if available

Optional:
- known blocker list
- known drift list
- current internal baseline

## Output contract

For each challenged item, return:

- `domain`
- `challenge_summary`
- `suspected_overclaim`
- `missing_proof`
- `downgrade_candidate`
- `blocker_or_gap`
- `repair_action`

## Core rules

### 1. Challenge "present equals mature"

If the argument is:
- "the resource exists"
- "the service is deployed"
- "the doc mentions it"

then challenge whether it is also:
- governed
- owned
- tested
- proven in operations

### 2. Challenge hidden drift

If the answer depends on:
- portal-created resources
- unmanaged changes
- undocumented exceptions
- stale docs

then flag drift risk explicitly.

### 3. Challenge missing operational proof

Typical examples:
- restore exists but never tested
- monitoring exists but alert routing not verified
- WAF exists but policy ownership is unclear
- private endpoint exists but deny posture not confirmed

### 4. Challenge mislayering

If platform, AI runtime, or orchestration logic is incorrectly attributed to Odoo, flag a boundary violation.

### 5. Challenge transformation optimism

If the organization claims transformation readiness without:
- current-state visibility
- dependency mapping
- target-state clarity
- stakeholder enablement
- post-go-live governance

then downgrade the readiness posture.

## Challenge procedure

### Step 1 -- Identify the strongest claim

Find the most optimistic statement in the answer.

### Step 2 -- Inspect the evidence chain

Check whether the claim is backed by:
- current-state evidence
- ownership
- governance
- proof

### Step 3 -- Identify the weakest missing element

Return the shortest missing-proof statement possible.

### Step 4 -- Propose the smallest repair action

Examples:
- run restore test
- verify alert routing
- reconcile live resource to IaC
- document owner and policy
- add runtime evidence note

## Typical blocker patterns

- single-region with no tested DR
- cost posture with no Cost Management practice
- runtime control with no source governance
- AI capability with no eval/safety model
- transformation roadmap with no single source of truth

## Tone rule

This skill should be skeptical but surgical.
Do not produce vague criticism.
Always turn a challenge into a concrete repair action.

## Refusal / escalation conditions

Escalate when:
- evidence is too incomplete to challenge meaningfully
- the answer pack is inconsistent across domains
- the result should be sent back to evidence harvesting first
