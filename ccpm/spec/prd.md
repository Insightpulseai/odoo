# Sample PRD — Claude Code PM

## R-1: Spec Ingestion
The system MUST accept a PRD markdown file and assign stable requirement IDs.

## R-2: Epic Generation
The system MUST convert requirements into epics with unique keys.

## R-3: GitHub Issue Sync
The system MUST create/update GitHub Issues idempotently from epics.

## R-4: Worktree Orchestration
The system MUST manage parallel git worktrees per issue.

## R-5: Agent Execution
The system MUST execute an "issue contract" (implement, test, evidence, PR).

## R-6: Traceability Ledger
The system MUST maintain an append-only event store linking requirements to commits, PRs, and deploys.
