# Eval Engine Hardening PRD

## Problem
LLM-as-a-judge patterns inherently introduce non-determinism. Without strict boundaries, the pipeline is vulnerable to ambiguous approvals or relaxed evidence thresholds.

## Goal
Make the evaluation engine deterministic, strict, and explicitly fail-closed on ambiguity.

## Non-Goals
- Perfect generalized AI judgment.
- Replacing the pipeline with purely deterministic rules.

## Functional Requirements
- Strict schema-bound LLM outputs.
- Explicit threshold contracts for scoring.
- Bounded retry and timeout parameters for Judges.
- Fail-closed ambiguity handlers.
- Immutable evaluation result schematization.

## Acceptance Criteria
- Malformed unstructured LLM outputs result in `fail`.
- Partial evidence meets threshold triggers `fail`.
- Metric contracts correctly track ambiguous rejections.
- CI testing covers exact fallback paths.

## Risks
- False negatives paralyzing the assembly line.
- Silently shifting judge criteria.
- Flaky external LLM providers.
