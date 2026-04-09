# Assessment Answer Drafter

## Purpose

Draft conservative, evidence-backed answers for the internal assessment harness.

This skill converts harvested evidence into structured answers that resemble the type of reasoning an architect would use when answering an assessment questionnaire.

It does not produce the final score.
It does not normalize to Microsoft's official score.
It drafts the safest justifiable answer based on available evidence.

## When to use

Use this skill when:
- converting evidence into question responses
- creating pre-portal answer packs for Microsoft Assessments
- drafting internal answers for WAF core, overlays, or adjacent assessment families
- preparing answer sheets for later judge review

## Inputs

Required:
- output from `assessment-evidence-harvester`
- target question or domain
- target assessment family
- relevant persona context if available

Optional:
- current internal baseline score
- prior answer pack
- official portal-prep checklist

## Output contract

For each answer, return:

- `question_or_domain`
- `proposed_answer`
- `answer_type`
  - `yes`
  - `partial`
  - `no`
  - `not_enough_evidence`
- `justification`
- `evidence_basis`
- `confidence`
- `safe_answer`
- `risk_notes`
- `follow_up_needed`

## Core rules

### 1. Answer conservatively

If evidence is partial, prefer:
- `partial`
- `no`
- or `not_enough_evidence`

Do not upgrade an answer just because a resource exists.

### 2. Keep the distinction explicit

In the justification, make it obvious whether the answer is based on:
- present only
- partly governed
- proven and repeatable

### 3. Avoid aspirational wording

Never answer based on what the architecture intends unless the evidence shows the intended state is actually in force.

### 4. Use workload context correctly

If the question is workload-specific, use the correct overlay:
- SaaS
- AI
- SAP-like workload operations
- Mission-critical where justified

### 5. Use transformation context correctly

If the question is about readiness to change, use the transformation-readiness phase:
- Discover
- Analyze
- Design
- Implement
- Operate

## Drafting procedure

### Step 1 -- Establish answer posture

Choose the minimal defensible answer:
- yes
- partial
- no
- not enough evidence

### Step 2 -- Justify with evidence

Summarize why the answer is correct using only the strongest evidence.

### Step 3 -- Add caveats

State the major caveat if:
- drift exists
- testing is absent
- governance is partial
- ownership is unclear

### Step 4 -- Propose what would improve the answer

List the smallest evidence or execution step needed to raise confidence.

## Answer patterns

### Strong positive

Use only when evidence shows the control is:
- present
- governed
- and proven

### Partial

Use when:
- control exists but is not yet consistently governed, or
- governance exists but proof is incomplete

### Negative

Use when:
- control is absent, or
- evidence is too weak to support even a partial maturity claim

## Special handling for the official Microsoft portal

When drafting answer packs for the official Microsoft assessment:
- treat the internal answer as a **prep recommendation**
- not as a substitute for the portal
- prefer conservative answers where the portal likely expects operational proof

## Refusal / escalation conditions

Escalate when:
- the evidence pack is missing
- the question requires a live fact not yet gathered
- the user is trying to force a stronger answer than the evidence supports
