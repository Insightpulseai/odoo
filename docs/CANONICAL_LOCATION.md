# Canonical Odoo CE Location

**Purpose**: Document the permanent, canonical location for Odoo CE development to prevent data loss from periodic Downloads folder cleanup.

---

## ⚠️ Critical: Avoid Downloads Folder

**Problem**: The Downloads folder is periodically cleaned, which will **delete any sandbox work** left there.

**Old (Temporary) Location** - ❌ DO NOT USE:
```
~/Downloads/extracted_files/odoo-dev-sandbox
```
This location will be wiped during cleanup!

**Canonical (Permanent) Location** - ✅ USE THIS:
```
~/Documents/GitHub/odoo-ce
```

---

## Canonical Paths

| Component | Path | Purpose |
|-----------|------|---------|
| **Repo Root** | `~/Documents/GitHub/odoo-ce` | Git repository, permanent storage |
| **Sandbox** | `~/Documents/GitHub/odoo-ce/sandbox/dev` | Docker compose runtime, development work |
| **Docker Compose** | `~/Documents/GitHub/odoo-ce/sandbox/dev/docker-compose.yml` | Container orchestration |
| **Entrypoint** | `~/Documents/GitHub/odoo-ce/bin/odoo-ce` | Canonical operations wrapper |

---

## Migration from Downloads

If you have work in the temporary Downloads location:

```bash
# 1. Check if temporary location exists
ls ~/Downloads/extracted_files/odoo-dev-sandbox

# 2. Copy any custom work (if needed)
# WARNING: Only copy files you created, not the entire sandbox
cp -r ~/Downloads/extracted_files/odoo-dev-sandbox/custom_work ~/Documents/GitHub/odoo-ce/sandbox/dev/

# 3. Verify canonical location has everything
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
ls -la

# 4. Safe to delete temporary location
rm -rf ~/Downloads/extracted_files/odoo-dev-sandbox
```

---

## Canonical Usage

**Always use the canonical entrypoint:**

```bash
# Start sandbox (works from any directory)
odoo-ce up

# View logs
odoo-ce logs

# Check status
odoo-ce ps

# Restart Odoo
odoo-ce restart odoo

# Shell into container
odoo-ce sh odoo
```

**Launch Claude Code in canonical sandbox:**

```bash
# This wrapper ensures Claude starts in sandbox/dev
claude-odoo-ce
```

---

## Why This Matters

1. **Data Persistence**: Work in `~/Documents/GitHub/odoo-ce` is permanent
2. **Git Integration**: Changes are tracked and backed up to GitHub
3. **No Surprises**: Periodic Downloads cleanup won't delete your sandbox
4. **Deterministic**: All tools and scripts use the same canonical path

---

## Verification

Run this to verify you're using the canonical location:

```bash
# Should print: /Users/tbwa/Documents/GitHub/odoo-ce/sandbox/dev
odoo-ce cwd | grep sandbox
```

If you see `Downloads/extracted_files` in any path, you're using the **wrong location**.

---

## Current Working Directory

When in doubt, always cd to the canonical sandbox:

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
```

Or use the alias:

```bash
odoo-ce cwd  # Prints canonical path
cd $(odoo-ce cwd | tail -1)  # Navigate to it
```

---

**Last Updated**: 2025-01-15
**Canonical Location**: `~/Documents/GitHub/odoo-ce`
**Never Use**: `~/Downloads/extracted_files/*` (temporary, will be cleaned)
