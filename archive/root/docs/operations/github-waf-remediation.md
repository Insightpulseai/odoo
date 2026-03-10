# Runbook: GitHub WAF Remediation

## Overview

This runbook provides step-by-step instructions for resolving common failures detected by the GitHub Well-Architected Assessment System.

## P1: Productivity Failures

### `generator_scripts_exist`

**Issue:** Missing critical SSOT generator scripts (`gen_addons_path.sh`, `gen_dns_manifest.sh`).
**Fix:**

1. Check `scripts/` directory.
2. Restore missing scripts from `scripts/templates/` or git history.
3. Ensure they are executable (`chmod +x`).

### `makefile_automation`

**Issue:** Makefile missing standard targets (`install`, `test`, `deploy`).
**Fix:**
Add the following targets to `Makefile`:

```makefile
install:
	pip install -r requirements.txt

test:
	pytest

deploy:
	./scripts/deploy.sh
```

## P2: Collaboration Failures

### `readme_current`

**Issue:** README.md is stale (> 30 days).
**Fix:**
Update `README.md` with current project status, setup instructions, or recent changes. Commit the change.

### `codeowners_exists`

**Issue:** `.github/CODEOWNERS` is missing.
**Fix:**
Create `.github/CODEOWNERS` with at least:

```
* @owner-team
```

## P3: Security Failures

### `github_secrets_scanning_enabled`

**Issue:** GitHub Secret Scanning is disabled.
**Fix:**

1. Go to Repo Settings > Security & Analysis.
2. Enable "Secret scanning".

### `dependabot_enabled`

**Issue:** `.github/dependabot.yml` is missing.
**Fix:**
Create the file with standard config:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

### `supabase_rls_enabled`

**Issue:** No RLS enabling migration found.
**Fix:**
Create a new migration in `supabase/migrations/` that runs:

```sql
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
```

## P4: Governance Failures

### `drift_gates_exist`

**Issue:** No drift detection workflow found.
**Fix:**
Create `.github/workflows/drift-check.yml` that runs generators and asserts no git changes.

## P5: Architecture Failures

### `ssot_generators_exist`

**Issue:** See P1.

### `dependency_pinning`

**Issue:** No lock files found.
**Fix:**
Run `pip freeze > requirements.txt` or `npm install` to generate lock files. Commit them.
