# IPAI agent routing guide

## Three agent types in VS Code

| Type | Where it runs | Best for | Worktree isolation |
|---|---|---|---|
| **Local agent** | Your machine, same workspace | Interactive, review-as-you-go | No |
| **Copilot CLI** (background) | Your machine, isolated worktree | Longer tasks, don't need to watch | Yes (automatic) |
| **Cloud agent** | GitHub Actions infrastructure | Async, PR-based, no local machine needed | Yes (GitHub) |

## IPAI task routing

### Local agent
- Reviewing an Odoo module interactively (`odoo-reviewer` agent)
- Quick BIR tax code changes with immediate feedback
- Writing a new `ipai_*` bridge module while you watch
- Debug a specific Odoo traceback with `@terminal:odoo-dev`

```
Chat → Agent (local) → prompt → review inline diffs → accept/reject
```

### Copilot CLI — background worktree (Plan → Continue in Copilot CLI)

Use for any `pulser-odoo` skill with `disable-model-invocation: true`:

| Skill | Plan agent prompt | Hand off to |
|---|---|---|
| `pulser-iac-scaffold` | "Plan the Bicep module layout for a new stamp" | Copilot CLI |
| `pulser-stamp-deploy` | "Plan the stamp-ph-02 promotion with pre-flight gates" | Copilot CLI |
| `pulser-onboarding` | "Plan the TBWA\SMP onboarding wizard steps" | Copilot CLI |
| `pulser-publish` | "Plan the Q1 ERP ops report PPTX structure" | Copilot CLI |
| `pulser-eval` | "Plan the evaluation suite for pulser-ppm" | Copilot CLI |

**Workflow:**
1. Switch to **Plan** agent in session dropdown
2. Enter the planning prompt — agent asks clarifying questions
3. Review the plan — add inline comments
4. Select **Start Implementation → Continue in Copilot CLI**
5. Copilot CLI creates a git worktree, implements in background
6. Your main workspace is free while it runs
7. Review diffs → Apply to main workspace

**Why worktrees matter for IPAI infra work:**
- `pulser-stamp-deploy` modifies Bicep files — a background agent in an isolated worktree means your `main` branch is never in a broken state during deployment planning
- `.worktreeinclude` copies `.env` and `config/secrets.json` automatically

### Cloud agent (Copilot coding agent)

Use for PR-based async work:

| Task | Prompt |
|---|---|
| Go-live readiness PR | "Review the ipai_ppm module against IPAI go-live criteria and open a PR with findings" |
| GA gate assessment | "Run a GA readiness check against the 41 Smart Success Criteria and submit a draft PR" |
| Dependency upgrade PR | "Upgrade all OCA submodules to latest 18.0 releases and open a PR" |
| BIR compliance audit PR | "Audit all ipai_bir_* modules for Odoo 18 breaking changes and open a PR" |

**Workflow:**
```
Chat → Cloud (session type dropdown) → prompt
→ agent creates branch + PR on GitHub
→ review PR in GitHub PR view (or GitHub Pull Requests extension)
→ request changes / approve
```

**Prerequisites for cloud agent:**
- Repo must be published to GitHub
- Enable: `github.copilot.chat.claudeAgent.enabled: true` in VS Code settings
- Requires: Copilot Pro+ or Copilot Enterprise subscription

## Billing — what uses what

| Agent | Billed via | Jake's Max | Copilot Pro+ |
|---|---|---|---|
| Claude Code extension (local) | Anthropic | ✓ primary | not needed |
| Copilot CLI (background) | GitHub Copilot | not needed | ✓ |
| Cloud agent (Copilot coding agent) | GitHub Copilot | not needed | ✓ |
| Claude as cloud agent in Copilot | GitHub Copilot | separate billing | ✓ |

Jake's Max subscription covers the Claude Code extension fully.
Copilot CLI and cloud agents require a separate Copilot Pro+ subscription.
These do not conflict — they are different billing surfaces.

## Skills cross-compatibility (zero duplication)

Per VS Code docs: `.claude/skills/` directories work in **both** Claude Code AND GitHub Copilot.

| Location | Read by |
|---|---|
| `.claude/skills/` | Claude Code ✓, GitHub Copilot ✓ |
| `.github/skills/` | GitHub Copilot ✓ only |
| `plugins/pulser-odoo/skills/` | Claude Code plugin (via marketplace) ✓ only |

**IPAI approach:** `.claude/skills/` is the source of truth. No `.github/skills/` duplication needed — Copilot reads `.claude/skills/` directly.

## Handoff chain for complex IPAI workflows

```
1. Local agent (Plan)     — clarify requirements, ask questions, produce plan
         ↓
2. Copilot CLI            — implement plan in isolated worktree (background)
         ↓
3. Review + adjust        — send follow-up prompts to Copilot CLI session
         ↓
4. Apply to workspace     — merge worktree back, commit
         ↓
5. Cloud agent            — open PR, run async GA gate check, request review
```

This is the complete pattern for `pulser-stamp-deploy` and `pulser-go-live`.
