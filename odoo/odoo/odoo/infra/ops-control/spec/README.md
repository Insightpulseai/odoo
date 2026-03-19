# Spec Kit Bundles

This directory contains **Spec Kit bundles** for various projects. Each bundle follows a standardized 4-file structure for comprehensive project documentation.

---

## 📦 Standard Spec Kit Structure

Each project bundle contains exactly 4 markdown files:

```
spec/<project-slug>/
├── constitution.md    # System principles, constraints, and non-negotiables
├── prd.md            # Product Requirements Document (problem, goals, acceptance)
├── plan.md           # Implementation roadmap with phases and timeline
└── tasks.md          # Granular task breakdown with progress tracking
```

---

## 📁 Current Bundles

### 1. [ops-control-room](./ops-control-room/)
**Parallel Runbook Executor**

Production-grade control room for concurrent task execution with:
- Parallel lanes (A/B/C/D)
- Atomic claiming (FOR UPDATE SKIP LOCKED)
- Real-time telemetry
- Worker fleet deployment (DO/K8s)
- Spec Kit generation

**Status:** M0 complete (database foundation), M1 in progress (execution core)

### 2. [continue-orchestrator](./continue-orchestrator/)
**Continue Agent Orchestrator**

Agent orchestration system for managing Continue IDE agents.

---

## ✅ Validation

All Spec Kit bundles are automatically validated by CI using:

**Script:** `/scripts/validate_spec_kit.py`  
**CI Workflow:** `/.github/workflows/spec-kit-enforce.yml`

### Validation Rules

Each bundle must:
- ✅ Contain all 4 required files
- ✅ Have meaningful content in each file (>40 chars)
- ✅ Include "acceptance" criteria in PRD
- ✅ Include "principles" or "tenets" in constitution
- ✅ Include "phases" or "milestones" in plan
- ✅ Include task items with checkboxes in tasks.md

### Run Validation Locally

```bash
python3 scripts/validate_spec_kit.py
```

**Expected output:**
```
[SPEC-KIT] Starting Spec Kit validation...
[SPEC-KIT] Found 2 bundle(s) to validate

[SPEC-KIT] Validating bundle: ops-control-room
[SPEC-KIT] ✅ Bundle 'ops-control-room' is valid

[SPEC-KIT] Validating bundle: continue-orchestrator
[SPEC-KIT] ✅ Bundle 'continue-orchestrator' is valid

[SPEC-KIT] ✅ All 2 bundle(s) passed validation!
```

---

## 🎯 Purpose of Spec Kits

Spec Kits provide:

1. **Constitution** - Immutable principles and design constraints
2. **PRD** - Clear problem statement, goals, and acceptance criteria
3. **Plan** - Phased implementation roadmap with timeline
4. **Tasks** - Granular breakdown with progress tracking

**Benefits:**
- 📖 Complete project documentation in one place
- 🎯 Clear goals and success criteria
- 📊 Transparent progress tracking
- 🔒 CI-enforced compliance
- 🗺️ Shared understanding across team

---

## 📝 Creating a New Spec Kit

### 1. Create Directory
```bash
mkdir -p spec/my-project
```

### 2. Create Required Files
```bash
touch spec/my-project/constitution.md
touch spec/my-project/prd.md
touch spec/my-project/plan.md
touch spec/my-project/tasks.md
```

### 3. Fill in Content

**constitution.md template:**
```markdown
# Constitution — My Project

## 0. Purpose
[What is this project and why does it exist?]

## 1. Core Principles (Non-negotiables)
1) [Principle 1]
2) [Principle 2]
...

## 2. Scope Boundaries
### In scope (v1)
- [Feature 1]
- [Feature 2]

### Out of scope (v1)
- [Excluded 1]
- [Excluded 2]
```

**prd.md template:**
```markdown
# PRD — My Project

## 1) Problem
[What problem are we solving?]

## 2) Goals
### Success criteria
1. [Goal 1]
2. [Goal 2]

## Acceptance Criteria (Hard)
- [Criteria 1]
- [Criteria 2]
```

**plan.md template:**
```markdown
# Plan — My Project

## A) Decisions Locked
1) [Decision 1]
2) [Decision 2]

## B) Phased Implementation
### Phase 0 — Foundation
[Tasks]

### Phase 1 — Core
[Tasks]
```

**tasks.md template:**
```markdown
# Tasks — My Project

## T0 — Foundation
- [ ] T0.1 Task one
- [ ] T0.2 Task two

## T1 — Core
- [ ] T1.1 Task one
- [ ] T1.2 Task two
```

### 4. Validate
```bash
python3 scripts/validate_spec_kit.py
```

### 5. Commit
```bash
git add spec/my-project
git commit -m "Add Spec Kit for my-project"
```

The CI will automatically validate your Spec Kit on push!

---

## 🔗 Related Files

- **Validation Script:** `/scripts/validate_spec_kit.py`
- **CI Workflow:** `/.github/workflows/spec-kit-enforce.yml`
- **Documentation:** `/SPEC_KIT_CREATED.md`

---

## 📚 Learn More

See any existing bundle (like `ops-control-room/`) for a complete example of:
- Comprehensive constitution with principles
- Detailed PRD with acceptance criteria
- Multi-phase implementation plan
- Granular task breakdown with estimates

---

**All Spec Kits are CI-validated and production-ready! ✅**
