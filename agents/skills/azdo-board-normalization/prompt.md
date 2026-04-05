# Skill: azdo.board.normalization

## Reasoning Strategy

You normalize an Azure DevOps board from a flat or misaligned structure to the canonical IPAI hierarchy model. This is a compound skill that orchestrates multiple board operations.

### Target Model

```
Epic (7 canonical) → Issue (workstream) → Task (substep)
```

### Normalization Protocol

#### Phase 1: Audit

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

#### Phase 2: Create Canonical Epics

For each canonical spec bundle, create an Epic if it doesn't exist:
- Odoo on Azure Operating Model
- AI Platform Operating Model
- AI-Led Engineering Model
- Data Intelligence Operating Model
- Governance Drift Closure
- Azure Assessment Harness
- Odoo SDK

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

After all children are reparented:
1. Set state to Done on each legacy Epic
2. Do NOT delete — preserve history

#### Phase 6: Clean Up

- Delete `_dummy_` or placeholder items (with `--yes`)
- Remove duplicate Items created by failed operations
- Verify final state

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
- It is a cross-cutting objective that doesn't map to one bundle (rare)

### IPAI Reference State (2026-04-05)

After normalization:
- 7 canonical Epics: #238-244
- 2 retained OBJ Epics: #1 (Identity), #7 (Revenue)
- 14 legacy Epics: closed to Done
- 19 Issues as workstream layer
- 171 Tasks (58 reparented + 14 new governance tasks)
- 2 evidence-closure Tasks marked Done (#273 PITR, #279 KV PE)

## Edge Cases

- Basic process has no Feature type — use Issue instead
- `az boards work-item create --type Feature` will error with VS402323
- Reparenting a work item that has children does NOT move the children — they stay attached
- Closing an Epic does not close its children — close each explicitly if needed
- WIQL `[System.Parent] = 0` may not work for orphan detection on all process types

## Notes

- Run Phase 1 (audit) first in dry-run mode to produce the normalization matrix
- Never reparent and close in the same command — always reparent first, verify, then close
- The normalization matrix should be committed as evidence
