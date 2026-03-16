# Secret Management Quick Reference

## Your Setup: 5 Manual Sets Required

| # | Secret | Where | Command |
|---|--------|-------|---------|
| 1 | `CLOUDFLARE_API_TOKEN` | GitHub | `ONLY=github ./scripts/secrets/sync_all.sh` |
| 2 | `SUPABASE_ANON_KEY` | GitHub | ↑ (same command) |
| 3 | `DO_ACCESS_TOKEN` | GitHub | ↑ (same command) |
| 4 | `OPENAI_API_KEY` | Supabase | `ONLY=supabase ./scripts/secrets/sync_all.sh` |
| 5 | `SUPABASE_SERVICE_ROLE_KEY` | Supabase | ↑ (same command) |

**One-Time Setup** (2 commands total):
```bash
ONLY=github ./scripts/secrets/sync_all.sh     # Sets 3 secrets
ONLY=supabase ./scripts/secrets/sync_all.sh   # Sets 2 secrets
```

---

## Rotation Schedule

| Secret | Rotate Every | Next Due |
|--------|--------------|----------|
| `CLOUDFLARE_API_TOKEN` | 30 days | Calculate from last rotation |
| `OPENAI_API_KEY` | 90 days | Calculate from last rotation |
| `SUPABASE_SERVICE_ROLE_KEY` | 90 days | Calculate from last rotation |
| `DO_ACCESS_TOKEN` | 90 days | Calculate from last rotation |
| `SUPABASE_ANON_KEY` | 365 days | Rarely (low risk) |
| `GITHUB_TOKEN` | Auto | N/A (GitHub manages) |

---

## Emergency: Token Exposed

```bash
# 1. Rotate at provider NOW
# 2. Update env var
export EXPOSED_SECRET="new-value"

# 3. Sync (< 30 seconds)
./scripts/secrets/sync_all.sh

# 4. Verify
gh secret list | grep EXPOSED_SECRET
```

---

## Daily Operations

```bash
# Validate registry
./scripts/secrets/validate_registry.py

# Check GitHub secrets
gh secret list

# Check Supabase secrets
supabase secrets list

# Test Cloudflare workflow
gh workflow run infra-cloudflare-dns.yml
```
