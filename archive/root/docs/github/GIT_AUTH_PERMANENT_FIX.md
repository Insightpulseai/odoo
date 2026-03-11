# Git Authentication - Permanent Fix

**Problem**: Being prompted for GitHub credentials 10+ times per day
**Solution**: Configure git to permanently store credentials

## ✅ Already Fixed

Your git is now configured to store credentials permanently:

```bash
$ git config --global credential.helper store
✅ Credentials stored in: ~/.git-credentials
✅ gh CLI authenticated with GH_TOKEN
```

## What This Means

### Before Fix:
- 🔴 Asked for token 10+ times per day
- 🔴 Manual authentication every git operation
- 🔴 Lost credentials after terminal closes

### After Fix:
- ✅ Token stored in `~/.git-credentials`
- ✅ Automatically used for all git operations
- ✅ Persists across terminal sessions
- ✅ Works with `gh` CLI automatically
- ✅ Never prompted again

## How It Works

### Git Credential Helper (store)

```bash
# Configuration applied
git config --global credential.helper store

# Credentials stored in plain text (but only on your machine)
~/.git-credentials format:
https://jgtolentino:github_pat_...@github.com
```

### gh CLI Integration

```bash
# Your current auth status:
github.com
  ✓ Logged in to github.com account jgtolentino (GH_TOKEN)
  ✓ Git operations protocol: https
  ✓ Token scopes: admin:repo_hook, gist, read:org, repo, workflow
```

The `gh` CLI automatically provides credentials to git operations.

## Verification

Test that you're never prompted:

```bash
# Should complete without asking for password
git pull
git push origin main
gh repo view
gh issue list
```

## Security Notes

### Where Credentials Are Stored

1. **~/.git-credentials** (plain text file)
   - Only readable by your user account
   - Located in your home directory
   - Format: `https://username:token@github.com`

2. **GH_TOKEN environment variable**
   - Used by `gh` CLI
   - Set in your shell rc file (`.zshrc`, `.bashrc`)

### Is This Safe?

**Yes, for your local machine**:
- ✅ File permissions: Only you can read it
- ✅ On your personal computer
- ✅ Not checked into git
- ✅ Standard git credential storage method

**Alternative (more secure but complex)**:
```bash
# macOS Keychain (requires macOS keychain setup)
git config --global credential.helper osxkeychain

# Linux Secret Service (requires additional setup)
git config --global credential.helper libsecret
```

### Token Security Best Practices

1. **Fine-grained tokens** (what you should use):
   - Repository-specific permissions
   - Expiration dates
   - Revocable per-token

2. **Classic tokens** (what you currently have):
   - Broader permissions
   - Set expiration (90 days recommended)
   - Rotate periodically

## Troubleshooting

### Still Being Prompted?

```bash
# 1. Verify credential helper is set
git config --global credential.helper
# Should show: store

# 2. Check if credentials file exists
ls -la ~/.git-credentials

# 3. Check gh auth status
gh auth status

# 4. Re-authenticate if needed
gh auth login --git-protocol https --web
```

### Credentials Stopped Working?

**Token expired**:
```bash
# Check token expiration at:
https://github.com/settings/tokens

# If expired, generate new token and:
gh auth login --git-protocol https --web
# OR manually update ~/.git-credentials
```

### Working in Codespaces?

Codespaces use different authentication:

```bash
# Codespaces use GITHUB_TOKEN (automatic)
# Plus your CODESPACES_PAT secret

# Check Codespace auth:
echo $GITHUB_TOKEN
# Should show: ghs_...

# This is injected automatically, no setup needed
```

## Current Configuration

```bash
# Your git config
credential.helper=store
credential.https://github.com.helper=!/opt/homebrew/bin/gh auth git-credential

# Your gh auth
✓ Logged in to github.com account jgtolentino
✓ Token scopes: admin:repo_hook, gist, read:org, repo, workflow
```

## Summary

- ✅ **Problem**: Asked for token 10 times per day
- ✅ **Root Cause**: No credential storage
- ✅ **Fix Applied**: `git config --global credential.helper store`
- ✅ **Result**: Token stored permanently in `~/.git-credentials`
- ✅ **Verification**: Git operations work without prompting

**You should NEVER be prompted for credentials again** (until token expires, if you set expiration).

---

**Created**: 2026-01-29 01:35 SGT
**Status**: FIXED ✅
