# Tasks: [FEATURE NAME]

> **Spec**: `spec/[FEATURE_SLUG]/spec.md`
> **Plan**: `spec/[FEATURE_SLUG]/plan.md`
> **Generated**: [DATE]

---

## Task Legend

- `[TaskID]` — Unique identifier (T001, T002, ...)
- `[P]` — Parallelizable (can run concurrently with other [P] tasks)
- `[US#]` — Linked user story
- File paths are absolute from repo root

---

## Phase 1: Setup

- [ ] T001 [P] Project scaffolding and directory structure
- [ ] T002 [P] Configuration files and environment setup

## Phase 2: Foundational

> Critical infrastructure that blocks user story work.

- [ ] T003 Data models and migrations — `[FILE_PATH]`
- [ ] T004 Base service/module setup — `[FILE_PATH]`

## Phase 3: User Story 1 (P1)

> [US1 Title]: [Brief description]

- [ ] T005 [US1] Write tests for [feature] — `[TEST_PATH]`
- [ ] T006 [US1] Implement [component] — `[FILE_PATH]`
- [ ] T007 [US1] Integration test — `[TEST_PATH]`

**Checkpoint**: US1 independently testable and deployable.

## Phase 4: User Story 2 (P1)

> [US2 Title]: [Brief description]

- [ ] T008 [US2] Write tests for [feature] — `[TEST_PATH]`
- [ ] T009 [US2] Implement [component] — `[FILE_PATH]`
- [ ] T010 [US2] Integration test — `[TEST_PATH]`

**Checkpoint**: US2 independently testable and deployable.

## Phase 5: User Story 3 (P2)

> [US3 Title]: [Brief description]

- [ ] T011 [US3] Write tests — `[TEST_PATH]`
- [ ] T012 [US3] Implement — `[FILE_PATH]`

## Phase 6: Polish & Cross-Cutting

- [ ] T013 Documentation updates — `docs/`
- [ ] T014 CI/CD pipeline updates — `.github/workflows/`
- [ ] T015 Final verification — `scripts/`

---

## Dependencies

```
T001, T002 (parallel) → T003 → T004
T004 → T005..T007 (US1)
T004 → T008..T010 (US2, parallel with US1)
US1 + US2 → T011..T012 (US3)
All → T013..T015 (Polish)
```

---

## Implementation Strategy

**Recommended**: MVP-first
1. Complete Phase 1-2 (Setup + Foundational)
2. Deliver US1 as standalone MVP
3. Layer US2 incrementally
4. Add US3 if time permits

---

## Progress

| Phase | Total | Done | % |
|-------|-------|------|---|
| Setup | 2 | 0 | 0% |
| Foundational | 2 | 0 | 0% |
| US1 | 3 | 0 | 0% |
| US2 | 3 | 0 | 0% |
| US3 | 2 | 0 | 0% |
| Polish | 3 | 0 | 0% |
| **Total** | **15** | **0** | **0%** |
