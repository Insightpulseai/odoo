# Runbook — GitHub Correct Setup Sequence for IPAI

Canonical source: [`ssot/governance/github-feature-leverage-matrix.yaml`](../../ssot/governance/github-feature-leverage-matrix.yaml) — `prioritized_adoption_ladder`.

## Metadata

- **Owner**: platform-architecture
- **Last updated**: 2026-04-19
- **Scope**: operational sequence for IPAI's GitHub Enterprise Cloud setup, deadline-aware
- **Preconditions**: enterprise `ipai` + primary org `Insightpulse-ai` exist, GHAS trial active, 145 commits queued locally
- **Evidence root**: `docs/evidence/<YYYYMMDD-HHMM>/github-setup/`

## Deadline watch

| Deadline | Item | Days out |
|---|---|---|
| 2026-04-24 | Copilot training opt-out (default opt-in otherwise) | 5 |
| 2026-05-19 (approx) | GHAS trial expiry — adoption decision required | 30 |

## Sequence

Execute in order. Each block gates the next.

---

### Block 1 — Unblock the push (secret rotation + history rewrite)

> [!CAUTION]
> Destructive git operation. 145 commit SHAs will be rewritten. Collaborators must re-clone.

- [ ] Rotate the compromised Google OAuth client secret
  - Google Cloud Console → Credentials → W9 Studio OAuth client (ID `916601142061-...`) → regenerate secret
  - Revoke old secret immediately
- [ ] Replace old secret in git history with `filter-repo`

```bash
# Install filter-repo if not present
brew install git-filter-repo

# Capture the leaked literal (from commit 9b6b09c35:platform/ssot/identity/google-oauth.yaml:19)
# Replace in history
git filter-repo --replace-text <(echo 'GOCSPX-<old-leaked-value>==>REDACTED_ROTATED')

# Verify the leaked value no longer appears
git log --all -p -S 'GOCSPX-' | head
```

- [ ] Force-push rewritten history

```bash
git push --force-with-lease origin main
```

- [ ] Notify any collaborators to re-clone
- [ ] Evidence: `docs/evidence/<ts>/github-setup/01-secret-rotation/`

---

### Block 2 — Copilot training data opt-out (deadline 2026-04-24)

- [ ] Each engineering user: Account → Settings → Copilot → "Allow GitHub to use my code snippets for product improvement" → **OFF**
- [ ] Enterprise owner (you): `https://github.com/enterprises/ipai/settings/copilot/policies` → set tenant-level Copilot data policy → **opt out**
- [ ] Update [`ssot/governance/claude-code-activation-matrix.yaml`](../../ssot/governance/claude-code-activation-matrix.yaml) and [`ssot/governance/vscode-operating-profile.yaml`](../../ssot/governance/vscode-operating-profile.yaml) with opt-out posture
- [ ] Evidence: `docs/evidence/<ts>/github-setup/02-copilot-optout/` (screenshot of toggle)

---

### Block 3 — GHAS trial: confirm CodeQL coverage before expiry

- [ ] Inventory tier_0 repos per [`repo-classes.yaml`](../../ssot/governance/repo-classes.yaml): `odoo`, `platform`, `agent-platform`, `infra`
- [ ] Enable CodeQL on each tier_0 repo if not already on

```bash
gh api -X PUT /repos/Insightpulse-ai/<repo>/code-scanning/default-setup \
  --field 'state=configured' \
  --field 'query_suite=extended' \
  --field 'languages[]=python' \
  --field 'languages[]=javascript'
```

- [ ] Confirm first scan completes on each repo (`gh api /repos/.../code-scanning/alerts`)
- [ ] Decision before 2026-05-19: adopt commercial GHAS (billing via Azure subscription) vs fall back to Defender for DevOps
- [ ] Update [`github-enterprise-current-state-snapshot.yaml`](../../ssot/governance/github-enterprise-current-state-snapshot.yaml) with the decision
- [ ] Evidence: `docs/evidence/<ts>/github-setup/03-codeql/`

---

### Block 4 — Identity: SAML SSO vs EMU decision + SCIM

> Decision gate. Read [`github-identity-and-oauth.yaml`](../../ssot/governance/github-identity-and-oauth.yaml) first.

- [ ] Decide: **SAML SSO** (standard, keeps existing GitHub usernames) or **EMU** (Enterprise Managed Users — full Entra-managed identities, stronger posture but breaks personal accounts)
  - Recommendation: SAML SSO for now; evaluate EMU migration after first customer
