# Constitution: GitHub Well-Architected Assessment System

## Core Principles

1. **Reuse Over Reinvent**: Leverage `lib.py`, existing patterns, and tools.
2. **Fail Fast**: Critical violations block PRs immediately (local checks).
3. **Evidence-Based**: All assessments produce timestamped JSON evidence.
4. **Automation-First**: Zero manual steps for assessment.

## Non-Negotiables

- **PR Gate Speed**: Must complete in < 5 minutes.
- **Critical Checks**:
  - Branch protection enabled (P4).
  - Secrets scanning enabled (P3).
  - SSOT generators exist and are deterministic (P5).
- **Scoring**: Must use 0-4 maturity scale (0=Missing, 2=Defined/Managed, 4=Optimized).

## Integration Standards

- Must run on Ubuntu-latest runners.
- Must not require Docker for local checks (unless wrapper script handles it transparently).
- Must output standard JSON evidence to `docs/evidence/`.
