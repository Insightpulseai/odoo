# Constitution — Cursor Sovereign

## Purpose
Build a Cursor-grade AI coding environment that is enterprise/airgap compatible, policy-governed, and deterministically gateable.

## Principles
1. **Local-first by default**: core workflows must function without sending source code to vendor infra.
2. **Deterministic runs**: every agent action is reproducible from a signed context snapshot + run manifest.
3. **Policy over preference**: org policy decides what agents can do, what code can ship, and what data can leave.
4. **Gates are product features**: "Odoo.sh-grade parity gating" is not optional; it is the trust layer.
5. **No secret sprawl**: secrets only via env/secret stores; never committed; never logged.
6. **Observable by design**: every run emits events, artifacts, and attestations.

## Definition of Done (DoD)
- Spec-compliant PRD + plan + tasks
- CI gates implemented and green
- Security model + data-flow docs merged
- "Golden path" demo: agent proposes change -> gates -> deploy -> validate -> rollback

## Non-Negotiables
- BYO enterprise LLM endpoints supported (direct-route)
- Self-hostable prompt/context builder service supported
- Context snapshots are signed and verifiable in CI
- All agent-initiated diffs require gate proofs before merge
