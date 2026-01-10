# OCA Subtree Migration Plan

## Current State

The repository currently uses **git submodules** for OCA repositories at `addons/OCA/`:

```
addons/OCA/
├── queue/
├── server-tools/
├── web/
├── server-auth/
├── server-brand/
├── server-ux/
├── reporting-engine/
├── partner-contact/
├── automation/
├── helpdesk/
├── dms/
└── account-financial-reporting/
```

## Target State

Migrate to **git subtree** for deterministic pinning without submodule complexity.

New location: `addons/oca/` (lowercase, separate from existing placeholder)

## Why Subtree Over Submodules

| Aspect | Submodules | Subtree |
|--------|------------|---------|
| Clone behavior | Requires `--recursive` | Normal clone |
| CI complexity | Extra init steps | No extra steps |
| Pinning | SHA in `.gitmodules` | SHA in git history |
| Updates | `submodule update` | `subtree pull` |
| Code visibility | Reference only | Full code in repo |

## Migration Steps

### Phase 1: Prepare (Non-Breaking)

1. **Document current submodule SHAs**
   ```bash
   git submodule status > oca-submodule-pins.txt
   ```

2. **Create subtree target directory**
   ```bash
   # addons/oca/ already exists as placeholder
   # We'll add subtrees there
   ```

3. **Add subtrees for critical OCA repos**
   ```bash
   # Queue jobs (required for async tasks)
   git subtree add --prefix=addons/oca/queue \
     https://github.com/OCA/queue.git 18.0 --squash

   # Server tools
   git subtree add --prefix=addons/oca/server-tools \
     https://github.com/OCA/server-tools.git 18.0 --squash

   # Web widgets
   git subtree add --prefix=addons/oca/web \
     https://github.com/OCA/web.git 18.0 --squash
   ```

### Phase 2: Update Addons Path

1. **Update `odoo.conf` or compose**
   ```
   addons_path = /mnt/extra-addons/ipai,/mnt/extra-addons/oca
   ```

2. **Test module discovery**
   ```bash
   docker compose exec odoo-core odoo shell -d odoo_core
   >>> self.env['ir.module.module'].search([('name', 'like', 'queue%')])
   ```

### Phase 3: Remove Submodules (Breaking)

> **Warning:** This changes git history. Coordinate with team.

1. **Remove submodule entries**
   ```bash
   git submodule deinit -f addons/OCA/queue
   git rm -f addons/OCA/queue
   rm -rf .git/modules/addons/OCA/queue
   ```

2. **Clean up `.gitmodules`**
   ```bash
   # Remove entries for migrated repos
   git config -f .gitmodules --remove-section submodule.addons/OCA/queue
   ```

3. **Commit the removal**
   ```bash
   git add .gitmodules
   git commit -m "chore(oca): migrate queue from submodule to subtree"
   ```

### Phase 4: Update CI

1. **Remove submodule init steps**
   ```yaml
   # Before
   - run: git submodule update --init --recursive

   # After (not needed for subtrees)
   ```

2. **Update any scripts referencing `addons/OCA/`**

## Subtree Update Commands

When you need to update OCA modules:

```bash
# Pull latest changes from OCA queue
git subtree pull --prefix=addons/oca/queue \
  https://github.com/OCA/queue.git 18.0 --squash

# Pull latest changes from OCA server-tools
git subtree pull --prefix=addons/oca/server-tools \
  https://github.com/OCA/server-tools.git 18.0 --squash
```

## Recommended OCA Modules

### Required for Integration Modules

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `queue_job` | queue | Async job processing |
| `queue_job_cron_jobrunner` | queue | Cron-based job runner |
| `base_rest` | rest-framework | REST API framework |

### Optional but Useful

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `web_responsive` | web | Mobile-friendly backend |
| `web_notify` | web | User notifications |
| `audit_log` | server-tools | Audit trail |

## Rollback Plan

If issues arise during migration:

1. **Keep submodules until subtrees are verified**
2. **Test in staging environment first**
3. **Document all pinned commits**

## Timeline

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Prepare | Pending | Add subtrees alongside submodules |
| Phase 2: Update paths | Pending | Point to new location |
| Phase 3: Remove submodules | Pending | After team coordination |
| Phase 4: Update CI | Pending | Simplify workflows |

## References

- [Git Subtree Documentation](https://git-scm.com/book/en/v2/Git-Tools-Subtree-Merging)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md)
- [Current .gitmodules](./.gitmodules)
