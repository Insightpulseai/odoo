# Odoo.sh-Equivalent E2E Test Plan

> Validates that the Azure-native Odoo platform achieves operational parity with Odoo.sh across 10 test lanes covering 5 parity surfaces: delivery, safety, operator, recovery, and lifecycle.

---

## Parity Surfaces

| Surface | What It Proves |
|---------|---------------|
| **Delivery** | Branch → build → deploy works like Odoo.sh builds |
| **Safety** | Non-prod cannot cause real-world side effects |
| **Operator** | Shell, logs, mail view, monitoring are available |
| **Recovery** | Backup + restore produces a usable environment |
| **Lifecycle** | Environments are created, promoted, and cleaned up predictably |

---

## Test Lanes

### 1. Development Build

**Goal**: A branch change produces an isolated, testable non-prod build.

| Check | Pass Criteria |
|-------|--------------|
| Code push triggers deploy/test lane | Pipeline run succeeds |
| New non-prod environment or revision is created | ACA revision exists |
| Environment uses fresh DB for dev | `odoo_dev` or `test_<module>` DB, not prod clone |
| Module install/update and tests run | `--test-enable` exit code 0 |
| Build logs are retained and readable | GitHub Actions / AzDO logs accessible |
| Environment is reachable and isolated from prod | Different revision, zero prod traffic |

### 2. Preview / Instant Branch Deploy

**Goal**: Feature branches produce Odoo.sh-style preview availability.

| Check | Pass Criteria |
|-------|--------------|
| PR/branch update creates preview revision | ACA revision with deterministic label |
| Preview has deterministic name/label | Derived from PR number or branch name |
| Preview URL emitted in pipeline evidence | URL in pipeline artifacts/logs |
| Prod traffic unchanged | Traffic weight = 0% on preview revision |
| Re-run updates same preview lane | Same label, new revision replaces old |

### 3. Staging Clone from Production

**Goal**: Staging uses a fresh clone of prod data, not a drifted test DB.

| Check | Pass Criteria |
|-------|--------------|
| Staging rebuild restores from prod backup | `pg_dump`/`pg_restore` from `odoo` → `odoo_staging` |
| Staging DB is recreated, not reused | Known prod records appear after clone |
| Filestore is cloned or mounted | Azure Files share accessible from staging |
| Restore provenance is recorded | Source timestamp + target identity in evidence |

### 4. Neutralization and Post-Import Safety

**Goal**: Staging/imported environments cannot cause real-world side effects.

| Check | Pass Criteria |
|-------|--------------|
| `ir.cron` scheduled actions disabled | `active=False` on all non-whitelisted crons |
| Real SMTP disabled or routed to Mailpit | `ir.mail_server` blanked or pointing to `ipai-mailpit-dev:1025` |
| Payment providers disabled or test mode | All `payment.provider` records `state != 'enabled'` |
| Shipping/integration connectors neutralized | No real-world external side effects possible |
| Idempotent | Running twice produces no harmful drift |
| No real outbound email leaves staging/dev | Mail lands in Mailpit, not real SMTP |

### 5. Operator Tooling

**Goal**: Operators have the same troubleshooting surfaces as Odoo.sh.

| Check | Pass Criteria |
|-------|--------------|
| Real-time application logs readable | `az containerapp logs show` returns log lines |
| Container shell/console access works | `az containerapp exec` opens shell |
| DB shell access in non-prod | `psql` to `odoo_dev` / `odoo_staging` |
| Outgoing mail inspection | Mailpit web UI shows staged emails |
| Monitoring/status reachable | Azure Monitor / Application Insights |

### 6. Production Promotion and Approval

**Goal**: Prod deploys are deliberate, reviewable, and reversible.

| Check | Pass Criteria |
|-------|--------------|
| Non-prod passes before prod stage | Pipeline stage dependency enforced |
| Production stage is approval-gated | AzDO environment approval required |
| Deploy produces new revision | New revision name, old revision available |
| Rollback target known | Previous working revision identified |

### 7. Backup and Restore

**Goal**: The platform can recover what Odoo.sh protects.

| Check | Pass Criteria |
|-------|--------------|
| Production DB backup exists and is recent | Azure PG automated backup within 24h |
| Restore recreates usable environment | Known record recoverable after restore |
| Filestore included in recovery | Azure Files share persists across restores |
| Immutable backup survives deletion attempt | `odoo-backups` container rejects delete within 30 days |
| Evidence includes restore point + duration | Restore metadata captured |

### 8. Filestore Persistence

**Goal**: Attachments survive redeploys, revision swaps, and restarts.

| Check | Pass Criteria |
|-------|--------------|
| Upload attachment in Odoo | File created in Azure Files share |
| Restart/roll to new revision | Attachment still accessible |
| Filestore path stable | `/var/lib/odoo/filestore` mount survives revision update |
| No corruption or orphaning | File hash matches before/after |

### 9. Build Garbage Collection / Lifecycle

**Goal**: Non-prod environments don't accumulate forever.

| Check | Pass Criteria |
|-------|--------------|
| Old preview/dev environments pruned | Stale revisions deactivated per policy |
| No-traffic revisions cleaned | ACA revision list bounded |
| Cleanup never touches prod | Active prod revision untouched |
| Cleanup logged | Evidence of what was removed |

### 10. Business Smoke Tests

**Goal**: The platform is usable, not just alive.

| Check | Pass Criteria |
|-------|--------------|
| Login | Operator can authenticate |
| Install/update addons | Target modules install without error |
| Create lead/contact | CRM record persists |
| Create quotation/invoice | Sales flow completes |
| Send test email (non-prod) | Email lands in Mailpit |
| Upload and retrieve attachment | File round-trips through filestore |
| Run scheduled action manually | Action completes without error |
| Payment provider disabled in non-prod | Payment flow blocked/test-only |

---

## Evidence Pack Structure

```
docs/evidence/<timestamp>/odoosh-equivalent-e2e/
  00-summary.md
  01-dev-build.md
  02-preview-lane.md
  03-staging-clone.md
  04-neutralization.md
  05-operator-tooling.md
  06-prod-promotion.md
  07-backup-restore.md
  08-filestore.md
  09-gc.md
  10-smoke-tests.md
  artifacts/
    pipeline-logs/
    revision-metadata/
    restore-metadata/
    screenshots-or-json/
```

### Summary Format (`00-summary.md`)

| Lane | Verdict | Notes |
|------|---------|-------|
| 1. Dev build | PASS / FAIL / PARTIAL / NOT TESTED | |
| 2. Preview lane | ... | |
| ... | ... | |

---

## Minimum Exit Criteria

The Azure stack is **not** "Odoo.sh-equivalent" until all of these pass together:

- [ ] Fresh staging clone from prod
- [ ] Staging neutralization
- [ ] Mail catcher / no real outbound mail in non-prod
- [ ] Preview or development branch deploy
- [ ] Shell + logs access
- [ ] Backup + restore tested
- [ ] Persistent filestore across revisions

---

## Benchmark References

| Benchmark Source | Classification |
|------------------|---------------|
| **Odoo.sh admin docs** | Platform behavior benchmark (builds, staging, neutralization, backups, operator tools) |
| **Azure SAP DevOps automation** | Deploy control-plane benchmark (AzDO pipelines, service connections, variable groups) |
| **Azure Container Apps docs** | Runtime benchmark (revisions, labels, traffic splitting, console access, Azure Files mounts) |

---

*Last updated: 2026-04-01*
