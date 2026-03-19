# IMPLEMNTATION NOTE - KB Skills Addition

**Date**: 2026-02-15
**Task**: Add KB-based module validation + skill generation procedures

## Changes

1.  **Skills**:
    - `agents/skills/validate-odoo-module-against-kb/SKILL.md`: Validates modules against pinned KB.
    - `agents/skills/generate-odoo-skill-from-kb/SKILL.md`: Generates skills from pinned KB.

2.  **Registry**:
    - Updated `agents/registry/odoo_skills.yaml` with new entries.
    - Added guardrails and evidence paths.

3.  **Verification**:
    - Updated `tests/test_skill_registry.py`.
    - Verified registration via tests.

## Purpose

These skills enable the "Cloudpepper-grade" workflow where all development actions are:

1.  Grounded in a specific, pinned version of the Odoo documentation.
2.  Verified for compliance with that documentation without expensive model calls.
3.  Capable of bootstrapping new capabilities (skills) from that same documentation in a deterministic way.
