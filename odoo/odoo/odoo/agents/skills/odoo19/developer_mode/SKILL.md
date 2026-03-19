---
name: developer_mode
description: Activate debug/developer mode to access advanced tools, technical menus, and debugging features.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# developer_mode — Odoo 19.0 Skill Reference

## Overview

Developer mode (also called debug mode) unlocks advanced tools and technical settings in Odoo that are hidden by default. It provides access to field technical names, view structures, record metadata, the Technical menu in Settings, and model/action inspection tools. Developers, administrators, and technical consultants use it for debugging, customization, and advanced configuration. It also has variants for JavaScript asset debugging and test tour execution.

## Key Concepts

- **Developer mode**: Standard debug mode exposing technical menus and the bug icon toolbar.
- **Developer mode with assets**: Loads unminified JavaScript/CSS for frontend debugging (`?debug=assets`).
- **Developer mode with tests**: Loads test assets for running test tours (`?debug=tests`).
- **Bug icon menu**: A toolbar accessible via the bug icon in the top bar (when dev mode is active). Shows contextual technical information about the current view — fields, filters, actions, XML IDs.
- **Technical menu**: Section in Settings app exposing advanced database configuration — sequences, email settings, system parameters, actions, views, etc.
- **Command palette**: `Ctrl+K` / `Cmd+K` keyboard shortcut; typing "debug" toggles developer mode with assets.

## Core Workflows

### 1. Activate developer mode via Settings

1. Open the **Settings** app.
2. Scroll to **Developer Tools** section.
3. Click **Activate the developer mode**.
4. To deactivate: click **Deactivate the developer mode** in the same location.

### 2. Activate via URL

1. Append `?debug=1` to the database URL (e.g., `https://example.odoo.com/odoo?debug=1`).
2. To deactivate: use `?debug=0`.
3. Variants: `?debug=assets` (with assets), `?debug=tests` (with test assets).

### 3. Activate via command palette

1. Press `Ctrl+K` (or `Cmd+K` on macOS).
2. Type `debug`.
3. Select the option to activate with assets or deactivate.

### 4. Use developer tools (bug icon)

1. With developer mode active, click the bug icon in the top bar.
2. Inspect field definitions, view XML IDs, filters, and actions relevant to the current page.

### 5. Access the Technical menu

1. With developer mode active, open the Settings app.
2. The **Technical** section appears in the menu with sub-items: Sequences, System Parameters, Actions, Views, Email, etc.

## Technical Reference

### URL Parameters

| Parameter | Effect |
|-----------|--------|
| `?debug=1` | Activate developer mode |
| `?debug=0` | Deactivate developer mode |
| `?debug=assets` | Activate with unminified JS/CSS |
| `?debug=tests` | Activate with test tour assets |

### Browser Extension

- **Odoo Debug** extension: Toggle developer mode from browser toolbar.
- Available on Chrome Web Store and Firefox Add-ons.
- GitHub: `https://github.com/Droggol/OdooDebug`

### Menu Paths (when active)

- `Settings > Technical > Parameters > System Parameters`
- `Settings > Technical > Email > Outgoing Mail Servers`
- `Settings > Technical > Email > Alias Domains`
- `Settings > Technical > Actions > Server Actions`
- `Settings > Technical > Database Structure > Models`
- `Settings > Users & Companies > Groups`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Unintended changes**: Developer tools expose settings that can break the database if modified carelessly. Only use if you understand the implications.
- **Assets mode performance**: Developer mode with assets loads unminified files, significantly slowing the frontend. Disable when not actively debugging JavaScript.
- **Not persisted across sessions**: Developer mode activation via URL does not persist; it resets on the next navigation or logout unless activated via Settings.
- **Technical menu visibility**: The Technical menu only appears in the Settings app, not in other application menus.
