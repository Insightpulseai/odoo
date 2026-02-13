# Implementation Plan: Agent Execution Constraints

> **Branch**: N/A (governance artifact)
> **Spec**: `spec/agent/prd.md`
> **Created**: 2026-02-12

---

## Summary

### Primary Requirements
- FR-001..003: Prevent forbidden operations (Docker, apt, systemctl, sudo)
- FR-004: Capability verification via manifest
- FR-005: CI workflow alternatives
- FR-006: Self-correction on violations

### Technical Approach
Enforcement through three layers: agent self-compliance (constitution), automated CI scanning, and capability manifest validation.

---

## Technical Context

| Attribute | Value |
|-----------|-------|
| **Enforcement Layer 1** | Agent instruction (constitution.md as system context) |
| **Enforcement Layer 2** | CI gate (`.github/workflows/policy-no-cli.yml`) |
| **Enforcement Layer 3** | Capability manifest (`agents/capabilities/manifest.json`) |
| **Target Environment** | Claude Code Web (browser sandbox) |

---

## Constitutional Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| No forbidden ops in Web | PASS | Comprehensive forbidden list in constitution §2 |
| Capability verification | PASS | Manifest-based validation in constitution §5 |
| CI-first architecture | PASS | CI alternatives documented in constitution §6 |

---

## Architecture Decisions

| Decision | Justification | Alternatives Considered |
|----------|---------------|------------------------|
| Constitution as system instruction | Agent reads it as context, self-enforces | Programmatic enforcement (too rigid), post-hoc scanning only (too late) |
| JSON capability manifest | Machine-readable, CI-scannable, version-controlled | YAML (less tooling support), database (overkill) |
| Three-layer enforcement | Defense in depth: agent + CI + manifest | Single layer (insufficient coverage) |

---

## Source Code Layout

```
spec/agent/
├── constitution.md              # Non-negotiable execution constraints
├── prd.md                       # Requirements for agent behavior
├── plan.md                      # This file
└── tasks.md                     # Task breakdown

agents/capabilities/
└── manifest.json                # Verified capability registry

.github/workflows/
└── policy-no-cli.yml            # CI enforcement gate
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent ignores constitution | High | CI scanner catches forbidden patterns in output |
| Manifest out of date | Medium | Review manifest quarterly; CI warns on unverified claims |
| Overly restrictive constraints | Medium | Amendment process in constitution §11 |

---

## Verification Commands

```bash
./scripts/check-spec-kit.sh
# Validates spec bundle completeness

python3 -c "import json; m=json.load(open('agents/capabilities/manifest.json')); print(f'{len(m[\"capabilities\"])} capabilities verified')"
# Validates manifest structure
```

---

## Handoff

- **Next**: `tasks.md` for task breakdown
- **Status**: Plan ratified — this is a governance artifact, not a code feature
