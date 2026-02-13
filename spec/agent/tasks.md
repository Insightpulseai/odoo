# Tasks: Agent Execution Constraints

> **Spec**: `spec/agent/prd.md`
> **Plan**: `spec/agent/plan.md`
> **Generated**: 2026-02-12

---

## Task Legend

- `[TaskID]` — Unique identifier
- `[P]` — Parallelizable
- `[US#]` — Linked user story
- File paths are absolute from repo root

---

## Phase 1: Governance Artifacts

- [x] T001 [P] [US1] Author constitution with forbidden operations — `spec/agent/constitution.md`
- [x] T002 [P] [US2] Create capability manifest with 8 verified capabilities — `agents/capabilities/manifest.json`
- [x] T003 [P] [US1] Write PRD for agent execution constraints — `spec/agent/prd.md`

**Checkpoint**: All governance documents exist and are non-empty.

## Phase 2: Enforcement Infrastructure

- [x] T004 [US1] Create CI gate for policy enforcement — `.github/workflows/spec-kit-enforce.yml`
- [x] T005 [US1] Add spec-kit validation to CI pipeline — `scripts/check-spec-kit.sh`
- [x] T006 [P] [US3] Document response patterns in constitution — `spec/agent/constitution.md` §4

**Checkpoint**: CI gates pass on current constitution.

## Phase 3: Integration

- [x] T007 [US1] Register agent constraints in CLAUDE.md — `CLAUDE.md`
- [x] T008 [US2] Document capability verification process — `spec/agent/constitution.md` §5
- [x] T009 [P] [US3] Add self-correction examples to constitution — `spec/agent/constitution.md` §8-9

**Checkpoint**: Full spec bundle passes `./scripts/check-spec-kit.sh`.

---

## Dependencies

```
T001, T002, T003 (parallel) → T004, T005, T006
T004..T006 → T007, T008, T009
```

---

## Progress

| Phase | Total | Done | % |
|-------|-------|------|---|
| Governance | 3 | 3 | 100% |
| Enforcement | 3 | 3 | 100% |
| Integration | 3 | 3 | 100% |
| **Total** | **9** | **9** | **100%** |
