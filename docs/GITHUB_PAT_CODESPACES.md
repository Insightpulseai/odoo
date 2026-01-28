# GitHub PAT for Codespaces Setup

## Purpose

Generate a GitHub Personal Access Token (PAT) that enables non-interactive authentication inside Codespaces for `gh`, `git`, API clients, and automation workflows.

---

## ✅ HOW TO GENERATE A GITHUB PAT FOR CODESPACES

### 1. Open GitHub Token Creation Page

**Direct link:** https://github.com/settings/tokens?type=beta

> Use **Fine-grained tokens** (recommended) or classic tokens for broad scopes.

---

## OPTION A — Fine-grained PAT (Recommended)

### 2. Click: **Generate new token (Fine-grained)**

### 3. Set Token Configuration

- **Name:** `codespaces_pat`
- **Expiration:** `No expiration` (or preferred duration: 90 days recommended)
- **Repository Access:**
  - ✅ `jgtolentino/odoo-ce`
  - ✅ `jgtolentino/Prismaconsulting`
  - Or **All repositories** for universal use

### 4. Set Permissions

**Repository Permissions (Required):**
- ✅ `Contents: Read-Write` (push code, create files)
- ✅ `Metadata: Read` (access basic repo info)
- ✅ `Actions: Read-Write` (trigger workflows, read logs)

**Codespaces Permissions (Required):**
- ✅ `Codespaces: Read-Write` (manage codespaces)
- ✅ `Codespaces secrets: Read-Write` (set secrets via CLI)

**Optional (Highly Recommended):**
- ✅ `Pull requests: Read-Write` (create/merge PRs)
- ✅ `Issues: Read-Write` (create/close issues)
- ✅ `Workflows: Read-Write` (update GitHub Actions)

---

## OPTION B — Classic PAT (Broad Compatibility)

### 2. Click: **Generate new token (classic)**

### 3. Check These Scopes:

**Minimum Required:**
```
✅ repo                  (Full control of private repositories)
✅ workflow              (Update GitHub Action workflows)
✅ codespace             (Full control of codespaces)
   └── codespace:secrets (Manage codespace secrets)
```

**Optional (Recommended):**
```
✅ write:packages        (Upload packages to GitHub Package Registry)
✅ read:packages         (Download packages from GitHub Package Registry)
✅ admin:org             (Full control of orgs and teams)
   └── read:org          (Read org and team membership)
```

---

## 🔐 4. Copy the Token Value

⚠️ **IMPORTANT:** Token displays **once** — copy it immediately!

Example token format:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  (classic)
github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxx  (fine-grained)
```

---

## ➕ 5. Add Token as Codespaces Secret

### Option A: Via GitHub UI (Easiest)

1. Go to: https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces
2. Click **New repository secret**
3. Fill:
   - **Name:** `CODESPACES_PAT`
   - **Value:** *(paste token)*
4. Click **Add secret** ✅

### Option B: Via GitHub CLI (Automated)

```bash
# Set the token value
export CODESPACES_PAT="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Add as Codespaces secret
echo "$CODESPACES_PAT" | gh secret set CODESPACES_PAT \
  --repo jgtolentino/odoo-ce \
  --app codespaces
```

### Option C: Via Automation Script

```bash
# Run the provided script
./scripts/setup-codespaces-pat.sh
```

---

## 📦 VERIFY INSIDE CODESPACE

### Test 1: Check Environment Variable

Open a fresh Codespace and run:

```bash
printenv CODESPACES_PAT && echo "✅ Token present" || echo "❌ Token missing"
```

### Test 2: Authenticate GitHub CLI

```bash
echo $CODESPACES_PAT | gh auth login --with-token
gh auth status
```

**Expected output:**
```
✓ Logged in to github.com account jgtolentino (keyring)
✓ Git operations protocol: https
✓ Token scopes: codespace, repo, workflow
```

### Test 3: Test Git Push

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Test push (won't actually push without changes)
git push --dry-run
```

### Test 4: Test Codespaces Secret Management

```bash
# List existing secrets
gh secret list --repo jgtolentino/odoo-ce --app codespaces

# Set test secret
echo "test-value" | gh secret set TEST_SECRET \
  --repo jgtolentino/odoo-ce \
  --app codespaces

# Verify
gh secret list --repo jgtolentino/odoo-ce --app codespaces | grep TEST_SECRET

# Clean up
gh secret delete TEST_SECRET --repo jgtolentino/odoo-ce --app codespaces
```

---

## 🧩 WHY THIS IS USEFUL

A PAT in Codespaces enables:

