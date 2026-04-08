# Task Router Hardening PRD

## Problem
Delivery correctness is not fully bounded unless enqueue/claim/retry/dead-letter semantics are explicitly tracked and bounded.

## Goal
Make task routing deterministic, observable, idempotent, and fail-closed.

## Non-Goals
- Not a replacement for the Supervisor.
- Not a new orchestration framework.
- Not universal exactly-once across arbitrary substrates (limited to at-least-once with duplicate suppression).

## Personas
- Router
- Worker
- Supervisor
- Operator

## Functional Requirements
- Deterministic routing key.
- Claim/lease semantics.
- Retry budget and backoff contract.
- Dead-letter queue contract.
- Replay/recovery semantics.
- Metrics and evidence surfaces.

## Acceptance Criteria
- Malformed tasks do not enter runnable flow.
- Duplicate deliveries are detectable and bounded.
- Retry exhaustion lands in dead-letter deterministically.
- Stale claims are recoverable without silent duplication.
- CI fails on undocumented state transitions.

## Risks
- Duplicate execution.
- Poison-message loops.
- Silent loss after partial claim.
- Lease expiry races.
- Dead-letter drift.
