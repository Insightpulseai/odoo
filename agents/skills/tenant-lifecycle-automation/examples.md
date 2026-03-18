# Examples: Tenant Lifecycle Automation

## Example 1: Provisioning Workflow (Shared Model)

**State machine**:
```
[requested] --> [provisioning] --> [active] --> [suspended] --> [offboarding] --> [deleted]
                     |                              |
                     v                              v
                [failed] ----retry-----> [provisioning]
```

**Provisioning steps** (shared model, < 5 min):
1. Create tenant record in control plane database
2. Create database schema for tenant (or enable RLS row)
3. Seed default configuration data
4. Create admin user in identity provider
5. Configure subdomain DNS (if subdomain model)
6. Send welcome email with activation link
7. Run smoke test (API health check with tenant context)
8. Transition state to `active`

**Failure handling**: Each step is idempotent. On failure, retry from the failed step. After 3 retries, transition to `failed` state and alert operations.

---

## Example 2: Offboarding Workflow

**Timeline**:
```
Day 0: Tenant requests cancellation
  --> Deactivate: disable login, stop billing, mark as "suspended"
Day 1-30: Grace period
  --> Tenant can reactivate by contacting support
  --> Data export available via self-service download
Day 30: Grace period expires
  --> Export data to cold storage (compliance retention)
  --> Delete tenant resources (database schema, storage, secrets)
  --> Remove DNS records
  --> Permanent deletion logged
Day 30 + retention period: Cold storage purged
```

---

## Example 3: Self-Service Capability Matrix

| Capability | Free | Standard | Enterprise |
|-----------|------|----------|------------|
| Manage users | 3 max | 50 max | Unlimited |
| View usage dashboard | Basic | Detailed | Custom |
| Update branding | No | Logo only | Full theme |
| Export data | Manual request | Self-service | API + self-service |
| Configure SSO | No | No | Yes (SAML/OIDC) |
| API key management | 1 key | 5 keys | Unlimited |
| Billing management | View only | Self-service | Custom invoicing |
