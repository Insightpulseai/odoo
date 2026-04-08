# Foundry Supervisor Runbook

## Overview
The Foundry Supervisor dictates the continuous pipeline mapping Agents to physical progression states.

## Start / Stop / Replay Semantics
- **Start**: `agents foundry daemon`
- **Replay**: Safe. The `idempotency.transition_key` guarantees that a crashed or duplicated loop will not double-mint a `PromotionRecord` JSON file due to the strict `fs.writeFileSync(..., {flag: 'wx'})` file system level lease mechanism.
- **Dry-Run vs Live**: Configured in `ssot/agents/foundry_supervisor.yaml`. Default is `dry-run` to prevent accidental minting during onboarding.

## Dedupe Recovery Procedure
If an agent gets "stuck" due to lock contention or an orphaned/corrupted promotion record:
1. Identify the blocking transition key in terminal logs.
2. Locate the orphaned JSON in `agents/promotions/`.
3. If the JSON is malformed (zero bytes), manually delete it.
4. Restart the supervisor; it will re-evaluate and re-emit a clean record.

## Backfill / Replay Policy
Because records are append-only immutable files bound to precise gate versions, backfilling historical evidence is strictly mapped to manual `agents foundry promote <agent-id> <target-stage>` commands.
