# Colima Desktop — Spec Kit

**Spec-driven development bundle for Docker Desktop-like control plane for Colima**

This directory contains the complete specification for Colima Desktop, following the [Spec Kit methodology](https://github.com/github/spec-kit) for evidence-based software development.

---

## Table of Contents

- [Overview](#overview)
- [Spec Files](#spec-files)
- [How to Use This Spec](#how-to-use-this-spec)
- [Implementation Status](#implementation-status)
- [Architecture Summary](#architecture-summary)
- [Key Constraints](#key-constraints)

---

## Overview

**Project:** Colima Desktop
**Type:** CLI-first daemon + optional Electron UI
**Purpose:** Docker Desktop-like control plane for Colima on macOS

**Spec Kit Components:**
1. **constitution.md** - Non-negotiable rules and security constraints
2. **plan.md** - Implementation plan and phased rollout
3. **prd.md** - Product requirements (to be created)
4. **tasks.md** - Task breakdown (to be created)

**Status:** Phase 2 - Daemon + CLI Core (In Progress)

---

## Spec Files

### constitution.md

**Purpose:** Define non-negotiable constraints that CANNOT be violated

**Contents:**
- Core principles (No Colima forking, Security first, CLI-first, etc.)
- Security boundaries (Electron process model)
- Architecture constraints (Daemon, CLI, State management)
- Forbidden operations
- Compliance verification checklist

**When to reference:**
- Before implementing any feature
- During code review
- When making architectural decisions
- Security audit

**Key rules:**
1. ✅ Integration via `colima` CLI only (never fork/patch)
2. ✅ Electron `contextIsolation` enabled (MUST)
3. ✅ Daemon binds to localhost only (security)
4. ✅ All state under `~/.colima-desktop/` (deterministic)
5. ✅ Config changes require user approval (safe restarts)

**Read online:** [constitution.md](./constitution.md)

---

### plan.md

**Purpose:** Implementation plan with phased rollout

**Contents:**
- Context and motivation
- Architecture overview with diagrams
- Directory structure
- Technology stack justification
- State management design
- Critical files identification
- 4-phase implementation timeline

**Phases:**

**Phase 1: Foundation & Spec Kit** (Week 1-2) ✅
- Spec Kit bundle (constitution, plan)
- Directory scaffolding
- Core services (Colima CLI wrapper, config, types)
- Unit tests

**Phase 2: Daemon + CLI Core** (Week 3-4) 🔄 In Progress
- Fastify daemon with REST API
- yargs CLI (status, start, stop, config, logs)
- Daemon lifecycle (PID file, graceful shutdown)
- Integration tests

**Phase 3: Electron UI** (Week 5-6) 📋 Planned
- Menubar app with React
- Security implementation (contextBridge, IPC)
- UI components (Status, Controls, Settings, Logs)
- electron-builder packaging

**Phase 4: Polish, Docs, CI** (Week 7-8) 📋 Planned
- **Comprehensive documentation** (READMEs, API reference)
- Makefile targets
- CI workflow (lint, test, build)
- Security audit
- Homebrew formula (optional)

**Read online:** [plan.md](./plan.md)

---

### prd.md (To Be Created)

**Purpose:** Product requirements document

**Expected contents:**
- User stories and personas
- Feature requirements
- Success criteria
- Non-functional requirements (performance, reliability)
- Acceptance criteria

**Status:** Not yet created (will be extracted from plan.md)

---

### tasks.md (To Be Created)

**Purpose:** Granular task breakdown

**Expected contents:**
- Phase 1 tasks (✅ Completed)
- Phase 2 tasks (🔄 In Progress)
- Phase 3 tasks (📋 Planned)
- Phase 4 tasks (📋 Planned)
- Task dependencies
- Estimated effort

**Status:** Not yet created (will be generated from plan.md)

---

## How to Use This Spec

### For Developers

**Starting a new feature:**
1. Read `constitution.md` - Understand constraints
2. Read `plan.md` - Understand architecture
3. Check current phase - Know what's implemented
4. Write code following rules
5. Reference spec in PR description

**During code review:**
1. Check compliance with `constitution.md`
2. Verify alignment with `plan.md` architecture
3. Ensure no forbidden operations
4. Validate security model

**Example PR description:**
```markdown
## Summary
Implement GET /v1/status endpoint

## Spec Reference
- Phase 2 deliverable: REST API daemon (plan.md:307)
- API contract: plan.md:186-203
- Security: localhost binding (constitution.md:297)

## Verification
- [x] Follows architecture constraints
- [x] Passes security checklist
- [x] Unit tests written
```

### For Reviewers

**Checklist:**
1. **Constitution compliance**
   - [ ] No Colima forking?
   - [ ] Localhost-only API?
   - [ ] Atomic writes?
   - [ ] Electron security (if UI)?

2. **Architecture alignment**
   - [ ] Follows directory structure?
   - [ ] Uses correct tech stack?
   - [ ] State management correct?

3. **Phase alignment**
   - [ ] Matches current phase deliverables?
   - [ ] Doesn't skip ahead?
   - [ ] Prerequisites met?

### For Project Managers

**Tracking progress:**
- Phase 1: ✅ Completed (constitution, plan, core services)
- Phase 2: 🔄 In Progress (daemon, CLI)
- Phase 3: 📋 Planned (Electron UI)
- Phase 4: 📋 Planned (docs, CI, polish)

**Next milestones:**
1. Complete Phase 2 daemon + CLI
2. Write integration tests
3. Begin Electron UI (Phase 3)
4. Comprehensive documentation (Phase 4)

---

## Implementation Status

### Completed ✅

**Spec Kit:**
- ✅ `constitution.md` - All rules defined
- ✅ `plan.md` - Complete implementation plan

**Foundation (Phase 1):**
- ✅ Directory structure scaffolded
- ✅ TypeScript configuration
- ✅ Build tooling (vitest, ESLint)
- ✅ Core types (`src/shared/types.ts`)
- ✅ Colima CLI wrapper (`src/daemon/services/colima.ts`)
- ✅ Config management (`src/shared/config.ts`)

### In Progress 🔄

**Daemon + CLI (Phase 2):**
- 🔄 Fastify REST API server
- 🔄 yargs CLI commands
- 🔄 Daemon lifecycle (PID file, graceful shutdown)
- 🔄 Integration tests

### Planned 📋

**Electron UI (Phase 3):**
- 📋 Menubar tray app
- 📋 React components (Status, Controls, Settings, Logs)
- 📋 Preload script + IPC handlers
- 📋 electron-builder packaging

**Polish & Docs (Phase 4):**
- 📋 Comprehensive README documentation
- 📋 Makefile targets
- 📋 CI workflow
- 📋 Security audit
- 📋 Homebrew formula

---

## Architecture Summary

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
├─────────────────────┬───────────────────────────────────────┤
│   CLI (yargs)       │   Electron UI (optional)              │
│   colima-desktop    │   menubar + main window               │
│   status/start/stop │   React + Vite                        │
│   config/logs/diag  │   contextBridge API                   │
└──────────┬──────────┴────────────────┬──────────────────────┘
           │                           │
           │   HTTP (localhost:35100)  │
           ▼                           ▼
    ┌──────────────────────────────────────────────┐
    │         Daemon (Fastify REST API)            │
    │  /v1/status /v1/lifecycle /v1/config        │
    │  /v1/logs /v1/diagnostics                   │
    └───────────────────┬──────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │  Colima CLI Integration  │
           │  colima start/stop/...   │
           │  lima logs / docker ctx  │
           └─────────────────────────┘
```

### Key Design Decisions

**1. CLI-First Architecture**
- Daemon + CLI work without UI
- Electron UI optional enhancement
- Scriptable automation

**2. No Colima Forking**
- Integration via `colima` CLI only
- No source code modifications
- Respect upstream boundaries

**3. Security-First Electron**
- `contextIsolation` enabled
- `nodeIntegration` disabled
- `sandbox` enabled
- `contextBridge` only interface

**4. Deterministic State**
- All config/logs under `~/.colima-desktop/`
- Atomic writes (corruption prevention)
- No hidden state

**5. Safe Restarts**
- Config changes set `restart_required` flag
- User approval before restart
- No auto-restart

### Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| HTTP Framework | Fastify 4.x | Fast, TypeScript-native |
| CLI Framework | yargs 17.x | Robust arg parsing |
| Build Tool | TypeScript 5.7+ | Type safety |
| Test Runner | vitest 2.x | Fast, ESM-native |
| Config Format | YAML | Human-editable |
| Desktop Framework | Electron 28+ | User requirement |
| UI Framework | React 18 | Matches repo patterns |
| Build Tool (UI) | Vite 5.x | Fast HMR |
| Packaging | electron-builder | Industry standard |

---

## Key Constraints

### Security (Non-Negotiable)

**Daemon:**
- ✅ MUST bind to `localhost` only (never 0.0.0.0)
- ✅ MUST validate all config changes
- ✅ MUST use atomic writes

**Electron:**
- ✅ `contextIsolation` MUST be enabled
- ✅ `nodeIntegration` MUST be disabled
- ✅ `sandbox` MUST be enabled
- ✅ Preload MUST use `contextBridge` only
- ✅ NO raw `ipcRenderer` exposure

**Integration:**
- ✅ MUST use `colima` CLI only (no forking)
- ✅ MUST NOT execute arbitrary commands
- ✅ MUST NOT write outside `~/.colima-desktop/`

### Architecture (Non-Negotiable)

**State Management:**
- ✅ All state MUST live under `~/.colima-desktop/`
- ✅ Config writes MUST be atomic (tmp + rename)
- ✅ Daemon MUST enforce single instance (PID file)

**User Approval:**
- ✅ Config changes MUST set `restart_required` flag
- ✅ MUST NOT auto-restart without user action
- ✅ User MUST explicitly approve resource changes

**CLI-First:**
- ✅ Daemon + CLI MUST work without UI
- ✅ All operations MUST be scriptable
- ✅ Electron UI MUST be optional

### Platform (v1)

- ✅ macOS only (Colima limitation)
- ✅ Node.js >= 18.0.0
- ✅ Colima installed and working

---

## File Locations

| File | Purpose | Location |
|------|---------|----------|
| **Spec Kit** | This directory | `spec/colima-desktop/` |
| **Daemon + CLI** | Core implementation | `tools/colima-desktop/` |
| **Electron UI** | Optional UI | `apps/colima-desktop-ui/` |
| **Config** | User configuration | `~/.colima-desktop/config.yaml` |
| **Logs** | Runtime logs | `~/.colima-desktop/logs/` |
| **Diagnostics** | Debug bundles | `~/.colima-desktop/diagnostics/` |

---

## References

### Internal

- [Daemon + CLI README](../../tools/colima-desktop/README.md)
- [Electron UI README](../../apps/colima-desktop-ui/README.md)
- [Constitution](./constitution.md)
- [Implementation Plan](./plan.md)

### External

- [Colima](https://github.com/abiosoft/colima) - Container runtimes on macOS
- [Spec Kit](https://github.com/github/spec-kit) - Specification-driven development
- [Electron Security](https://www.electronjs.org/docs/latest/tutorial/security) - Best practices
- [Fastify](https://fastify.dev/) - HTTP framework
- [yargs](https://yargs.js.org/) - CLI framework

---

## Contributing to Specs

### Adding Requirements

1. **Update constitution.md** if adding non-negotiable constraints
2. **Update plan.md** if changing architecture or phases
3. **Create prd.md** when extracting feature requirements
4. **Update tasks.md** when breaking down work

### Spec Change Process

1. Propose change in GitHub Discussion
2. Review against existing constraints
3. Update relevant spec file
4. Get review from maintainers
5. Update implementation to match

### Spec Versioning

Specs follow semantic versioning:
- **Major:** Breaking constraint changes
- **Minor:** New phases or features
- **Patch:** Clarifications and fixes

**Current Version:** 1.0 (Initial spec)

---

## Support

**Issues:** [GitHub Issues](https://github.com/Insightpulseai/odoo/issues)
**Discussions:** [GitHub Discussions](https://github.com/Insightpulseai/odoo/discussions)
**Maintainer:** InsightPulse AI

---

**Last Updated:** 2026-02-15
**Spec Version:** 1.0
**Phase:** 2 - Daemon + CLI Core (In Progress)
