# Implementation Plan: [FEATURE NAME]

> **Branch**: `[BRANCH_NAME]`
> **Spec**: `spec/[FEATURE_SLUG]/spec.md`
> **Created**: [DATE]

---

## Summary

### Primary Requirements
- [From spec FR-001, FR-002, etc.]

### Technical Approach
[1-3 sentence overview of the implementation strategy]

---

## Technical Context

| Attribute | Value |
|-----------|-------|
| **Language/Version** | [e.g., Python 3.12] |
| **Framework** | [e.g., Odoo 19 CE] |
| **Database** | [e.g., PostgreSQL 16] |
| **Testing** | [e.g., pytest, Odoo test framework] |
| **Target Platform** | [e.g., Linux, Docker] |
| **Dependencies** | [Key dependencies] |

---

## Constitutional Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| [Principle 1] | PASS/FAIL | [Explanation] |
| [Principle 2] | PASS/FAIL | [Explanation] |

---

## Project Structure

```
spec/[FEATURE_SLUG]/
├── spec.md
├── plan.md
├── tasks.md
├── research.md          # Optional: unknowns resolved
├── data-model.md        # Optional: entity relationships
├── quickstart.md        # Optional: getting started
└── contracts/           # Optional: API contracts
    └── api.yml
```

---

## Source Code Layout

```
[PROJECT_SPECIFIC_LAYOUT]
```

---

## Architecture Decisions

| Decision | Justification | Alternatives Considered |
|----------|---------------|------------------------|
| [Decision 1] | [Why this choice] | [Other options] |
| [Decision 2] | [Why this choice] | [Other options] |

---

## Complexity Assessment

| Component | Complexity | Justification |
|-----------|------------|---------------|
| [Component 1] | Low/Medium/High | [Why] |
| [Component 2] | Low/Medium/High | [Why] |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [Impact] | [Mitigation strategy] |
| [Risk 2] | [Impact] | [Mitigation strategy] |

---

## Verification Commands

```bash
./scripts/repo_health.sh
./scripts/spec_validate.sh
# Add feature-specific checks
```

---

## Handoff

- **Next**: `/speckit.tasks` to generate task breakdown
- **Then**: `/speckit.checklist` for quality validation
- **Finally**: `/speckit.implement` to execute
