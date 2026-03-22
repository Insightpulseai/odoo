# VS Code + Claude Code Compatibility Model

> **Status**: Approved
> **Date**: 2026-03-22

---

## Rule

```
Org parent directory = agent orchestration root
Repo root = code / CI / PR authority boundary
Cross-repo work resolves into explicit per-repo changes and PRs
No nested duplicate repo roots
```

## Two-Level Authority Model

```
Insightpulseai/          ← orchestration root (Claude Code, Codex, discovery)
  odoo/                  ← repo authority (code, CI, PRs)
  data-intelligence/     ← repo authority
  platform/              ← repo authority
  infra/                 ← repo authority
  web/                   ← repo authority
  agents/                ← repo authority
  ...
```

### Org root is allowed

The sibling-repo parent directory is valid for:
- Claude Code / Codex orchestration
- repo discovery
- cross-repo refactors
- multi-repo PR planning

### Repo root is the authority boundary

Even when the agent starts at the org root:
- edits are evaluated **per repo**
- CI runs **per repo**
- PRs are opened **per repo**
- `.vscode/`, tests, specs, and workflows stay **repo-local**

## What is NOT allowed

- Nested duplicate paths (`odoo/odoo/odoo/...`)
- Recursive workspace discovery
- Duplicate repo roots under other repo roots
- One PR spanning multiple repos implicitly
- Hidden edits across repos without explicit per-repo diff
- Treating one big workspace as a merge/deploy authority

## VS Code Model

### Standardize with a profile, not a workspace file

One shared profile: **InsightPulseAI Platform Engineering**

The profile carries:
- extension allowlist
- UI/editor defaults
- Azure/Databricks/dev tooling defaults

### Repo-local `.vscode/` for per-repo behavior

Each repo gets only:

```
.vscode/settings.json
.vscode/extensions.json
.vscode/tasks.json        # only if justified
.vscode/launch.json       # only if justified
```

### Human VS Code usage

Open either:
- the **org parent directory** for broad multi-repo work
- the **exact repo root** for focused single-repo work

Both are valid. The repo root is still the authority boundary.

## Databricks Project Selection

Open the right root for the right work:

| Work | Open |
|------|------|
| Databricks analytics | `data-intelligence/` |
| Substrate/IaC | `infra/` |
| ERP/runtime | `odoo/` |
| Agent development | `agents/` |

Inside VS Code Databricks extension, select the specific bundle root:
- `databricks/bundles/foundation_python`
- `databricks/bundles/lakeflow_ingestion`
- `databricks/bundles/sql_warehouse`
- `infra/databricks` (substrate only)

## Optional at org root

```
Insightpulseai/.claude/       ← shared agent memory/config
Insightpulseai/docs/          ← cross-repo architecture docs
Insightpulseai/scripts/       ← cross-repo automation
```

Do not centralize repo-specific CI/editor behavior at org root unless truly shared.

## Compatibility Test

```
Cross-repo work must resolve into explicit per-repo diffs and PRs.
If a change touches two repos, it produces two PRs.
```
