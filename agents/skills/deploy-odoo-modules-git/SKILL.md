# SKILL: Deploy Odoo Modules via Git

## Skill ID

deploy-odoo-modules-git

## Skill Type

Procedural (Deterministic)

## Purpose

Deploy Odoo modules from Git into a target environment using an Odoo.sh/Cloudpepper-grade, audit-first workflow.
This skill MUST be the only path for module deployment (no manual installs).

## Preconditions (MUST all hold)

1. ops.projects row exists for project_id
2. ops.environments row exists for environment_id and belongs to project_id
3. Caller has deploy permission for project_id via ops.user_has_permission()
4. No concurrent running ops.runs for environment_id
5. Repo reachable and branch/commit exists

## Inputs (required)

project_id: string
environment_id: string
repo_url: string
branch: string
commit_sha: string|null
modules: string[] # list of module technical names

## Outputs (required)

run_id: string
status: success|failed
evidence_dir: string # docs/evidence/<YYYY-MM-DD>/deploy/<run_id>/

## Non-negotiables

- Do NOT deploy to prod without a successful staging deploy (must verify last successful run on staging for same commit)
- Do NOT install Enterprise modules
- Do NOT skip manifest validation
- Do NOT reorder steps
- Do NOT suppress errors
- Always emit ops.run_events + evidence artifacts

## Execution Steps (ORDER IS MANDATORY)

### 1) Create ops run

- Insert ops.runs(status=queued, type=deploy_modules_git, payload=<inputs>)
- Emit run_id

### 2) Clone repository

- git clone --depth=1 --branch=<branch> <repo_url> /tmp/odoo-deploy/<run_id>
- if commit_sha: git checkout <commit_sha>
- Fail if repo/branch/commit not found

### 3) Validate modules

For each module:

- folder exists
- **manifest**.py exists
- manifest parses
- depends only CE/OCA allowed set
- reject enterprise markers/paths
- record manifest_checks.json

### 4) Record validation_passed event

- Insert ops.run_events(event_type=validation_passed, payload={modules,...})

### 5) Sync modules to addons path

- Copy modules into target addons mount (no deletes unless explicitly configured)

### 6) Restart Odoo (graceful)

- drain workers
- restart service
- wait for /web/health (or equivalent) to return 200

### 7) Install/Update modules

- If not installed: odoo-bin -d <db> -i <module> --stop-after-init
- If installed: odoo-bin -d <db> -u <module> --stop-after-init
- Dependency order must be honored (toposort)

### 8) Post-deploy validation

- registry load clean
- no traceback
- login page responds
- write final_status.json

### 9) Finalize run

- ops.runs.status=success|failed
- append ops.run_events(event_type=run_completed, payload={status,...})

## Evidence Outputs (REQUIRED)

Write to:
docs/evidence/<YYYY-MM-DD>/deploy/<run_id>/
Must include:

- inputs.json
- git_commit.txt
- validated_modules.json
- manifest_checks.json
- odoo_restart.log
- module_install.log
- final_status.json

Missing evidence => FAIL
