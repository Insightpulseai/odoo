# Production Release Audit Template

Use this template to audit whether a feature was included and activated in a production release.

---

## Release Under Review

- **Release tag**: `prod-YYYYMMDD-HHMM`
- **Commit SHA**: `<full-sha>`
- **Previous prod tag**: `prod-YYYYMMDD-HHMM`
- **Deployment status**: Latest / Superseded

## Code Inclusion

### Commits in Range

```
git log --oneline <previous-tag>..<this-tag>
```

### Included PRs

| PR | Title | Merge SHA | Status |
|----|-------|-----------|--------|
| #NNN | description | sha | included |

### Not Included PRs (merged after tag)

| PR | Title | Merge SHA | Status |
|----|-------|-----------|--------|
| #NNN | description | sha | excluded — merged after prod tag |

## Runtime Activation Checks

### Odoo Modules

| Check | Status |
|-------|--------|
| Required module installed | yes / no / N/A |
| Migration applied | yes / no / N/A |
| Config present (odoo.conf) | yes / no / N/A |
| Module list updated | yes / no / N/A |

### Platform / Infrastructure

| Check | Status |
|-------|--------|
| Env vars / secrets present | yes / no / N/A |
| External integration connected | yes / no / N/A |
| Health check passed | yes / no / N/A |
| DNS / domain configured | yes / no / N/A |

### Database

| Check | Status |
|-------|--------|
| Schema migration applied | yes / no / N/A |
| Seed data present | yes / no / N/A |
| RLS policies active | yes / no / N/A |

## Feature Audit Table

| Feature | Merged before prod SHA? | Reachable from prod SHA? | Requires activation? | Active in prod? |
|---------|:-----------------------:|:------------------------:|:--------------------:|:---------------:|
| feature-name | yes/no | yes/no | yes/no | yes/no |

## Verdict

- **Deployed in code**: yes / no
- **Active in runtime**: yes / no / unknown
- **Expected in production**: yes / no

## Gaps

- [ ] Missing migration
- [ ] Missing module install
- [ ] Missing env var / secret
- [ ] Missing release note coverage
- [ ] Missing health check verification
