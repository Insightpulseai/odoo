# Continue+ Implementation Plan

## Scope

Implement the Continue+ spec-kit system with:
1. Spec-kit directory structure and enforcement
2. CI-aware execution (path-based short-circuit + preflight classification)
3. Continue slash commands (`/plan`, `/implement`, `/verify`, `/ship`)
4. CI templates library for OCA/Odoo repos

## Assumptions

- Repository uses GitHub Actions for CI
- OCA CI patterns (pre-commit, Odoo test matrix) are in use
- Continue IDE extension is available
- Claude Code or similar agent is the primary executor

## Files to Change

### Phase 1: Spec-Kit Structure

| File | Action | Purpose |
|------|--------|---------|
| `spec/continue-plus/constitution.md` | CREATE | Invariant rules |
| `spec/continue-plus/prd.md` | CREATE | Product requirements |
| `spec/continue-plus/plan.md` | CREATE | This file |
| `spec/continue-plus/tasks.md` | CREATE | Task checklist |

### Phase 2: Enforcement Tooling

| File | Action | Purpose |
|------|--------|---------|
| `scripts/spec-kit-enforce.py` | CREATE | Validate spec bundles |
| `.github/workflows/spec-kit-enforce.yml` | CREATE | CI workflow for spec validation |
| `.github/workflows/agent-preflight.yml` | CREATE | Diff classification + CI gating |

### Phase 3: Continue Integration

| File | Action | Purpose |
|------|--------|---------|
| `.continue/config.json` | UPDATE | Add custom slash commands |
| `.continue/rules/agentic.md` | CREATE | Agent behavior rules |
| `.continue/prompts/plan.md` | CREATE | /plan command prompt |
| `.continue/prompts/implement.md` | CREATE | /implement command prompt |
| `.continue/prompts/verify.md` | CREATE | /verify command prompt |
| `.continue/prompts/ship.md` | CREATE | /ship command prompt |

### Phase 4: CI Templates

| File | Action | Purpose |
|------|--------|---------|
| `infra/ci/continue-plus/odoo-paths-ignore.yml` | CREATE | OCA-safe path exclusions |
| `infra/ci/continue-plus/preflight-classify.yml` | CREATE | Reusable diff classifier |
| `infra/ci/continue-plus/README.md` | CREATE | Usage instructions |

## Risks / Rollback

| Risk | Mitigation | Rollback |
|------|------------|----------|
| Spec enforcement too strict | Default to WARN, not BLOCK | Remove CI workflow |
| CI gating breaks real tests | Only short-circuit on docs-only | Revert paths-ignore |
| Continue commands conflict | Namespace as `/project:*` | Remove .continue/ |

## Verification Commands

```bash
# Phase 1: Spec structure
ls -la spec/continue-plus/
python scripts/spec-kit-enforce.py spec/continue-plus/

# Phase 2: Enforcement
python scripts/spec-kit-enforce.py --check-all spec/
act -W .github/workflows/spec-kit-enforce.yml  # local CI test

# Phase 3: Continue
# Manual: Open VS Code, run /plan test

# Phase 4: CI templates
yamllint infra/ci/continue-plus/*.yml
```

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.10 | Enforcement scripts |
| PyYAML | ≥6.0 | YAML parsing |
| Continue | latest | IDE integration |
| GitHub Actions | v4 | CI/CD |

## Timeline

This plan does not include time estimates. Implementation order:

1. Spec-kit structure (foundation)
2. Enforcement script (enables CI)
3. CI workflows (automates enforcement)
4. Continue integration (developer UX)
5. CI templates (ecosystem reuse)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEVELOPER IDE                           │
│  Continue + Claude Code                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ /plan   │ │/implement│ │ /verify │ │  /ship  │              │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
└───────┼──────────┼──────────┼──────────┼────────────────────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SPEC-KIT (repo files)                      │
│  spec/<slug>/constitution.md                                    │
│  spec/<slug>/prd.md                                             │
│  spec/<slug>/plan.md     ◄── Planner writes here                │
│  spec/<slug>/tasks.md    ◄── Tasks tracked here                 │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CI PIPELINE                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │spec-kit-     │  │agent-        │  │odoo-tests    │          │
│  │enforce       │  │preflight     │  │(conditional) │          │
│  └──────────────┘  └──────┬───────┘  └──────────────┘          │
│                           │                                      │
│                    ┌──────┴──────┐                               │
│                    │ run_odoo?   │                               │
│                    │ true/false  │                               │
│                    └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

1. All spec bundles pass `spec-kit-enforce.py` validation
2. Docs-only PRs skip Odoo CI matrix
3. `/plan` outputs structured plan to `spec/<slug>/plan.md`
4. `/ship` produces PR-ready description with verification evidence
5. No red PRs from agent infra changes