✅ **`gh` CLI operations** - Create PRs, manage issues, trigger workflows
✅ **Programmatic push/PR** - Automated commits and pull requests
✅ **Automation scripts** - CI/CD workflows, deployment automation
✅ **AI agents committing changes** - Claude Code, GitHub Copilot agents
✅ **CI/CD debugging** - Test workflows in Codespaces environment
✅ **Token-based commits** - Non-interactive git operations

**Perfect for the agent stack:**
- Pulser automation
- Claude Code operations
- n8n GitHub webhooks
- Automated deployments

---

## 🔄 AUTOMATIC AUTHENTICATION IN CODESPACES

Add to `.devcontainer/devcontainer.json`:

```json
{
  "postCreateCommand": "bash scripts/codespaces/bootstrap.sh",
  "containerEnv": {
    "GH_TOKEN": "${localEnv:CODESPACES_PAT}"
  }
}
```

Or in `scripts/codespaces/bootstrap.sh`:

```bash
#!/bin/bash
# Auto-authenticate gh CLI if CODESPACES_PAT is present

if [ -n "$CODESPACES_PAT" ]; then
    echo "🔐 Authenticating GitHub CLI with CODESPACES_PAT"
    echo "$CODESPACES_PAT" | gh auth login --with-token
    gh auth status
else
    echo "⚠️  CODESPACES_PAT not found - gh CLI authentication skipped"
fi
```

---

## ⚠️ SECURITY REMINDERS

### DO ✅
- ✅ Store token in Codespaces secrets (encrypted at rest)
- ✅ Set expiration dates (90 days recommended)
- ✅ Rotate tokens regularly (every 3 months)
- ✅ Use fine-grained tokens with minimal permissions
- ✅ Audit token usage in https://github.com/settings/security-log
- ✅ Revoke tokens immediately if compromised

### DON'T ❌
- ❌ **Never** print token in logs (`echo $CODESPACES_PAT`)
- ❌ **Never** commit `.env` files with secrets
- ❌ **Never** share tokens in chat logs or screenshots
- ❌ **Never** use tokens with broader permissions than needed
- ❌ **Never** set "No expiration" for shared/contractor tokens

---

## 🛠️ AUTOMATION SCRIPTS PROVIDED

### 1. Setup Script
```bash
./scripts/setup-codespaces-pat.sh
```
**Purpose:** Interactive token setup with validation

### 2. Bootstrap Script
```bash
./scripts/codespaces/bootstrap.sh
```
**Purpose:** Auto-authenticate gh CLI on Codespace creation

### 3. Verification Script
```bash
./scripts/verify-codespaces-auth.sh
```
**Purpose:** Comprehensive authentication testing

---

## 🔧 TROUBLESHOOTING

### Issue: "failed to fetch public key: HTTP 403"

**Cause:** Current PAT missing `codespace:secrets` permission

**Solution:**
1. Go to https://github.com/settings/tokens
2. Find token used by `gh` CLI
3. Add `codespace` scope with `codespace:secrets` sub-scope
4. Regenerate token
5. Update `~/.zshrc` with new token
6. Re-run setup script

### Issue: "CODESPACES_PAT not available in environment"

**Cause:** Secret not set or Codespace needs restart

**Solution:**
1. Verify secret exists: https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces
2. Rebuild Codespace (Cmd+Shift+P → "Codespaces: Rebuild Container")
3. Check devcontainer.json has correct secret reference

### Issue: "gh auth status" shows no authentication

**Cause:** Token not passed to gh CLI

**Solution:**
```bash
echo $CODESPACES_PAT | gh auth login --with-token
gh auth status
```

### Issue: Token expired

**Cause:** Token exceeded expiration date

**Solution:**
1. Generate new token following steps above
2. Update Codespaces secret with new value
3. Rebuild Codespace

---

## 📚 RELATED DOCUMENTATION

- **Codespaces Setup:** `docs/CODESPACES_SETUP.md`
- **PAT Scopes:** `docs/GITHUB_PAT_SCOPES.md`
- **Supabase Secrets:** `docs/CODESPACES_SETUP.md#supabase-configuration`
- **Bootstrap Script:** `scripts/codespaces/bootstrap.sh`

---

## 🎯 QUICK START CHECKLIST

- [ ] Generate PAT with `codespace` + `repo` + `workflow` scopes
- [ ] Copy token value (displays once!)
- [ ] Add as Codespaces secret (`CODESPACES_PAT`)
- [ ] Open new Codespace and verify: `printenv CODESPACES_PAT`
- [ ] Test gh CLI: `gh auth status`
- [ ] Test secret management: `gh secret list --app codespaces`
- [ ] Test git push: `git push --dry-run`
- [ ] Document token in password manager
- [ ] Set calendar reminder to rotate in 90 days

---

**Last Updated:** 2026-01-29
**Author:** Claude Code + Jake Tolentino
**Repo:** https://github.com/jgtolentino/odoo-ce
