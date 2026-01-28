# GitHub Personal Access Token (PAT) Scopes

## Required Scopes for odoo-ce Repository Operations

### Minimum Scopes (Read/Write Operations)

```
✅ repo (Full control of private repositories)
   ├── repo:status
   ├── repo_deployment
   ├── public_repo
   └── repo:invite

✅ workflow (Update GitHub Action workflows)

✅ codespace (Full control of codespaces)
   ├── codespace:secrets

✅ admin:org (Read/Write access to organization membership)
   ├── write:org
   └── read:org

✅ project (Full control of projects)
```

### Current PAT Configuration

**Token Name**: `GITHUB_TOKEN` (stored in `~/.zshrc`)
**Organization**: tbwa-smp
**Repository**: jgtolentino/odoo-ce

### Adding `codespace` Scope

**Step 1: Go to Token Settings**
1. Navigate to: https://github.com/settings/tokens
2. Find your current token (or click "Generate new token (classic)")

**Step 2: Update Scopes**
1. Check the **`codespace`** scope
2. Under `codespace`, ensure **`codespace:secrets`** is also checked
3. Click "Update token" or "Generate token"

**Step 3: Update Local Environment**
```bash
# Copy the new token
export GITHUB_TOKEN=ghp_NEW_TOKEN_HERE

# Add to ~/.zshrc permanently
echo 'export GITHUB_TOKEN=ghp_NEW_TOKEN_HERE' >> ~/.zshrc
source ~/.zshrc

# Test authentication
gh auth status
```

**Step 4: Run Setup Script**
```bash
cd /Users/tbwa/odoo-ce
./scripts/setup-codespaces-secrets.sh
```

### Fine-Grained PAT Alternative (Future)

GitHub now supports fine-grained tokens with repository-specific permissions:

**Permissions Needed:**
- **Repository access**: jgtolentino/odoo-ce
- **Repository permissions**:
  - Codespaces: Read and write
  - Codespaces secrets: Read and write
  - Contents: Read and write
  - Pull requests: Read and write
  - Workflows: Read and write

**Advantages:**
- More granular control
- Expire after 1 year (better security)
- No organization-wide access needed

**Create at**: https://github.com/settings/personal-access-tokens/new

### Verification

**Test Codespaces Secret Access:**
```bash
# List existing secrets (should work now)
gh secret list --repo jgtolentino/odoo-ce --app codespaces

# Set test secret
echo "test-value" | gh secret set TEST_SECRET --repo jgtolentino/odoo-ce --app codespaces

# Delete test secret
gh secret delete TEST_SECRET --repo jgtolentino/odoo-ce --app codespaces
```

**Expected Output:**
```
✓ Set secret TEST_SECRET for jgtolentino/odoo-ce
```

### Troubleshooting

**403 Forbidden Error:**
- Cause: PAT missing `codespace` scope
- Solution: Update token scopes as described above

**401 Unauthorized Error:**
- Cause: Token expired or invalid
- Solution: Regenerate token at https://github.com/settings/tokens

**Resource Not Accessible:**
- Cause: Token doesn't have access to repository
- Solution: Check token has `repo` scope and organization membership

### Security Best Practices

1. **Scope Minimization**: Only grant necessary scopes
2. **Token Rotation**: Rotate tokens every 90 days
3. **Separate Tokens**: Use different tokens for different purposes
4. **Audit Logs**: Review token usage in https://github.com/settings/security-log
5. **Expiration**: Set expiration dates on all tokens

### Related Documentation

- [GitHub PAT Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Codespaces Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-secrets-for-your-codespaces)
- [Fine-Grained PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
