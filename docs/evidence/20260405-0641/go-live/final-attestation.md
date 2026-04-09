# Final Go-Live Attestation

**Date**: 2026-04-05
**Environment**: `ipai-odoo-ha-env` (grayhill-34461e89, Southeast Asia)
**Public endpoint**: `erp.insightpulseai.com`

---

## Closed Gates

| Gate | Issue | Status | Date |
|------|-------|--------|------|
| PG private-only cutover | Wave A | CLOSED | pre-2026-04-05 |
| CA enforcement | Wave A | CLOSED | pre-2026-04-05 |
| HA runtime stabilization | Wave A | CLOSED | pre-2026-04-05 |
| Front Door origin cutover | #680 | CLOSED | 2026-04-05 |
| k6 load baseline | #681 | CLOSED | 2026-04-05 |
| Evidence refresh | #682 | CLOSED | 2026-04-05 |

## Remaining (Non-Blocking)

| Item | Issue | Status |
|------|-------|--------|
| Quarantine old dev apps | #683 | In progress |
| Secret migration (KV) | — | Planned |

---

## Runtime Posture

- **Stable HA runtime**: 3 container apps (web, worker, cron) in HA environment
- **Private-only PG**: No public access, private endpoint from ACA subnet
- **Edge path verified**: AFD → ACA, TLS valid, WAF clean
- **Performance baseline attached**: All p95 < thresholds, 0% error rate

---

## Evidence Pack

| Document | What it proves |
|----------|---------------|
| `front-door-cutover.md` | AFD origin, TLS, WAF, /web/login fix |
| `k6-baseline.md` | Performance thresholds, error rates |
| `k6-baseline-results.json` | Raw k6 data |
| `GO_LIVE_CHECKLIST.md` | Comprehensive gate tracking |

---

## Go / No-Go

**DECISION: GO**

All blocking gates are closed with evidence. The only remaining items (#683 secret migration, dev app quarantine) are non-blocking cleanup.

**Attestation date**: 2026-04-05T06:50Z
