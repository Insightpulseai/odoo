# Constitution — Platform Master Index

Version: 1.0.0 | Status: Active | Last updated: 2026-03-01

## Purpose
Single source of truth for cross-cutting platform work across all milestones,
epics, and task streams. This spec bundle is the **index**, not the implementation —
it references other spec bundles, migrations, contracts, and PRs.

## Non-Negotiable Rules

**Rule 1: Every task references its evidence.**
No task is marked complete without a concrete artifact: migration file,
edge function, spec bundle, contract doc, or CI workflow.

**Rule 2: Dependencies are explicit.**
Milestones declare their prerequisite milestones. Tasks within epics
declare their prerequisite tasks.

**Rule 3: "Shipped" means deployed + verified, not just committed.**
A migration committed but not applied is "staged", not "shipped".
An edge function committed but not deployed is "staged".

**Rule 4: Missing items are tracked, not hidden.**
Tasks identified as needed but not yet planned appear in the
"Missing / Should Have Been Planned" section with clear rationale.

**Rule 5: Status is auditable.**
Every status claim cites a file path, migration name, or edge function name.
