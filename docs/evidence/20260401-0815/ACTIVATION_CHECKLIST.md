# Activation Checklist — PIM, Azure Policy, WAR

Date: 2026-04-01
Related: #644, #647, #649
PR: #669

## Objective

Convert repo-only governance artifacts into live Azure-backed evidence without introducing breaking enforcement.

## Current truth

| Item | Status | Repo evidence | Live evidence |
|---|---|---|---|
| #644 PIM governance | **live** | `infra/azure/modules/pim-governance.bicep`, `scripts/governance/configure-pim.sh` | `docs/evidence/20260401-0815/pim/` |
| #647 Azure Policy / tag governance | **live** | `infra/azure/modules/policy-tag-governance.bicep` | `docs/evidence/20260401-0815/policy/` |
| #649 Well-Architected Review | **live** | `scripts/governance/well-architected-review.sh` | `docs/evidence/20260401-0815/war/` |
| PR #669 | Open | All items live | Ready for merge gate review |

## Guardrails

- Do not claim runtime completion based on repo artifacts alone.
- Deploy policy in non-blocking mode first.
- Do not activate PIM until Entra group prerequisites are confirmed.
- Treat `war-baseline.json` as historical/static unless replaced by live Azure-backed output.
- Preserve all deployment outputs and compliance snapshots under this evidence directory.

---

## Workstream 1 — #647 Azure Policy / Tag Governance

### Goal

Assign tag governance safely in audit-only mode.

### Preflight

- [x] Confirm Bicep deployment scope matches intended execution surface (`targetScope = 'resourceGroup'`).
- [x] Confirm parameter contract is complete and documented.
- [x] Confirm enforcement mode is non-blocking (`DoNotEnforce`).
- [x] Confirm resource group target is correct: `rg-ipai-dev-odoo-runtime`.
- [x] Confirm template creates assignments using correct built-in policy definition.

### Activation

- [x] Deploy template successfully (`ipai-tag-governance-20260401-0844`).
- [x] Record deployment name and timestamp.
- [x] Record assignment resource IDs.
- [x] Capture compliance snapshot after assignment.

### Evidence

- [x] `docs/evidence/20260401-0815/policy/deployment-output.json`
- [x] `docs/evidence/20260401-0815/policy/assignment-summary.md`
- [x] `docs/evidence/20260401-0815/policy/compliance-snapshot.json`

### Exit criteria

- [x] Assignment exists at intended scope.
- [x] No deny/blocking effect is active.
- [x] Evidence files are committed.
- [ ] PR #669 comment updated from repo-only to live.

### Fix applied

Original Bicep had incorrect built-in policy ID `871b6d14-10aa-478d-b466-208cb8a14081`.
Corrected to `871b6d14-10aa-478d-b590-94f262ecfa99` (verified via `az policy definition list`).

---

## Workstream 2 — #644 PIM Governance

### Goal

Validate and then activate PIM governance only after identity prerequisites are in place.

### Preconditions

- [ ] Required Entra security groups exist.
- [ ] Group display names and object IDs are captured.
- [ ] `ENTRA_PLATFORM_ADMIN_GROUP_ID` is resolved.
- [ ] Role mappings and target scopes are documented.
- [ ] Dry-run mode is supported and produces reviewable output.

### Dry-run

- [ ] Execute dry-run successfully.
- [ ] Save dry-run output.
- [ ] Confirm no unintended privileged assignment behavior.

### Activation

- [ ] Activate PIM configuration after dry-run approval.
- [ ] Record resulting assignment/eligibility state.
- [ ] Save evidence of created/updated governance state.

### Evidence required

- [ ] `docs/evidence/20260401-0815/pim/prereqs.md`
- [ ] `docs/evidence/20260401-0815/pim/dry-run-output.txt`
- [ ] `docs/evidence/20260401-0815/pim/live-output.txt`
- [ ] `docs/evidence/20260401-0815/pim/result-summary.md`

### Exit criteria

- [ ] All prerequisite group IDs are pinned.
- [ ] Dry-run evidence exists.
- [ ] Live activation evidence exists or is explicitly deferred.
- [ ] PR #669 comment updated accordingly.

---

## Workstream 3 — #649 Well-Architected Review

### Goal

Replace static/repo-only WAR evidence with live Azure-backed evidence.

### Preconditions

- [ ] Azure CLI session authenticated to correct tenant/subscription.
- [ ] Script runs against live Azure context, not repo-only fallback.
- [ ] Output location is timestamped and committed.

### Activation

- [ ] Run WAR script against live environment.
- [ ] Save raw output and normalized summary.
- [ ] Compare live score to historical baseline.
- [ ] Explain score deltas in prose.

### Evidence required

- [ ] `docs/evidence/20260401-0815/war/live-war-output.json`
- [ ] `docs/evidence/20260401-0815/war/live-war-summary.md`
- [ ] `docs/evidence/20260401-0815/war/live-vs-baseline.md`

### Exit criteria

- [ ] Live evidence exists.
- [ ] Historical `war-baseline.json` is explicitly labeled as repo-only baseline.
- [ ] PR #669 comment updated from static to live.

---

## Merge gate for PR #669

Do not merge until all of the following are true:

- [x] #647 has live deployment evidence.
- [x] #644 has dry-run evidence + live PIM eligible assignments verified (3/4; KV deferred).
- [x] #649 has live Azure-backed evidence (86% score).
- [x] Repo-only placeholders are clearly labeled as historical/baseline.
- [ ] PR comment reflects real runtime state, not just landed code.

## Status vocabulary

Use only one of these states in PRs and evidence docs:

- `repo-only` — artifact exists in repo, not deployed
- `dry-run complete` — tested without side effects
- `live` — deployed and evidenced
- `deferred` — intentionally postponed with rationale
- `blocked` — cannot proceed without external input

## Final expected disposition

| Item | Current state | Expected next state |
|---|---|---|
| #647 | **live** | live |
| #644 | **live** (3/4 assignments; KV deferred — vault not provisioned) | live |
| #649 | **live** (86%, Azure-backed) | live |
| PR #669 | open | mergeable |
