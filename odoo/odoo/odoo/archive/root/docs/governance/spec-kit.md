# Spec Kit Policy

**Version pin SSOT**: `ssot/tooling/spec-kit.yaml`
**Refresh runbook**: `docs/runbooks/spec-kit-refresh.md`
**CI enforcement**: `.github/workflows/spec-kit-drift.yml`

---

## Rule 1 — Spec bundles are authored SSOT

`spec/<slug>/` directories are **hand-authored source of truth**. They are never
regenerated or overwritten by the `specify` CLI.

- `constitution.md`, `prd.md`, `plan.md`, `tasks.md` etc. are written by contributors.
- The `specify` CLI does not touch `spec/` at all.
- Any automated tooling that modifies `spec/<slug>/` files must be treated as a bug.

## Rule 2 — Templates are vendored; refresh only via the blessed command

The following paths are **vendored from the `specify` CLI** and must only change
via the blessed refresh workflow:

```
.specify/templates/
.specify/scripts/
.claude/commands/speckit.*.md
```

**Editing these paths directly outside a `chore/spec-kit-refresh-*` PR is prohibited.**
The CI drift gate (`spec-kit-drift.yml`) will fail if they drift from the pinned version.

Blessed refresh command:
```bash
npx specify@<pinned_version> init --here --force --ignore-agent-tools
```

Where `<pinned_version>` is the value in `ssot/tooling/spec-kit.yaml#spec_kit.cli.version`.

## Rule 3 — Version bumps require a dedicated `chore/spec-kit-refresh` PR

To upgrade the pinned CLI version:

1. Update `ssot/tooling/spec-kit.yaml` with the new version.
2. Run the refresh command (see Rule 2).
3. Open a PR on a branch named `chore/spec-kit-refresh-<version>` with the label
   `chore/spec-kit-refresh`.
4. CI must pass (`spec-kit-drift` + `all-green-gates`) before merge.

Do not bundle template refreshes with feature PRs.

---

## Rationale

The `specify` CLI scaffolds reusable spec templates (constitution, PRD, plan, tasks).
Pinning the version and drift-checking ensures all contributors use the same template
structure, preventing divergence that would break spec-driven development workflows.

Keeping `spec/<slug>/` bundles immutable by the CLI preserves the authored intent of
each feature specification.
