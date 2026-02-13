# Spec Kit — Spec-Driven Development

> Integrated from [github/spec-kit](https://github.com/github/spec-kit).
> Specifications are executable — they generate implementations, not just describe them.

## Quick Start

### 1. Create a new spec bundle

```bash
./scripts/speckit-scaffold.sh my-feature-slug
```

Or use the slash command:
```
/speckit.constitution my-feature-slug
```

### 2. Follow the workflow

```
/speckit.constitution → /speckit.specify → /speckit.clarify (optional)
    → /speckit.plan → /speckit.tasks → /speckit.analyze
    → /speckit.checklist → /speckit.implement
```

### 3. Validate

```bash
./scripts/check-spec-kit.sh
```

## Directory Structure

```
.specify/
├── README.md              # This file
├── memory/                # Spec-kit state and context (session persistence)
├── scripts/               # Helper scripts for spec-kit workflow
│   ├── common.sh          # Shared functions (get_repo_root, get_feature_paths, etc.)
│   ├── check-prerequisites.sh  # Validate prerequisites for each workflow phase
│   ├── create-new-feature.sh   # Create new spec bundle from templates
│   └── setup-plan.sh           # Initialize plan.md from template
└── templates/             # Scaffolding templates for spec artifacts
    ├── constitution-template.md
    ├── spec-template.md        # Generates prd.md
    ├── plan-template.md
    ├── tasks-template.md
    └── checklist-template.md
```

## Slash Commands

All commands are registered in `.claude/settings.json` and `.claude/settings.web.json`.

| Command | Purpose | Artifacts Produced |
|---------|---------|-------------------|
| `/speckit.constitution` | Governance principles | `constitution.md` |
| `/speckit.specify` | Product requirements | `prd.md` |
| `/speckit.clarify` | Resolve ambiguities | Updates `prd.md` |
| `/speckit.plan` | Implementation architecture | `plan.md`, `research.md` |
| `/speckit.tasks` | Task breakdown | `tasks.md` |
| `/speckit.analyze` | Consistency check (read-only) | Report only |
| `/speckit.checklist` | Quality validation | `checklist.md` |
| `/speckit.implement` | Execute implementation | Source code |

## Spec Bundle Structure

Each feature gets a bundle under `spec/<feature-slug>/`:

```
spec/<feature-slug>/
├── constitution.md   # Non-negotiable rules (REQUIRED)
├── prd.md            # Product requirements (REQUIRED)
├── plan.md           # Implementation plan (REQUIRED)
├── tasks.md          # Task breakdown (REQUIRED)
├── checklist.md      # Quality validation (optional)
└── research.md       # Unknowns resolved (optional)
```

**Required files**: constitution.md, prd.md, plan.md, tasks.md
**CI enforces**: All 4 required files must exist with >10 non-empty lines each.

## Conventions

### This repo vs upstream spec-kit

| Aspect | This repo | Upstream spec-kit |
|--------|-----------|-------------------|
| Bundle directory | `spec/` | `specs/` |
| Requirements file | `prd.md` | `spec.md` |
| Feature naming | `lowercase-hyphen` | `NNN-feature-name` |
| Module naming | `ipai_<domain>_<feature>` | N/A |
| Branch naming | `feature/<slug>` or `claude/<slug>` | `NNN-feature-name` |

### Validation accepts both

The CI gate and `check-spec-kit.sh` accept either `prd.md` or `spec.md` as the requirements file, for compatibility with both conventions.

## Integration Points

- **CLAUDE.md**: References spec-kit section with workflow and file table
- **CI**: `.github/workflows/spec-kit-enforce.yml` validates bundles on PR/push
- **Pre-commit**: `validate-spec-kit` hook runs on `spec/` changes
- **Agent memory**: `.claude/project_memory.db` stores spec context across sessions
