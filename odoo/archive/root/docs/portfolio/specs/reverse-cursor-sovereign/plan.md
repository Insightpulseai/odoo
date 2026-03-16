# Plan — Cursor Sovereign

## Phase 0 — Repo Wiring (1–2 days)
- Add Spec Kit bundle
- Add scaffolding directories:
  - `services/prompt-builder/`
  - `pkgs/context-snapshot/`
  - `gates/` (catalog + gate runner)
- Add CI workflow skeleton for gates

## Phase 1 — Context Snapshot MVP
- Implement snapshot generator:
  - Merkle hashing
  - ignore support
  - manifest emission
- Add verifier command for CI

## Phase 2 — Gate Runner MVP
- Implement gate runner:
  - preflight (fast)
  - full (comprehensive)
- Add baseline gates:
  - forbidden enterprise modules
  - secret scan
  - lint + unit tests
  - docs drift (mkdocs build + diff)
  - seed drift (regen + diff)

## Phase 3 — Prompt/Context Builder Service
- Dockerized service with:
  - policy checks
  - prompt assembly
  - enterprise LLM connectors (direct)
- Emit run manifests + gate proofs

## Phase 4 — Agent Loop Integration
- Agent runner that:
  - creates snapshot
  - runs change plan
  - executes tools
  - runs gates
  - outputs PR-ready artifacts

## Phase 5 — Docs + Primer Tokens
- mkdocs theme wiring
- Primer-compatible CSS tokens
- Add: security/threat model, data flows, gate catalog, runbooks

## Phase 6 — Hardening
- SLSA-style attestations
- signing keys integration
- performance tuning
