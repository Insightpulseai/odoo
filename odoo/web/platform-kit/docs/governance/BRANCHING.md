# Branching & Release Policy

> Platform Kit follows a trunk-based development model with protected main branch.

## Branch Naming

| Pattern | Purpose | Example |
|---------|---------|---------|
| `main` | Protected, deployable, tagged releases | - |
| `develop` | Integration branch (optional) | - |
| `feat/<slug>` | Feature branches | `feat/plane-sync` |
| `fix/<slug>` | Bug fix branches | `fix/queue-retry` |
| `hotfix/<slug>` | Urgent production fixes | `hotfix/auth-bypass` |
| `release/<version>` | Release stabilization | `release/1.2.0` |
| `claude/<slug>` | AI-assisted development | `claude/platform-kit-v1` |

## Protected Branch Rules

### `main` Branch

- **Required reviews:** 1 (or 0 for automated PRs with passing CI)
- **Required checks:**
  - `secrets-scan` (gitleaks)
  - `validate-secrets-shape`
  - `lint-and-unit`
  - `terraform-plan`
- **No direct pushes** (except release automation)
- **No force pushes**

## PR Requirements

### Before Merge

1. All CI checks pass
2. Terraform plan reviewed (if infrastructure changes)
3. Migration dry-run passes (if database changes)
4. No secrets detected by gitleaks
5. Changelog updated (for releases)

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Maintenance

**Examples:**
```
feat(ops): add queue claim with visibility timeout
fix(plane-sync): handle rate limit responses
docs(governance): add branching policy
```

## Release Process

### Version Tagging

- **Major:** Breaking changes (`v2.0.0`)
- **Minor:** New features, backwards compatible (`v1.2.0`)
- **Patch:** Bug fixes (`v1.2.1`)

### Release Steps

1. Create `release/<version>` branch from `main`
2. Update changelog
3. Run full test suite
4. Merge to `main`
5. Tag: `git tag -a v1.2.0 -m "Release v1.2.0"`
6. Push tag: `git push origin v1.2.0`

## Environment Mapping

| Branch | Environment | Auto-Deploy |
|--------|-------------|-------------|
| `main` | Production | Yes |
| `develop` | Staging | Yes (if configured) |
| `feat/*` | Preview | On PR (if configured) |

## Hotfix Process

1. Branch from `main`: `git checkout -b hotfix/critical-fix main`
2. Apply minimal fix
3. Create PR with `[HOTFIX]` prefix
4. Fast-track review (1 approval)
5. Merge to `main`
6. Tag patch release
7. Cherry-pick to `develop` if applicable

## Rollback Strategy

### Code Rollback

```bash
# Revert the problematic merge
git revert <merge_commit_sha>
git push origin main

# Or deploy previous tag
git checkout v1.1.0
# Re-run deploy workflow
```

### Database Rollback

1. **Preferred:** Apply down migration if available
2. **Emergency:** Use Supabase PITR (Point-in-Time Recovery)
3. **Document:** Create incident report

### Secret Rotation

If secrets are compromised:

1. Immediately rotate at provider
2. Update Supabase secrets: `supabase secrets set KEY="new_value"`
3. Update GitHub Actions secrets
4. Redeploy affected functions
5. Document in security incident log
