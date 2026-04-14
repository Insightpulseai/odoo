# Spec-Kit Extension Evaluation — Wave 01

> **Status:** Evaluation only. No extensions installed yet. Sandbox install requires a dedicated branch.
> **Pinned CLI version:** `v0.6.2` (see [`VERSION`](./VERSION))
> **Owner:** architecture / delivery
> **Date:** 2026-04-14

## Decision matrix

| Extension | Repo | License | Stars | Updated | Author | Verdict | Priority |
|---|---|---|---|---|---|---|---|
| **CI Guard** | `Quratulain-bilal/spec-kit-ci-guard` v1.0.0 | MIT | 0 | 2026-04-10 | community (unverified) | ❌ **BLOCKED-UPSTREAM** — incompatible with v0.6.2 namespacing (see [`trial-results/ci-guard-2026-04-14.md`](./trial-results/ci-guard-2026-04-14.md)) | P2 → defer |
| **Azure DevOps Integration** | `pragya247/spec-kit-azure-devops` v1.0.0 | MIT | 8 | 2026-04-09 | community (unverified) | **Sandbox — risk-flagged** | P3 |
| **MAQA Azure DevOps Integration** | `GenieRobot/spec-kit-maqa-azure-devops` v0.1.0 | MIT | — | (newer) | community (unverified) | **Watch — defer** | P4 |

## Why not install on `main` today

Per `CLAUDE.md` § Engineering Execution Doctrine and the user's explicit step ordering:
> "Do not run `specify init . --force` until overwrite impact is reviewed."

Same caution applies to `specify extension add` — it writes command files into `.claude/commands/` and config under `.specify/extensions/`. The blast radius needs to be reviewed in a sandbox branch first.

---

## Extension 1 — CI Guard (P2, recommended)

### Why it fits

- **Doctrine match:** Reinforces Cross-Repo Invariant #6 ("Specs Required") and `.claude/rules/ssot-platform.md` Rule #9 ("New contracts require a doc + CI validator").
- **Provides:** 5 commands + 2 hooks, only one of which writes files (`/speckit.ci.gate` writes `.speckit-ci.yml`).
- **Read-only by default:** 4 of 5 commands are read-only — low blast radius on first install.

### Coverage matrix (what it adds vs what we already have)

| Capability | Existing in repo | Spec-kit-ci-guard adds |
|---|---|---|
| Spec-bundle existence enforcement | `.github/workflows/spec-kit-enforce.yml` + `scripts/check-spec-kit.sh` | `/speckit.ci.check` (artifact existence + completeness) |
| Spec drift detection | None | `/speckit.ci.drift` (bidirectional) |
| Requirement traceability matrix | None | `/speckit.ci.report` |
| Coverage badge for README | None | `/speckit.ci.badge` |
| Mergeable threshold gates | Workflow-level only | `/speckit.ci.gate` (configurable per-bundle) |

### Risks

- Stars=0, author has no track record.
- Adds another `.claude/commands/` namespace (`speckit.ci.*`); namespace collision unlikely but verify in sandbox.
- `.speckit-ci.yml` becomes a new SSOT file we'd need to govern.
- Drift detection quality depends on prompt engineering; may produce false positives on our 66-bundle backlog.

### Sandbox plan

```bash
# Branch: spec-kit/trial-ci-guard
git checkout -b spec-kit/trial-ci-guard main
specify extension add ci-guard --from https://github.com/Quratulain-bilal/spec-kit-ci-guard/archive/refs/tags/v1.0.0.zip
git status -s   # Inspect overwrite impact
specify extension list
# Run /speckit.ci.check on 3 representative bundles:
#   - spec/pulser-platform/    (large, mature)
#   - spec/agent-platform/     (medium)
#   - spec/document-intelligence/ (newest)
# Capture results in docs/evidence/<stamp>/ci-guard-trial/
```

