# Vercel Previews — ops-console

> **Previews are the primary UI review surface for all `apps/ops-console` changes.**
> Every PR/branch automatically gets a fully-functional preview URL.

---

## What Previews are

Vercel **Preview** is a deployment environment created automatically when you:

- Push to any **non-production branch**
- Open or update a **pull request**
- Run `vercel deploy` from the CLI (without `--prod`)

Each preview produces a **unique, stable URL** you can share, inspect, and comment on.

---

## Preview Deployment Triggers

| Action | Preview created? | URL pattern |
|--------|-----------------|-------------|
| Push to any branch (not `main`) | ✅ Yes | `<app>-git-<branch>-<team>.vercel.app` |
| Open / update a PR | ✅ Yes | Same stable URL per branch |
| `vercel deploy` (no `--prod`) | ✅ Yes | Ephemeral URL, logged in CLI output |
| Merge to `main` | ❌ No (goes to Production) | `<app>.vercel.app` / custom domain |

---

## Vercel for GitHub — PR Status + Links

With **Vercel for GitHub** installed, every PR receives:

- A **deployment status check** on the PR ("Vercel — Preview deployment successful")
- **"Visit Preview"** and **"Inspect"** links in the PR checks panel
- Automatic re-deployment on every subsequent push to the PR branch

No CLI or manual action needed — push and the status appears automatically.

---

## Preview Comments (Vercel Toolbar)

The **Vercel Toolbar** is injected into every Preview deployment and allows reviewers to:

- Place **inline comments** directly on specific UI elements
- Attach comments to a URL + viewport
- Resolve threads from within the toolbar or the Vercel dashboard

**Availability**: Comments are available on all Vercel plans for Preview deployments.

### How to use

1. Open the Preview URL in a browser.
2. Click the **Vercel Toolbar** at the bottom of the page (appears automatically on Preview URLs).
3. Click any element on the page to add a comment.
4. Teammates see comments in the Vercel dashboard and via email/Slack (if configured).

**PR merge requirement**: All open Preview comments must be resolved before merge.
Add `- [ ] All Preview comments resolved` to your PR description checklist.

---

## Monorepo Contract

### One Vercel Project per deployable

| App | Vercel Project | Root Directory |
|-----|---------------|----------------|
| `apps/ops-console` | `odooops-console` | `apps/ops-console` |

New apps follow the same pattern: register in Vercel with the app's directory as Root Directory.
See `docs/ops/VERCEL_MONOREPO.md` for workspace registration and skip-unaffected setup.

### How build skipping works on Previews

Preview builds also respect the `ignoreCommand` in `vercel.json`. The skip logic:

```bash
git diff --name-only "$VERCEL_GIT_PREVIOUS_SHA" "$VERCEL_GIT_COMMIT_SHA" \
  | grep -qE "^apps/ops-console/" && exit 1 || exit 0
```

- `exit 0` → Vercel skips the build (no relevant change)
- `exit 1` → Vercel runs the build

This means pushing a change to `addons/` will **not** trigger a Preview build for `ops-console`.

---

## Preview Environment Variables

Previews use the **Preview** environment in Vercel (separate from Production).

- Secrets sync from Supabase follows the same contract as Production (see `SUPABASE_VERCEL.md`).
- Add preview-specific overrides in Vercel → Project Settings → Environment Variables → Preview.
- Stub or sandbox API keys are appropriate for Preview; use `NEXT_PUBLIC_*` for client-visible vars.

---

## Reviewer Workflow (UI changes)

1. **Author**: push branch → copy Preview URL from PR checks panel → paste into PR description.
2. **Reviewer**: open Preview URL → use Vercel Toolbar to leave inline comments.
3. **Author**: address comments → push fix → Preview auto-redeploys → resolve threads.
4. **Merge**: all comments resolved + all CI gates green.

This workflow is documented in `docs/design/DESIGN_ENGINEERING_WORKFLOW.md §6`.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `docs/ops/VERCEL_MONOREPO.md` | Workspace registration, skip-unaffected, env vars |
| `docs/ops/VERCEL_DOCS_SSOT.md` | Canonical Vercel docs URLs (MCP, monorepos, AI Gateway) |
| `docs/ops/SUPABASE_VERCEL.md` | Env var sync contract |
| `docs/design/DESIGN_ENGINEERING_WORKFLOW.md` | PR requirements for UI changes |
| `docs/platform/GOLDEN_PATH.md` | Full release lane contract |
