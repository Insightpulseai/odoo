# Stabilization and First-Close Guide — Pulser for Odoo

The Stabilization Phase is the final stage of the Go-Live Factory, ensuring that the new tenant environment is resilient, the users are proficient, and the first financial close is verified for accuracy.

---

## 1. The 30-Day Stabilization Window (BOM 13, 16)

Following "Zero Hour" activation, every tenant enters a mandatory **Stabilization Window**.

### Hypercare (Days 1–5)
- **Monitoring**: High-frequency telemetry review every 4 hours.
- **Daily LSR**: 15-minute "Live Site Review" at the start of each business day with the tenant Process Owner and Pulser Consultant.
- **Triage**: P1/P2 issues resolved within the 4-hour/8-hour service level target.

### Stabilization Support (Days 6–30)
- **Weekly Sync**: Review system performance, user adoption gaps, and exception logs.
- **Hypercare Channel**: Dedicated priority support channel remains active.

## 2. The First-Close Review Protocol (BOM 13)

The first financial close performed on the Pulser Hub is a critical quality checkpoint.

| Checkpoint | Target | Verification Method |
|------------|--------|---------------------|
| **Trial Balance Integrity** | 0% Variance vs. Ground Truth | Full account-level TB reconciliation between Odoo and source evidence. |
| **Agent Performance** | High Confidence | Manual audit of a sample of AI-assisted reconciliations and tax determinations. |
| **Close Task Completion** | 100% On-Time | Verification that all 39 close tasks in Phase I-V were completed. |
| **Data Continuity** | Trend Match | Comparison of month-end balances vs. the 24-month historical trend. |

## 3. Stabilization Sign-off

The tenant is transitioned from "Live Site" to "Steady State" status only after the **Stabilization Exit Authorization Log** is filed.

Required Sign-offs:
1. **First-Close Sign-off**: Verified by the Tenant Finance Director.
2. **Operational Stability Sign-off**: Verified by the Pulser SRE/Platform Lead.
3. **User Proficiency Sign-off**: Verified by the Tenant Process Owner.

## 4. Marketplace Subscription Reliability (GTM)

For tenants provisioned via the Microsoft Commercial Marketplace, the "Stabilization Window" begins with the technical handshake.

### SaaS Fulfillment Monitoring
- **Webhook Handshake**: Monitor `/api/marketplace/webhook` via App Insights for `200 OK` responses during `Activate` and `Resolve` calls.
- **Onboarding Link**: Verify the customer completes the Entra ID SSO handshake at `w9studio.net/onboarding/marketplace` within 24 hours of purchase.

### Operational Failover (Hypercare Only)
- **Manual Activation**: In the event of an API `v2` handshake failure, the Platform Lead may manually activate the Odoo Subscription record to ensure zero-downtime onboarding, provided a valid `Marketplace Purchase ID` is evidenced in the Partner Center portal.
- **Retry Logic**: All failed webhooks must be replayed within 4 hours to synchronize the Odoo `marketplace.fulfillment` audit log.

---

*Last updated: 2026-04-18*
