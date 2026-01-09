# claude.md (Cloud-Agent Contract for Odoo 18 CE + OCA Repos)

## Operating Mode

You are running inside a **cloud sandbox IDE** (Claude Code Web / VS Code Cloud / Codespaces-like).
**Assume all tools are available in this sandbox** unless explicitly stated otherwise:
- git, bash, python3, node (optional), pip
- docker + docker compose
- ability to run background services/ports inside the sandbox
- ability to create PRs and push branches
- ability to run CI-equivalent checks locally

**NEVER say** "Docker/CLI is not available in this environment."
If Docker is unavailable, **detect it and fall back** automatically (see Fallbacks).

---

## Repo is Source of Truth (OCA-style)

This repo follows **OCA-style distribution**:
1. Odoo CE core first
2. OCA deps second (18.0 only)
3. Third-party deps after OCA
4. Custom addons last

All scripts/config must be committed and used by CI and deploy runners.
**No manual UI steps. No "click here in Odoo UI" instructions.**

---

## Environment Detection (no guessing, no questions)

Before executing, run:
```bash
which docker || true
docker version || true
python3 --version
git status --porcelain
```

Then choose the right runner path automatically:
- If Docker is available and container `odoo-ce` exists: use `docker exec`
- Else: run `./odoo/odoo-bin` with `-c ./config/odoo.conf`

---

## Dependency Strategy (choose automatically)

**Preferred**: git-aggregator if `oca-aggregate.yml` exists:
```bash
./scripts/sync_oca.sh
```

**Else**: submodules:
```bash
git submodule sync --recursive
git submodule update --init --recursive
```

---

## Deterministic Addons Path (no globs)

Odoo does not support wildcards in `addons_path`.
Use:
```bash
python3 scripts/gen_addons_path.py
```

and pass it explicitly to `odoo-bin` or ensure config is generated with the expanded list.

---

## Module Install/Upgrade Contract (no UI)

All module install/upgrade actions must be scripted and non-interactive:

1. **Gate first** (dry-run): `./scripts/ci_gate/gate_modules.sh`
2. **Apply second**: `./scripts/odoo_update_modules.sh`
3. **Verify third**: `./scripts/run_odoo_shell.sh scripts/odoo_verify_modules.py`

---

## "Never Block" Policy

You must always proceed with the best available execution path:
- If docker is missing: fallback to `odoo-bin`
- If `odoo-bin` missing: fail with an actionable error (paths to check)
- If ports are blocked: run `--stop-after-init` checks and provide logs

---

## Output Format (required)

Every response must include:
1. **Commands executed** (copy/paste)
2. **Result/proof commands**
3. **Next deterministic action** if a step fails

---

## Forbidden Behaviors

- Do not claim tools are unavailable without running the detection commands.
- Do not require manual UI steps (Odoo Settings clicks, etc.).
- Do not introduce non-OCA repo layouts.
- Do not broaden scope (no repo-wide refactors) while fixing a targeted issue.

---

## Standard Verification Commands

```bash
# Check for merge conflicts
git grep -n "<<<<<<<\\|=======\\|>>>>>>>" || true

# Verify addons path
python3 scripts/gen_addons_path.py | tr ',' '\n' | head -50

# Check running containers
docker ps --format '{{.Names}}' | head -50 || true

# Verify repo structure
./scripts/repo_health.sh || true
```

---

## Fallback Execution Matrix

| Condition | Action |
|-----------|--------|
| Docker available + `odoo-ce` running | `docker exec -i odoo-ce odoo shell -d $DB < script.py` |
| Docker available + container stopped | `docker compose up -d && docker exec ...` |
| Docker unavailable + `odoo-bin` exists | `./odoo/odoo-bin shell -d $DB -c ./config/odoo.conf < script.py` |
| Neither available | Fail with: "Install Docker or set ODOO_BIN path" |

---

## CI/CD Integration

All changes must pass these gates before merge:
1. `./scripts/repo_health.sh` - Repo structure check
2. `./scripts/spec_validate.sh` - Spec bundle validation
3. `./scripts/ci_gate/gate_modules.sh` - Module manifest/deps validation
4. `./scripts/ci_local.sh` - Full local CI suite

---

## SMTP/Email Configuration

Email configuration is **environment-driven** (no secrets in repo):

```bash
# Set environment variables
export SMTP_HOST=smtp.mailgun.org
export SMTP_PORT=2525
export SMTP_USER=postmaster@mg.example.com
export SMTP_PASSWORD=your-password

# Run configuration
./scripts/run_odoo_shell.sh scripts/configure_smtp.py

# Verify
./scripts/run_odoo_shell.sh scripts/verify_smtp.py
```

---

## Production Deployment

Production deployments happen via GitHub Actions workflows:
- `prod-configure-smtp.yml` - Configure SMTP
- `prod-odoo-modules.yml` - Install/upgrade modules

Secrets are stored in GitHub Actions, never in repo.

---

*Last updated: 2026-01-09*