- [ ] Provision Entra SAML app for GitHub Enterprise
  - Entra admin center → Enterprise applications → New application → "GitHub Enterprise Cloud"
  - Configure SSO with enterprise `ipai`
  - Upload SAML metadata to GitHub Enterprise → Settings → Authentication security
- [ ] Create SCIM authorizing service account `svc-github-scim` (org owner role, no human personal account)
- [ ] Approve `okta_scim_integration` OAuth app only if choosing Okta; skip for Entra
- [ ] Enable SCIM in Entra → upload SCIM secret from GitHub
- [ ] Verify user provisioning sync completes
- [ ] Evidence: `docs/evidence/<ts>/github-setup/04-identity/`

---

### Block 5 — Team sync Entra → GitHub

- [ ] After Block 4 SCIM is live, enable team sync

```bash
gh api -X PATCH /orgs/Insightpulse-ai/team-sync/groups \
  --field groups='[{"group_id":"<entra-group-id>","group_name":"platform-architecture"}]'
```

- [ ] Create initial Entra security groups mirroring IPAI teams: `platform-architecture`, `finance-ops`, `data-intelligence`, `agent-platform`, `web`, `design`
- [ ] Map each Entra group → GitHub team with same slug
- [ ] Replace direct repo-level user grants with team-based access per [`github-target-state-success-criteria.yaml`](../../ssot/governance/github-target-state-success-criteria.yaml#category_1_organization_and_access) AC-2
- [ ] Evidence: `docs/evidence/<ts>/github-setup/05-team-sync/`

---

### Block 6 — Provision Foundry project (go-live blocker)

- [ ] Create `rg-ipai-dev-ai-sea` Foundry project (RG already exists)

```bash
az cognitiveservices account create \
  -n ipai-copilot-resource \
  -g rg-ipai-dev-ai-sea \
  --kind AIFoundry \
  --sku S0 \
  --location southeastasia \
  --custom-domain ipai-copilot-resource \
  --assign-identity
```

- [ ] Deploy gpt-4.1 model to the project (start at 30K TPM, scale from observed usage)

```bash
az cognitiveservices account deployment create \
  -n ipai-copilot-resource \
  -g rg-ipai-dev-ai-sea \
  --deployment-name gpt-4-1-default \
  --model-name gpt-4.1 \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 30
```

- [ ] Grant agent-platform managed identity access to the project
- [ ] Update [`platform/ssot/ai/foundry-resource-model.yaml`](../../platform/ssot/ai/foundry-resource-model.yaml) `current_state: NOT_YET_PROVISIONED` → `provisioned`
- [ ] Register agent-platform agents into the project
- [ ] Evidence: `docs/evidence/<ts>/github-setup/06-foundry/`

---

### Block 7 — Copilot Enterprise enrollment

- [ ] Enterprise owner → Settings → Copilot → Access → **Enabled** for all engineering members
- [ ] Verify Foundry routing: Copilot → Model settings → confirm default model family (aligns with [`foundry-resource-model.yaml`](../../platform/ssot/ai/foundry-resource-model.yaml))
- [ ] Enable Copilot Autofix for tier_0 + tier_1 repos
- [ ] Enable Copilot secret scanning (augments regex-based scanning)
- [ ] Evidence: `docs/evidence/<ts>/github-setup/07-copilot/`

---

### Block 8 — Audit log streaming to Azure Monitor

- [ ] Enterprise → Settings → Audit log → Streaming → Destination = Azure Event Hubs
- [ ] Create Event Hub namespace and hub in `rg-ipai-dev-mon-sea`

```bash
az eventhubs namespace create -n ehns-ipai-github-audit -g rg-ipai-dev-mon-sea --location southeastasia --sku Standard
az eventhubs eventhub create -n audit-events -g rg-ipai-dev-mon-sea --namespace-name ehns-ipai-github-audit
```

- [ ] Configure GitHub audit log to stream to the Event Hub with SAS auth
- [ ] Create Log Analytics data connector to pull from Event Hub into `log-ipai-dev-runtime-sea`
- [ ] Verify audit events appear in Log Analytics
- [ ] Evidence: `docs/evidence/<ts>/github-setup/08-audit-log/`

---

### Block 9 — Extend repository rules + GHA billing

- [ ] Copy tier_0 ruleset to tier_1 repos (web, data-intelligence, agents, design, automations) via GitHub org rulesets

```bash
gh api /orgs/Insightpulse-ai/rulesets -X POST --input tier1-ruleset.json
```

- [ ] Confirm GitHub Actions billing is routed to Azure subscription
  - Enterprise → Billing → "Billed through Azure subscription" → link `eba824fb-...`
  - Set $50/mo monthly spending limit (per [`gha-scoped-exception.yaml`](../../ssot/governance/gha-scoped-exception.yaml))
- [ ] Verify Azure Cost Management shows GitHub Actions meter after first workflow run
- [ ] Evidence: `docs/evidence/<ts>/github-setup/09-rules-billing/`

---

### Block 10 — Azure Front Door provisioning (go-live blocker)

- [ ] Create AFD Standard profile

```bash
az afd profile create -n afd-ipai-prd -g rg-ipai-dev-net-sea --sku Standard_AzureFrontDoor
```

- [ ] Create endpoint + origin group + routes per [`reference-platform-doctrine.yaml#pattern_references.vercel_saas_microservices.canonical_contract`](../../ssot/governance/reference-platform-doctrine.yaml)
- [ ] Add ACA apps as origins: `ipai-odoo-dev`, `ipai-website`, `ipai-prismalab`, `ipai-w9studio`
- [ ] Attach custom domains with DNS CNAME validation
- [ ] Evidence: `docs/evidence/<ts>/github-setup/10-afd/`

---

### Block 11 — GitHub Projects ↔ Azure Boards sync

- [ ] Define sync contract in [`github-projects-v2-scope.yaml`](../../ssot/governance/github-projects-v2-scope.yaml) (source of truth = Azure Boards; GitHub Projects is projection)
- [ ] Create Azure Logic App to pull ADO work items → GitHub Issues
- [ ] Create GitHub webhook (issue events) → Logic App to push status changes back to ADO
- [ ] Verify round-trip on a test work item
- [ ] Evidence: `docs/evidence/<ts>/github-setup/11-projects-sync/`

---

## Non-blocking follow-ups (parallel)

- Update Developer Program support email from `jgtolentino_rn@yahoo.com` (personal Yahoo) to `platform@insightpulseai.com` (org-owned monitored alias)
- Transfer first published GitHub App from personal `jgtolentino` account to `Insightpulse-ai` org
- Reconcile observed `ipai-platform` enterprise slug vs canonical `ipai`
- Write enterprise README on `https://github.com/enterprises/ipai` (currently blank per dashboard)
- Complete remaining 7 "Explore Enterprise" onboarding items

## Rollback

Each block has its own rollback. Catastrophic rollback:

- Block 1 secret rotation: not reversible (old secret stays compromised — that's intended)
- Blocks 2-11: each has documented revert in the block's linked SSOT

## Verification after all blocks complete

- [ ] 0 direct repo grants outside teams ([`AC-2`](../../ssot/governance/github-target-state-success-criteria.yaml#category_1_organization_and_access))
- [ ] 100% tier_0 repos have CodeQL running ([`SEC-2`](../../ssot/governance/github-target-state-success-criteria.yaml#category_4_security_and_compliance))
- [ ] SAML enforcement ON ([`IDO-1`](../../ssot/governance/github-identity-and-oauth.yaml#success_criteria))
- [ ] SCIM provisioning live ([`IDO-2`](../../ssot/governance/github-identity-and-oauth.yaml#success_criteria))
- [ ] Foundry project registered and agent-platform connects ([`platform/ssot/ai/foundry-resource-model.yaml#reality_vs_target`](../../platform/ssot/ai/foundry-resource-model.yaml))
- [ ] Audit log streaming active
- [ ] AFD routing live with all 4 public hostnames
- [ ] Azure Cost Management shows GHA meter usage
- [ ] `push` succeeds without secret-scanning block

## Related

- [GitHub feature leverage matrix](../../ssot/governance/github-feature-leverage-matrix.yaml)
- [GitHub target state success criteria](../../ssot/governance/github-target-state-success-criteria.yaml)
- [GitHub enterprise current state snapshot](../../ssot/governance/github-enterprise-current-state-snapshot.yaml)
- [Well-Architected framework alignment](../../ssot/governance/github-well-architected-framework.yaml)
