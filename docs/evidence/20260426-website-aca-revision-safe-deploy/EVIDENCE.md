# Evidence — ACA revision-safe website deployment (B-prime)

- **Timestamp**: 2026-04-26 (UTC+8)
- **Branch**: `chore/pipeline-aca-revision-safe-deploy`
- **PR title**: `chore(deploy): add ACA revision-safe website deployment flow`
- **Repo**: `Insightpulseai/odoo`
- **Base**: `main` (post-#807 + post-#808 merges)

## Goal

Add staging-style revision support to the public-website deploy
pipeline so a flat-cutover deploy directly to the only live ACA
becomes avoidable risk.

## Prior state

| PR | Title | Status | Effect |
|---|---|---|---|
| #807 | Scope A — trust pages + SEO/LLM artifacts | merged | New /security, /subprocessors, /llms.txt, /sitemap.xml, /robots.txt, /features redirect on `main`. **Not yet deployed.** |
| #808 | Pipeline drift fix (`containerAppName`, `resourceGroup`) | merged | Pipeline targets the live ACA. **No deploy run yet.** |

The next deploy after #808 would have been a flat 100% cutover of
Scope A onto production. This PR replaces that with revision-safe
deploy.

## What this PR changes

| File | Change |
|---|---|
| `azure-pipelines/web-landing-deploy.yml` | REPLACED with revision-safe pipeline (Build → Deploy @ 0% → Smoke revision FQDN → ManualValidation gate → ShiftTraffic → Smoke prod → Evidence). 7 stages instead of 4. |
| `docs/deployment/ACA_REVISION_SAFE_DEPLOY.md` | NEW — explains flow, rollback procedures (Scenarios A/B/C), authority split per ADR-0010. |
| `docs/evidence/20260426-website-aca-revision-safe-deploy/EVIDENCE.md` | NEW (this file). |

The shared `templates/jobs/deploy-containerapp.yml` template is **NOT**
modified — it remains available for other pipelines that want
flat-deploy semantics. Web-landing now uses inline `az containerapp`
calls within `web-landing-deploy.yml`.

## Pipeline stage map

```
Build (template)
  ↓
Deploy
  ├─ az containerapp revision set-mode --mode multiple   (idempotent)
  ├─ az containerapp update --revision-suffix build-<id>  (creates revision)
  └─ az containerapp ingress traffic set                  (defensive: prev=100, new=0)
       outputs: newRevisionName, newRevisionFqdn, previousRevisionName
  ↓
SmokeNewRevision
  └─ curl https://<newRevisionFqdn>/ , /security, /subprocessors,
       /llms.txt, /sitemap.xml, /robots.txt, /features
  ↓
PromoteApproval
  └─ ManualValidation@0  (timeout 72h, default reject on timeout)
  ↓
PromoteShiftTraffic
  └─ az containerapp ingress traffic set --revision-weight <new>=100
  ↓
SmokeProduction
  └─ curl https://www.insightpulseai.com/  (HTTP 200 + content match)
  ↓
Evidence (template, dependsOn all)
```

## Scope guarantee

- 🚫 **No deployment triggered by this PR.** The pipeline trigger is
  `paths.include: web/ipai-landing/**`. This PR changes
  `azure-pipelines/**` and `docs/**`; neither is under that path. So
  merging this PR does not auto-run the deploy pipeline.
- 🚫 No Azure mutation in this PR (no ACA / RG / image / DNS changes).
- 🚫 No website content changes.
- 🚫 No secrets added.
- 🚫 No DNS / Front Door changes.
- 🚫 No environment created or deleted in Azure DevOps (the
  `ManualValidation@0` task does NOT require a deployment environment;
  it runs inline on `pool: server`).
- 🚫 No touching `Odoo`, `agent-platform`, `infra`,
  `marketplace-publishing`, or `docs` repos in the canonical
  `Insightpulse-ai` org. Changes are confined to the legacy
  `Insightpulseai/odoo` monorepo at `azure-pipelines/**` and `docs/**`.

## What is required to actually update the live site

After this PR merges:

1. Manually queue the pipeline (Azure DevOps UI or
   `az pipelines run --name web-landing-deploy --branch main`). The
   pipeline does not auto-trigger on this PR's merge because of the
   path filter.
2. The pipeline will:
   - Build a new image containing Scope A.
   - Deploy a new revision at 0% traffic.
   - Smoke the new revision FQDN.
   - Pause at ManualValidation.
3. A reviewer with Azure DevOps approval permission clicks Approve.
4. The pipeline shifts 100% traffic to the new revision, smokes
   production, and publishes evidence.

That deploy is **separately gated** — it requires explicit go-ahead and
manual approval at the ManualValidation step. This PR alone does not
trigger any of it.

## Verification of pipeline correctness (without running)

YAML parses cleanly:

```bash
python3 -c "import yaml; yaml.safe_load(open('azure-pipelines/web-landing-deploy.yml'))"
```

Stage dependencies are well-formed (each `dependsOn` references an
earlier-defined stage).

`stageDependencies` references for cross-stage variables use the
correct path: `Deploy.DeployRevision.outputs['deployRev.<varName>']`
where `Deploy` is the stage, `DeployRevision` is the job, `deployRev`
is the step name (`name: deployRev`), and `<varName>` is the variable
emitted by `##vso[task.setvariable variable=<varName>;isOutput=true]`.

## Confirmations

- [x] No deployment triggered.
- [x] No Azure mutation.
- [x] No GitHub environment / Azure DevOps environment created or deleted.
- [x] No DNS / Azure Front Door change.
- [x] No secrets added or moved.
- [x] No website content changed (Scope A content remains exactly as
      merged in PR #807).
- [x] Existing shared template `templates/jobs/deploy-containerapp.yml`
      not modified; other pipelines that depend on it are unaffected.
- [x] Pipeline trigger paths preserved (`web/ipai-landing/**`); this
      PR's diff does not auto-run the pipeline.

## Rollback (this PR itself)

Single-commit revert. Reverting restores the previous flat-deploy
behavior. No Azure mutation occurred between this PR's merge and the
revert, so there is no Azure-side cleanup needed.
