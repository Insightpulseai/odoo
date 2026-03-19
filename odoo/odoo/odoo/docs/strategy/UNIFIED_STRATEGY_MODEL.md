# Unified Strategy Model

> Canonical SSOT: `ssot/governance/unified_strategy.yaml`

## Canonical rule

- **One strategy file**: `unified_strategy.yaml` is the single entry point
- `platform-strategy-2026.yaml` remains the primary time-bound objective source
- `enterprise_okrs.yaml` remains the supporting thematic KPI/OKR layer
- Both are read by the unified file; neither is deprecated

## Structure

```
Vision
  └── 7 Canonical Objectives (OBJ-001..007) — time-bound, sequenced
        ├── maps_to → 5 Thematic OKRs (obj_A..E) — steady-state lenses
        └── maps_to → 3 Rollup OKRs (O1..O3) — engineering pillars
              └── 4 Quarterly Programs (Q1..Q4)
```

## Interpretation

The **7 canonical objectives** define sequencing and deadlines (what to do when).
The **5 thematic OKRs** define steady-state performance targets (how well we run).
The **3 rollup OKRs** group objectives into engineering pillars (why it matters).

They complement each other — objectives answer "what by when", thematic OKRs answer "how good is good enough."

## Mapping

| OBJ | Name | Thematic | Rollup | Program |
|-----|------|----------|--------|---------|
| OBJ-001 | Identity baseline | obj_B, obj_E | O1 | Q1 |
| OBJ-002 | AzDo operationalization | obj_A, obj_D | O1 | Q1 |
| OBJ-003 | Foundry runtime hardening | obj_B | O3 | Q2 |
| OBJ-004 | Public advisory assistant | obj_A | O3 | Q2 |
| OBJ-005 | Automation consolidation | obj_A, obj_C | O1 | Q3 |
| OBJ-006 | OLTP/OLAP separation | obj_C | O3 | Q4 |
| OBJ-007 | Observability + security | obj_B, obj_E | O1 | Q1 |

## Delivery systems

| System | Role |
|--------|------|
| GitHub + repo SSOT | Engineering system of record |
| Azure Boards | Portfolio system of record |
| Plane | Optional mirror (SoW, not SoR) |
| Spec bundles (`spec/*/`) | Feature-level implementation truth |

## Explicit policy

- **Do not** build target-state planning around Viva Goals (retired Dec 2025)
- **Do not** treat Plane as system of record for strategic objectives
- **Do** link every Plane Epic to a canonical objective ID (`OBJ-xxx`)
- **Do** link every Plane Feature to a thematic OKR ID (`obj_x`)
