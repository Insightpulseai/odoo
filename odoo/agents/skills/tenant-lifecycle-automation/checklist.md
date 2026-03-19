# Checklist: Tenant Lifecycle Automation

## Provisioning

- [ ] Provisioning workflow fully automated (zero manual steps)
- [ ] Resource creation scripted (Bicep/Terraform for dedicated resources)
- [ ] Database setup automated (schema creation, seed data, RLS policies)
- [ ] DNS configuration automated (subdomain creation, certificate provisioning)
- [ ] Identity setup automated (tenant record, admin user, role assignments)
- [ ] Health validation runs after provisioning (smoke test)
- [ ] Provisioning is idempotent (safe to retry)
- [ ] Provisioning time meets SLO (< 5 min shared, < 30 min dedicated)

## Onboarding

- [ ] Signup form captures required tenant information
- [ ] Email verification automated
- [ ] Initial admin user created with secure temporary credentials
- [ ] Welcome email sent with getting-started guide
- [ ] Default configuration applied based on tier
- [ ] First-login experience guides admin through setup

## Configuration Management

- [ ] Per-tenant configuration stored in centralized config store
- [ ] Configuration versioned (rollback possible)
- [ ] Feature flags per tenant supported
- [ ] Branding customization per tenant supported
- [ ] Configuration changes audited

## Offboarding

- [ ] Tenant deactivation disables access immediately
- [ ] Data export provided to tenant before deletion
- [ ] Grace period enforced (configurable, default 30 days)
- [ ] Resource cleanup automated after grace period
- [ ] Permanent deletion confirmed and logged
- [ ] Data retention compliance verified

## Self-Service

- [ ] Tenant admin can manage users (invite, remove, assign roles)
- [ ] Tenant admin can view billing and usage
- [ ] Tenant admin can update configuration and branding
- [ ] Tenant admin can export their data
- [ ] All self-service actions produce audit events
