# Repository Structure - odoo-ce

## Repository Locations

### 1. Local Repository (Your Mac)
```
Location: /Users/tbwa/odoo-ce
Branch: main
Current Commit: e8c4ef7c
Remote: git@github.com:jgtolentino/odoo-ce.git
```

This is where you make changes and push to GitHub.

### 2. Remote Repository (GitHub)
```
URL: https://github.com/jgtolentino/odoo-ce
Branch: main
Latest Commit: e8c4ef7c (synced)
```

This is the central repository on GitHub that both local and production sync with.

### 3. Production Repository (DigitalOcean Server)
```
Server: root@178.128.112.214
Location: /opt/odoo-ce/repo
Branch: main
Current Commit: 89fed573
Remote: https://github.com/jgtolentino/odoo-ce.git
```

This is cloned on the production server and mounted into the Odoo Docker container.

## Git Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  LOCAL REPO (/Users/tbwa/odoo-ce)                              │
│  ════════════════════════════════════                           │
│  Branch: main                                                   │
│  Commit: e8c4ef7c                                              │
│                                                                 │
│  You work here:                                                │
│  - Edit files                                                  │
│  - git commit                                                  │
│  - git push origin main                                        │
│                                                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ git push
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  REMOTE REPO (GitHub)                                           │
│  ═══════════════════════                                        │
│  URL: github.com:jgtolentino/odoo-ce                           │
│  Branch: main                                                   │
│  Commit: e8c4ef7c                                              │
│                                                                 │
│  Central repository:                                            │
│  - Stores all changes                                          │
│  - Both local and production sync here                         │
│                                                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ git pull (on production)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  PRODUCTION REPO (DigitalOcean)                                │
│  ═══════════════════════════════                               │
│  Server: root@178.128.112.214                                  │
│  Location: /opt/odoo-ce/repo                                   │
│  Branch: main                                                   │
│  Commit: 89fed573 (BEHIND by 2 commits)                       │
│                                                                 │
│  Deployed here:                                                │
│  - Mounted to Docker: /mnt/extra-addons                        │
│  - Used by Odoo: https://erp.insightpulseai.net               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Current Status

### Local vs Production

| Aspect | Local | Production |
|--------|-------|------------|
| **Location** | `/Users/tbwa/odoo-ce` | `/opt/odoo-ce/repo` |
| **Server** | Your Mac | `178.128.112.214` |
| **Commit** | `e8c4ef7c` | `89fed573` |
| **Status** | ✅ Up to date | ⚠️ Behind by 2 commits |

### Production is BEHIND

Production needs to pull the latest changes:

```bash
# Connect to production
ssh root@178.128.112.214

# Update production repo
cd /opt/odoo-ce/repo
git pull origin main

# Restart Odoo
docker restart odoo-prod
```

Or use the deployment script:
```bash
./scripts/deploy_theme_to_production.sh
```

## Docker Container Mount

```
Production Server Filesystem:
  /opt/odoo-ce/repo/addons/
      └── ipai/
          └── ipai_web_theme_tbwa/
              ├── __manifest__.py
              ├── views/
              │   └── webclient_templates.xml
              └── static/src/scss/
                  └── components/
                      ├── navbar.scss
                      └── login.scss

          ↓ Mounted as Docker Volume ↓

Docker Container Filesystem:
  /mnt/extra-addons/ipai/ipai_web_theme_tbwa/
      (same structure as above)
```

## How Changes Flow to Production

1. **Make changes locally**:
   ```bash
   cd /Users/tbwa/odoo-ce
   # Edit files
   git add .
   git commit -m "fix: my changes"
   git push origin main
   ```

2. **Deploy to production**:
   ```bash
   ./scripts/deploy_theme_to_production.sh
   ```

3. **What the script does**:
   - SSH to production server
   - `cd /opt/odoo-ce/repo`
   - `git pull origin main`
   - `docker restart odoo-prod`
   - Wait for health check

4. **Assets regenerate**:
   - Odoo automatically rebuilds CSS/JS on restart
   - Or manually: `./scripts/force_asset_regeneration.sh`

## Summary

- **Local**: Where you develop (`/Users/tbwa/odoo-ce`)
- **Remote**: GitHub central repo (`github.com:jgtolentino/odoo-ce`)
- **Production**: Live server (`178.128.112.214:/opt/odoo-ce/repo`)

**Current issue**: Production is 2 commits behind. Run deployment script to update!

```bash
./scripts/deploy_theme_to_production.sh
```
