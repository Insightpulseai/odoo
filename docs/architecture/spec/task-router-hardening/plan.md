# Task Router Hardening Plan

## Phase 1 — Contracts
- Task envelope schema
- Router state model
- Retry/dead-letter schema

## Phase 2 — Implementation
- Claim logic
- Dedupe logic
- Retry scheduler/backoff
- Dead-letter handling

## Phase 3 — Observability
- Metrics
- Audit events
- Evidence fixtures

## Phase 4 — CI Gates
- Schema validation
- State-machine tests
- Negative-path tests

## Phase 5 — Acceptance
- Replay proof
- Duplicate suppression proof
- Dead-letter proof
