# Email Admin Migration Checklist

**Purpose**: Step-by-step guide to migrate platform ownership to `devops@insightpulseai.com`

**Policy Reference**: `admin-email-policy.yaml`

**Status**: 4 platforms pending migration

---

## Pre-Migration Checklist

- [ ] Verify `devops@insightpulseai.com` email account is active and accessible
- [ ] Store `devops@` credentials in Supabase Vault (use email policy SSOT)
- [ ] Backup current admin access credentials before starting
- [ ] Notify team of planned migration window
- [ ] Test `devops@` login on a non-critical platform first

---

## Migration Targets (Priority Order)

### ✅ High Priority: Security-Critical Platforms

#### 1. Supabase (`spdtwktxdalcfigzeqrz`) - **HIGH PRIORITY**

**Current Owner**: `jgtolentino.rn@gmail.com`
**Target Owner**: `devops@insightpulseai.com`
**Risk**: Control plane for ops, auth, Vault access

**Migration Steps**:

1. **Add devops@ as Owner**
   - Login to Supabase dashboard as current owner
   - Go to: Settings → Team
   - Click "Invite member"
   - Email: `devops@insightpulseai.com`
   - Role: **Owner**
   - Send invitation

2. **Accept Invitation**
   - Access devops@ inbox
   - Click invitation link
   - Complete account setup if needed
   - Verify access to project dashboard

3. **Transfer Critical Permissions**
   - Settings → API: Verify devops@ can access service role key
   - Settings → Database: Verify devops@ can access connection strings
   - Vault: Verify devops@ can read secrets
   - Edge Functions: Verify devops@ can deploy

4. **Demote Original Owner** (After 48h verification period)
   - Settings → Team
   - Find `jgtolentino.rn@gmail.com`
   - Change role from Owner → Developer (or remove if not needed)
   - Confirm demotion

5. **Update References**
   - Update `admin-email-policy.yaml` status: pending → completed
   - Update Vault references if any
   - Update team documentation

**Validation**:
```bash
# Verify devops@ has service role access
curl -H "Authorization: Bearer $DEVOPS_SUPABASE_TOKEN" \
  https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/

# Expected: 200 OK
```

**Rollback**: Re-promote original owner if issues arise within 7 days

---

#### 2. GitHub Organization (`Insightpulseai`) - **HIGH PRIORITY**

**Current Owner**: `jgtolentino.rn@gmail.com`
**Target Owner**: `devops@insightpulseai.com`
**Risk**: Source code, CI/CD, webhooks, secrets

**Migration Steps**:

1. **Add devops@ as Owner**
   - Go to: https://github.com/orgs/Insightpulseai/people
   - Click "Invite member"
   - Username/Email: `devops@insightpulseai.com`
   - Role: **Owner**
   - Send invitation

2. **Accept Invitation**
   - Access devops@ inbox
   - Click GitHub invitation link
   - Accept organization invitation

3. **Transfer Critical Permissions**
   - Verify devops@ can:
     - Create repositories
     - Manage webhooks
     - Access organization secrets
     - Modify team permissions
     - Access GitHub Actions

4. **Transfer Repository Ownership** (Optional)
   - For each critical repo: Settings → Danger Zone
   - Transfer ownership to organization if not already
   - Ensure devops@ has admin access

5. **Demote Original Owner** (After 7 day verification period)
   - Organization → People
   - Find `jgtolentino.rn@gmail.com`
   - Change role from Owner → Member (or remove if not needed)
   - Confirm demotion

6. **Update References**
   - Update `admin-email-policy.yaml` status: pending → completed
   - Update CI/CD references
   - Update webhook configurations

**Validation**:
```bash
# Verify devops@ has org admin access
gh api orgs/Insightpulseai/members/devops --jq '.role'
# Expected: "admin" or "Owner"
```

**Rollback**: Re-promote original owner via organization settings

---

### ⚠️ Medium Priority: Infrastructure Platforms

#### 3. Vercel (`insightpulseai` team) - **MEDIUM PRIORITY**

**Current Owner**: `jake.tolentino@insightpulseai.com`
**Target Owner**: `devops@insightpulseai.com`
**Risk**: Frontend deployments, domain management, env vars

**Migration Steps**:

1. **Add devops@ as Owner**
   - Go to: Settings → Team Members
   - Click "Invite Member"
   - Email: `devops@insightpulseai.com`
   - Role: **Owner**
   - Send invitation

2. **Accept Invitation**
   - Access devops@ inbox
   - Click Vercel invitation link
   - Complete account setup

3. **Transfer Critical Permissions**
   - Verify devops@ can:
     - Deploy projects
     - Manage domains
     - Access environment variables
     - Configure integrations

4. **Demote Original Owner** (After 48h verification period)
   - Settings → Team Members
   - Find `jake.tolentino@insightpulseai.com`
   - Change role from Owner → Member
   - Confirm demotion

5. **Update References**
   - Update `admin-email-policy.yaml` status: pending → completed
   - Update deployment documentation