**Trial gates (must all pass before merge to main):**
1. Zero overwrites of existing `.claude/commands/speckit.*` files.
2. No new dependency on Codex, OpenAI, or any non-Anthropic agent.
3. Drift detection produces <20% false-positive rate on the 3 sample bundles.
4. `.speckit-ci.yml` schema is documentable in `.claude/rules/spec-kit.md`.

---

## Extension 2 — Azure DevOps Integration (P3, sandbox with caveats)

### Why it fits the wave

- **Solves the iteration-assignment gap** flagged in the boards normalization (77 Wave-01 Tasks at root iteration path).
- Bidirectional spec ↔ ADO sync directly addresses the auto-memory vs canonical-truth tension.

### Why it's risk-flagged

- **Conflicts with our authority split.** `ssot/governance/platform-authority-split.yaml` says GitHub Issues = engineering execution backlog; Azure Boards = portfolio. Pushing per-task User Stories into ADO from spec bundles inverts that boundary.
- **Auth model mismatch.** Extension uses Azure CLI OAuth on developer hosts; our doctrine is **Managed Identity + Key Vault** for service-to-service. Per-developer `~/.speckit/ado-config.json` is a developer-experience config, not service auth — acceptable for local sync but never in CI.
- **Duplicates the MCP path we already use.** `mcp__azure-devops__wit_*` MCP tools (already in `.mcp.json`) provide the same write surface with team-approved scope. Adding a second sync path risks divergence.

### Sandbox plan (only if user confirms intent)

```bash
git checkout -b spec-kit/trial-ado-ext main
specify extension add azure-devops --from https://github.com/pragya247/spec-kit-azure-devops/archive/refs/tags/v1.0.0.zip
# Test against ipai-platform with a SINGLE throwaway spec bundle:
#   - Create spec/_speckit-ext-trial/{constitution,prd,plan,tasks}.md
#   - Run /speckit.azure-devops.sync against ipai-platform
#   - Verify created work items go into a "trial" area path, NOT under existing epics
#   - Delete trial work items + branch after evaluation
```

**Trial gates:**
1. Sync targets a dedicated `Area Path = ipai-platform\Trial`, never touches benchmark epics #523/#524/#525.
2. Verify config persists to `~/.speckit/` only — no credential material in repo.
3. Compare with `mcp__azure-devops__wit_create_work_item` flow: which is faster, more controllable, more team-shareable?
4. **Decision:** keep MCP path as canonical, OR adopt extension as developer ergonomics layer. Not both.

---

## Extension 3 — MAQA Azure DevOps (P4, watch)

More sophisticated than `pragya247/spec-kit-azure-devops` (handles Story column moves + real-time Task ticking). Defer until P3 trial outcome decides whether we need any spec-kit→ADO sync at all.

---

## Extensions explicitly REJECTED

| Extension | Reason |
|---|---|
| `spec-kit-canon` | Overlaps SSOT/parity_matrix.yaml authority |
| `spec-kit-confluence` | We don't use Confluence (anti-Microsoft-centric stack) |
| `spec-kit-conduct-ext` | Sub-agent orchestration overlap with Claude Code agent teams |
| `spec-kit-brownfield` | We're past bootstrap — 66 bundles already exist |

---

## Summary

```
Pin Spec Kit version            ✅ DONE   (v0.6.2 — see VERSION)
Trial CI Guard in sandbox       ⏳ PREP'D (branch + gates documented above)
Sandbox ADO extension           ⏳ PREP'D (risk-flagged, awaits confirm)
Run `specify init . --force`    ⛔ HOLD   (until overwrite review complete)
```

## Anchors

- `CLAUDE.md` § Engineering Execution Doctrine
- `.claude/rules/spec-kit.md` (path-scoped spec-kit rules)
- `.claude/rules/ssot-platform.md` Rule #9 (cross-boundary contracts)
- `ssot/governance/platform-authority-split.yaml` (GitHub vs ADO authority)
- `docs/backlog/azdo_normalization_matrix.md` (current ADO state)
