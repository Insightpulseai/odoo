# Examples: SaaS Billing & Cost Management

## Example 1: Per-Seat Tiered Model

**Pricing table**:

| Tier | Price | Users | Features |
|------|-------|-------|----------|
| Free | $0/mo | up to 3 | Core features, 1GB storage |
| Standard | $15/user/mo | up to 50 | All features, 50GB storage, API access |
| Enterprise | Custom | Unlimited | Dedicated resources, SLA, SSO federation |

**Cost attribution**: Azure tags (`tier: free|standard|enterprise`, `tenant-id: {uuid}`) on all resources. Shared compute costs split by user-count ratio.

**Budget alerts**: Free tier hard-capped at $5/mo infrastructure cost. Standard tier alerts at 80% of expected margin. Enterprise tier custom thresholds.

---

## Example 2: Usage-Based Model

**Pricing table**:

| Metric | Unit | Price |
|--------|------|-------|
| API calls | per 1,000 | $0.50 |
| Storage | per GB/mo | $0.10 |
| Compute minutes | per minute | $0.02 |

**Metering pipeline**:
```
API Gateway --> Event Hub --> Stream Analytics --> Cosmos DB (usage store)
                                                       |
                                               Rating Engine --> Invoice
```

**Anti-fraud**: Rate limiting per tenant, anomaly detection on usage spikes, pre-paid credits with hard cutoff.

---

## Example 3: Hybrid Model (InsightPulse AI)

**Pricing table**:

| Tier | Base Price | Included | Overage |
|------|-----------|----------|---------|
| Starter | $49/mo | 5 users, 10GB, 10K API calls | $0.01/call |
| Business | $199/mo | 25 users, 100GB, 100K API calls | $0.005/call |
| Enterprise | Custom | Custom limits, dedicated infra | Negotiated |

**Cost management**: Azure Cost Management with tenant-id tag filter. Monthly export to billing system. Shared infrastructure cost allocated by weighted user count.
