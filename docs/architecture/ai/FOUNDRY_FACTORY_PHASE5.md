# Foundry Factory Architecture (Phase 5)

## Supervisor Topology
The Supervisor is a Singleton meta-agent daemon running continuous polling (`setInterval`) against the authoritative Agent Registry YAMLs.

## Execution Flow
1. **Registry** parsed into Memory Index.
2. **Supervisor** isolates active, non-terminal agents.
3. **Transition Worker** locks the target agent optimistic memory mapping.
4. **Eval Engine / Criteria Guards** determine eligibility against physical SSOT YAML constraints.
5. **Record Minting**: A highly structured `ipai.promotion.v1.hardened` record is written to `agents/promotions/`.
6. **Passport Bump**: The agent's `version` is incremented and `stage` reflects the new bounds.

## Exactly-Once Semantics
Due to strict CI requirements, transitions employ single-writer idempotent transition issuance under the documented lock/write assumptions. This is achieved by minting a deterministic `Transition Key` (e.g. `odoo-sage:S03:S04:v1`). The file system's atomic write locks prevent dual issuance even under heavy loop execution.

## Locking Assumptions
The transition worker's idempotency guarantee depends on:
- a shared filesystem or equivalent lock substrate visible to all competing writers
- atomic create semantics for lock acquisition
- immutable record write path after successful lock acquisition
- no out-of-band writers bypassing the transition contract

Outside these assumptions, the system should be treated as fail-closed and not exactly-once.

## Why Immutable Records?
Immutable records serve as the absolute source of truth for CI Gates. When Github Actions runs `agents foundry ci-run`, these JSON records bypass the registry overhead entirely and act as explicit database facts.