**Validation**:
```bash
# Verify devops@ can list projects
vercel projects ls --token $DEVOPS_VERCEL_TOKEN
# Expected: List of projects
```

**Rollback**: Re-promote original owner via team settings

---

#### 4. Cloudflare (`insightpulseai.com` zone) - **MEDIUM PRIORITY**

**Current Owner**: `jake.tolentino@insightpulseai.com`
**Target Owner**: `devops@insightpulseai.com`
**Risk**: DNS, SSL, WAF, Workers

**Migration Steps**:

1. **Add devops@ as Administrator**
   - Go to: Manage Account → Members
   - Click "Invite"
   - Email: `devops@insightpulseai.com`
   - Role: **Administrator**
   - Send invitation

2. **Accept Invitation**
   - Access devops@ inbox
   - Click Cloudflare invitation link
   - Complete account setup

3. **Transfer Zone Ownership**
   - Go to: Domain → Overview → Advanced Actions
   - Transfer zone to devops@ if needed
   - Or verify devops@ has Administrator role

4. **Transfer Critical Permissions**
   - Verify devops@ can:
     - Modify DNS records
     - Manage SSL/TLS certificates
     - Configure Workers
     - Modify WAF rules

5. **Demote Original Owner** (After 7 day verification period)
   - Manage Account → Members
   - Find `jake.tolentino@insightpulseai.com`
   - Change role from Administrator → Member
   - Confirm demotion

6. **Update References**
   - Update `admin-email-policy.yaml` status: pending → completed
   - Update DNS documentation
   - Update Terraform references

**Validation**:
```bash
# Verify devops@ can list zones
curl -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $DEVOPS_CF_TOKEN" \
  | jq '.result[].name'

# Expected: insightpulseai.com
```

**Rollback**: Re-promote original owner via account settings

---

## Post-Migration Verification

### All Platforms

After each platform migration:

1. **Functional Test**
   - [ ] Login with devops@ credentials
   - [ ] Perform critical operation (e.g., deploy, DNS change)
   - [ ] Verify operation succeeds

2. **Access Verification**
   - [ ] Verify devops@ has Owner/Administrator role
   - [ ] Verify devops@ can access secrets/credentials
   - [ ] Verify devops@ can modify critical settings

3. **Documentation Update**
   - [ ] Update `admin-email-policy.yaml` status
   - [ ] Update team runbooks
   - [ ] Update incident response contacts

4. **Credential Storage**
   - [ ] Store devops@ platform credentials in Supabase Vault
   - [ ] Verify Vault access from CI/CD if needed
   - [ ] Remove any hardcoded credentials

5. **Team Notification**
   - [ ] Notify team of completed migration
   - [ ] Share updated access procedures
   - [ ] Update emergency contact lists

---

## Migration Timeline

| Platform | Priority | Estimated Time | Dependencies |
|----------|----------|----------------|--------------|
| Supabase | High | 2 hours | None |
| GitHub Org | High | 1 hour | None |
| Vercel | Medium | 1 hour | None |
| Cloudflare | Medium | 1 hour | None |

**Total Estimated Time**: 5 hours (can be done in parallel)

**Recommended Approach**: Migrate high-priority platforms first, then medium-priority

---

## Rollback Procedures

### If Migration Causes Issues

1. **Immediate Rollback** (within 48 hours):
   - Re-promote original owner to Owner role
   - Demote devops@ to Member or remove
   - Restore original credentials from backup

2. **Partial Rollback** (48h - 7 days):
   - Keep both accounts as Owner
   - Gradually transition critical operations
   - Remove original owner after extended verification

3. **Post-Migration Issues** (after 7 days):
   - Create new admin account if devops@ is compromised
   - Transfer ownership to new account
   - Rotate all credentials immediately

---

## Troubleshooting

### Common Issues

**Issue**: devops@ invitation not received
- **Fix**: Check spam folder, resend invitation, verify email address spelling

**Issue**: devops@ lacks permission after migration
- **Fix**: Verify Owner/Administrator role was assigned, not Member or Developer

**Issue**: Original owner cannot be demoted
- **Fix**: Ensure at least 2 Owners exist before demotion, platform may require minimum

**Issue**: Credentials don't work after migration
- **Fix**: Regenerate API keys/tokens after ownership transfer, update Vault

---

## Compliance Verification

After all migrations complete:

```bash
# Run email policy audit
./scripts/audit-email-policy.sh

# Expected output:
# ✅ Supabase: devops@insightpulseai.com (Owner)
# ✅ GitHub Org: devops@insightpulseai.com (Owner)
# ✅ Vercel: devops@insightpulseai.com (Owner)
# ✅ Cloudflare: devops@insightpulseai.com (Administrator)
#
# Compliance Status: PASS
```

---

## Related Documents

- `admin-email-policy.yaml` - Policy SSOT
- `docs/EMAIL_ALIAS_GUIDE.md` - Email alias usage guide
- `.github/workflows/email-policy-check.yml` - CI enforcement
- `infra/identity/` - Identity and access management

---

**Last Updated**: 2026-02-17
**Migration Status**: Pending
**Next Review**: After all migrations complete
