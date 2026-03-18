# Examples — odoo-staging-to-production-promotion

## Example 1: Clean production deployment

**Input**: Staging validated, tester and platform admin sign-off received

**Output**:
- Tester evidence: `docs/evidence/20260317-1500/odoo-delivery/odoo-staging-validation/` — PASS (38 tests, 0 failures)
- Platform admin: backup at 2026-03-17T16:00:00Z confirmed, monitoring active — PASS
- Rollback: previous revision `rev-prod-abc788`, backup at 16:00:00Z
- Production revision: `rev-prod-abc789` deployed, health check 200 — PASS
- Database: migration completed (0 errors)
- Bake-time: 30 minutes observed, error rate 0.1% (baseline 0.1%), p95 latency 450ms (baseline 420ms) — PASS
- Release status: HEALTHY
- Evidence: `docs/evidence/20260317-1630/odoo-delivery/odoo-staging-to-production-promotion/`

## Example 2: Bake-time failure

**Input**: Production deployed but error rate spiked during observation

**Output**:
- Production revision: `rev-prod-def790` deployed, health check 200
- Bake-time: 15 minutes elapsed, error rate 8.5% (baseline 0.2%, threshold 5.2%) — FAIL
- Finding: `ipai_helpdesk` raising `ValidationError` on ticket creation — cron conflict
- Action: ROLLBACK to `rev-prod-def789` + restore DB to 2026-03-17T16:00:00Z backup
- Release status: FAILED — rollback executed
- Evidence: Azure Monitor error rate graph + container logs excerpt
