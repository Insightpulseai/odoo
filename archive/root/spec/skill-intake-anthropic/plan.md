# Plan: Intake Pipeline for Upstream Anthropic Skills

## Overview

Build a controlled intake pipeline that mirrors upstream skills from `anthropics/skills`, converts them to the local `agents/skills/` format, and enforces quality gates via CI.

## Phase 1 — Mirror Setup

- Add `third_party/anthropic_skills/` as a snapshot directory (not a submodule).
- Create `scripts/agents/sync_upstream_skills.sh` to fetch and update the snapshot.
- Generate an index file (`third_party/anthropic_skills/index.json`) listing available skills with metadata.
- Schedule weekly sync via GitHub Actions workflow.

## Phase 2 — Converter Template

- Create `scripts/agents/convert_skill.py` to transform upstream skill format to local format.
- Map upstream skill metadata to local taxonomy (`agents/skills/<name>/metadata.yaml`).
- Generate JSON Schema stubs for inputs and outputs from upstream examples.
- Produce skeleton test harness for each converted skill.

## Phase 3 — Quality Gates

- CI workflow: `.github/workflows/skill-intake-gate.yml`.
- Gate 1: `metadata.yaml` must exist with required fields (name, category, version, author).
- Gate 2: `io_schema.json` must be valid JSON Schema for inputs and outputs.
- Gate 3: No embedded secrets (scan for patterns: API keys, tokens, passwords).
- Gate 4: Test harness must exist and pass in sandbox mode.

## Phase 4 — First Skill Port

- Select one upstream skill with clear IO contract.
- Run full conversion pipeline.
- Validate all gates pass.
- Document the porting process in `docs/agents/SKILL_PORTING_GUIDE.md`.

## Dependencies

- Access to `https://github.com/anthropics/skills` (public repo).
- Python 3.12+ for converter script.
- GitHub Actions for CI gates and weekly sync.
