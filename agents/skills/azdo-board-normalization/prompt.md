# Skill: azdo.board.normalization

## Target Model

For the current IPAI Azure DevOps **Basic** process, the canonical hierarchy is:

```
Epic → Issue → Task
```

No Feature or User Story layer is assumed. These types do not exist in the Basic process template.

---

## Allowlists and Denylists

### canonical_epics

These are the only Epics that should be open (To Do or Doing) after normalization:

- Odoo on Azure Operating Model
- AI Platform Operating Model
- AI-Led Engineering Model
- Data Intelligence Operating Model
- Governance Drift Closure
- Azure Assessment Harness
- Odoo SDK

### retain_epics

These cross-cutting Epics are explicitly retained and must NOT be closed or converted:

- #1 — [OBJ-001] Identity Baseline & Platform Foundation
- #7 — [OBJ-007] Revenue-Ready Product Portfolio

### delete_placeholders

These items should be deleted (not closed) during cleanup:

- `_dummy_`

---

## Non-Goals

This skill restructures board hierarchy only. It does NOT:

- Change technical completion state of platform work
- Close open platform blockers (e.g. PG hardening, Entra OIDC activation)
- Imply operational readiness by marking structural items as Done
- Assert that task counts are exact invariants (counts are expected state, not pass/fail gates)

Board normalization is **structural**. Platform remediation is tracked separately in governance Issues and evidence packs.

---

## Dry-Run Rule

**Phase 1 must always run in dry-run mode first.** No mutations until the normalization matrix is produced and reviewed.

Phases 2-6 may mutate the board only after:
1. The normalization matrix has been written to evidence
2. The matrix has been reviewed (by human or by the invoking agent)
3. Destructive operations (delete, close) have been explicitly approved

---

## Evidence Rule

Every normalization run must emit:

1. **Normalization matrix** — `docs/evidence/boards/<timestamp>/normalization-matrix.md`
2. **Migration log** — `docs/evidence/boards/<timestamp>/work-item-migration.csv`
3. **Final board state summary** — `docs/evidence/boards/<timestamp>/board-state-summary.md`

These artifacts must be committed before the normalization run is considered complete.

---

## Reasoning Strategy

You normalize an Azure DevOps board from a flat or misaligned structure to the canonical IPAI hierarchy model. This is a compound skill that orchestrates multiple board operations.

### Normalization Protocol

#### Phase 1: Audit (always dry-run)

1. Query all Epics, count by state
2. Query all Issues (should exist; if 0, the board needs Issue layer creation)
3. Count Tasks and check for orphans (no parent)
4. Produce a normalization matrix:

```
| Current Item | Current Type | Current Parent | Target Type | Target Parent | Action |
|---|---|---|---|---|---|
| Go-Live Critical Path | Epic | - | Issue | #238 | Convert |
| _dummy_ | Epic | - | - | - | Delete |
| Smoke test task | Task | #63 | Task | #247 | Reparent |
```

5. Write matrix to evidence directory — do NOT proceed until written

#### Phase 2: Create Canonical Epics

For each entry in `canonical_epics`, create an Epic if it doesn't already exist.

#### Phase 3: Create Issue Layer

Under each canonical Epic, create Issues that represent workstreams.
An Issue should be created when:
- It produces a real artifact or evidence pack
- It represents a distinct deliverable or decision
- It groups related Tasks into a coherent execution unit

#### Phase 4: Reparent Tasks

For each legacy Epic being retired:
1. Query its child Tasks
2. Identify the correct new Issue parent (by domain affinity)
3. Update each Task's `System.Parent` to the new Issue ID
4. Verify all children migrated

#### Phase 5: Close Legacy Epics

After all children are reparented, close legacy Epics **except**:
- Epics in the `retain_epics` allowlist
- Epics that still have unresolved child Issues or Tasks (do not close parents with open children unless explicitly approved)

For closeable Epics:
1. Set state to Done
2. Do NOT delete — preserve history

#### Phase 6: Clean Up

- Delete items in `delete_placeholders` list only (with `--yes`)
- Remove duplicate Items created by failed operations
- Verify final state
- Write migration log and board state summary to evidence

### Decision Rules

**When to convert an Epic to an Issue:**
- It does not represent a top-level strategic bundle
- It is execution-scoped (a project phase, a go-live milestone, a module)
- Its natural parent is one of the 7 canonical Epics

**When to promote a Task to an Issue:**
- It produces a real artifact or evidence pack
- It is not merely a substep of another deliverable
- It has or should have its own child Tasks

**When to keep an Epic as-is:**
- It is one of the 7 canonical bundles
- It is in the `retain_epics` allowlist
- It still has unresolved children and closing would mask open work

**When NOT to close an Epic:**
- It still has unresolved child Issues or Tasks
- It is explicitly retained in `retain_epics`
- It is still the best cross-cutting container for active work
- Closing it would imply a platform blocker is resolved when it is not

### IPAI Reference State (2026-04-05)

After normalization:
- 7 canonical Epics: #238-244
- 2 retained OBJ Epics: #1 (Identity), #7 (Revenue)
- 14 legacy Epics: closed to Done
- 19 Issues as workstream layer
- Task counts are expected state, not hardcoded invariants

## Edge Cases

- Basic process has no Feature type — use Issue instead
- `az boards work-item create --type Feature` will error with VS402323
- Reparenting a work item that has children does NOT move the children — they stay attached
- Closing an Epic does not close its children — close each explicitly if needed
- WIQL `[System.Parent] = 0` may not work for orphan detection on all process types

## Notes

- Never reparent and close in the same command — always reparent first, verify, then close
- The normalization matrix must be committed as evidence before any mutations
- Board normalization does not imply technical readiness — keep blockers tracked in governance Issues
