---
name: apps_modules
description: Install, upgrade, and uninstall Odoo apps and modules from the Apps dashboard.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# apps_modules — Odoo 19.0 Skill Reference

## Overview

The Apps and Modules interface provides the central dashboard for managing Odoo applications and their underlying modules. From here, administrators can install new apps, upgrade existing ones to get new features from the current release, and uninstall apps that are no longer needed. The dashboard also surfaces dependency information — installing or removing one app may cascade to dependent modules. This is a core administrative function used during initial deployment, feature expansion, and database maintenance.

## Key Concepts

- **App**: A top-level Odoo application (CRM, Accounting, Inventory, etc.) that may depend on other modules.
- **Module**: A lower-level component that implements specific features; may be an app or a supporting module.
- **Extra filter**: By default, only Apps are shown. Selecting the **Extra** filter also displays supporting modules.
- **Dependencies**: An app may require other apps/modules. Installing one can auto-install dependencies; uninstalling one can cascade-remove dependents.
- **Activate**: Button on an app card to install the app.
- **Upgrade**: Updates the module code to the latest version within the current Odoo release, applying new improvements and features.
- **Uninstall**: Removes the app, its dependents, and **deletes their database records**.
- **Update Apps List**: Developer-mode function to refresh the available module list from disk.

## Core Workflows

### 1. Install an app

1. Open the **Apps** app from the main dashboard.
2. Search or scroll to find the desired app.
3. Click **Activate** on the app card.
4. If the app is not listed, enable developer mode > Apps > **Update Apps List** > Update.

### 2. Upgrade an app

1. Open the **Apps** app.
2. Find the app to upgrade.
3. Click the vertical ellipsis icon on the app card > **Upgrade**.

### 3. Uninstall an app

1. Open the **Apps** app.
2. Find the app to uninstall.
3. Click the vertical ellipsis icon > **Uninstall**.
4. Review the **Apps to Uninstall** section (tick "Show All" for complete dependency list).
5. Review the **Documents to Delete** section.
6. Click **Uninstall** to confirm.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `ir.module.module` | Module registry (installed, available, dependencies) |
| `ir.module.category` | Module categories |

### Key Fields on `ir.module.module`

| Field | Purpose |
|-------|---------|
| `name` | Technical module name |
| `shortdesc` | Human-readable name |
| `state` | installed, uninstalled, to upgrade, to install |
| `dependencies_id` | Module dependencies |

### Menu Paths

- Main dashboard > **Apps**
- Developer mode: Apps > **Update Apps List**

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Uninstall deletes data**: Uninstalling an app permanently removes all its database records. Always test on a duplicate database first.
- **Dependency cascades**: Uninstalling a base app (e.g., Point of Sale) also uninstalls dependent apps (e.g., Restaurant) and their data.
- **Subscription cost impact**: Installing apps can change subscription costs. Review before proceeding.
- **Hidden modules**: Supporting modules are not shown by default. Use the **Extra** filter to find them.
- **Update Apps List required**: Newly deployed modules on disk do not appear until the app list is refreshed (developer mode > Update Apps List).
