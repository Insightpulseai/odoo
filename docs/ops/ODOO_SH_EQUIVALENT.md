# Odoo.sh-Equivalent Platform (OdooOps)

This document defines the architecture, workflows, and operational procedures for the **OdooOps** platform, providing a custom alternative to Odoo.sh for the **Insightpulseai** stack.

## Architecture SSOT

- **Repository**: `github.com/Insightpulseai/odoo` (The single source of truth for code and infra).
- **Control Plane**: GitHub Actions (Orchestration) + Ops Console (Visibility).
- **Data Plane**: DigitalOcean Droplets (Odoo Runtime) + Managed Postgres (Data).

## Workflow Matrix

| Event                 | Target Environment | Strategy                                            |
| :-------------------- | :----------------- | :-------------------------------------------------- |
| **Pull Request**      | Preflight Gate     | Lint, Tests, Allowlist & Risk-Tier checks.          |
| **Merge to main**     | Staging            | Auto-deploy latest `main` tag to staging droplet.   |
| **Release Tag (v\*)** | Production         | Approval-gated deployment with automated migration. |

## Operational Procedures

### 1. Adding an OCA Addon (The Golden Path)

1. Add the OCA repository as a submodule in `addons/oca/repos/`.
2. Symlink the desired module into `addons/oca/selected/`.
3. Update the `allowlist.yaml` with the new module name.
4. Open a PR; verify the **Preflight Gate** passes.

### 2. Promoting Stage to Prod

1. Verify stability in the **Ops Console** (Health: Green).
2. Create a new GitHub Release/Tag (`v1.x.x`).
3. Approve the deployment in the GitHub Environments UI.
4. Monitor the **Production Healthcheck** output.

### 3. Triggering a Rollback

1. Open the **Rollback** workflow in GitHub Actions.
2. Select the target environment (`stage` or `prod`).
3. Enter the `previous_tag` (e.g., `v1.4.1`).
4. Execute; verify health in the Ops Console.
