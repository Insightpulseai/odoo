# Feature: Agent Execution Constraints

> **Created**: 2026-02-12
> **Status**: Ratified
> **Author**: InsightPulse AI

---

## Overview

Define the execution constraints and behavioral rules for Claude Code agents operating in the InsightPulse AI Odoo repository. Agents must operate within the capabilities of their execution environment (Web or CLI) without proposing forbidden operations.

## Problem Alignment

### Problem Statement

AI agents operating in browser-based environments (Claude Code Web) attempt operations that are architecturally impossible (Docker, apt, systemctl, sudo), causing failed commands, user confusion, and wasted time.

### Current State

Without explicit constraints, agents hallucinate capabilities they don't have, propose forbidden commands, and fail silently or noisily. Users lose trust when agents propose operations that can never succeed.

---

## User Scenarios

### P1 (Must Have)

#### US1: Agent respects environment constraints

**As a** developer using Claude Code Web, **I want** the agent to never propose Docker/apt/systemctl commands, **so that** I don't waste time on operations that will always fail.

**Acceptance Criteria**:
- Given a Web environment, When agent is asked to "run docker-compose up", Then agent explains the constraint and offers CI workflow alternative
- Given a Web environment, When agent encounters a task requiring apt-get, Then agent generates a GitHub Actions workflow instead

#### US2: Agent verifies capabilities before claiming them

**As a** developer, **I want** the agent to check the capability manifest before claiming it can do something, **so that** I receive accurate information about what's possible.

**Acceptance Criteria**:
- Given a capability not in manifest.json, When agent is asked about it, Then agent refuses to claim the capability
- Given a verified capability, When agent uses it, Then the operation succeeds

### P2 (Should Have)

#### US3: Agent self-corrects on constraint violations

**As a** developer, **I want** the agent to immediately self-correct if it accidentally proposes a forbidden operation, **so that** errors are caught and fixed in the same conversation.

**Acceptance Criteria**:
- Given an accidental forbidden proposal, When agent realizes the mistake, Then agent immediately corrects with the right approach

---

## Functional Requirements

| ID | Requirement | Priority | Story |
|----|-------------|----------|-------|
| FR-001 | Agent MUST NOT propose Docker/container operations in Web environment | P1 | US1 |
| FR-002 | Agent MUST NOT propose apt/brew/system package operations in Web environment | P1 | US1 |
| FR-003 | Agent MUST NOT propose systemctl/sudo operations in Web environment | P1 | US1 |
| FR-004 | Agent MUST check capability manifest before claiming capabilities | P1 | US2 |
| FR-005 | Agent MUST offer CI workflow alternatives for forbidden operations | P1 | US1 |
| FR-006 | Agent MUST self-correct immediately on constraint violations | P2 | US3 |

---

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Reliability | Agent constraint compliance must be 100% (zero tolerance for forbidden ops) |
| NFR-002 | Transparency | Agent must explain WHY an operation is forbidden when declining |
| NFR-003 | Usability | Alternative suggestions must be actionable (not just "you should...") |

---

## Success Criteria

| ID | Criterion | Measurement |
|----|-----------|-------------|
| SC-001 | Zero forbidden operations proposed in Web sessions | Count of Docker/apt/systemctl proposals = 0 |
| SC-002 | All capability claims backed by manifest evidence | Unverified claims = 0 |
| SC-003 | Every forbidden operation has an alternative offered | Alternative coverage = 100% |

---

## Edge Cases & Error Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| User explicitly asks to run Docker | Agent explains constraint, offers Dockerfile + CI workflow |
| Capability manifest file is missing | Agent refuses all capability claims, reports missing file |
| User insists on forbidden operation | Agent maintains refusal, explains architectural impossibility |
| New capability added but manifest not updated | Agent refuses until manifest is updated |
