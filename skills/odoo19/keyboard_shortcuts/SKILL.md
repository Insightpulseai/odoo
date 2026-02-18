---
name: keyboard_shortcuts
description: Keyboard shortcuts for navigation, record management, and the command palette in Odoo.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# keyboard_shortcuts — Odoo 19.0 Skill Reference

## Overview

Odoo provides keyboard shortcuts for navigating modules, managing records, and accessing features quickly. Shortcuts cover actions like creating records, saving changes, navigating breadcrumbs, searching, and opening the command palette. They vary slightly between Windows/Linux and macOS. Holding `Ctrl` reveals shortcut labels overlaid on UI elements. All Odoo users benefit from these shortcuts for faster daily workflows.

## Key Concepts

- **Command palette**: Global search/command interface opened with `Ctrl+K` / `Cmd+K`. Supports prefixed searches for menus (`/`), users (`@`), Discuss channels (`#`), and Knowledge articles (`?`).
- **Shortcut overlay**: Holding `Ctrl` displays the keyboard shortcuts assigned to each visible UI element.
- **Cross-platform**: Windows/Linux shortcuts use `Alt`; macOS shortcuts use `Ctrl` (not `Cmd`, except for the command palette).

## Core Workflows

### 1. Discover available shortcuts

1. Hold `Ctrl` while viewing any page.
2. Shortcut keys appear overlaid on buttons, menus, and actions.

### 2. Use the command palette

1. Press `Ctrl+K` (Windows/Linux) or `Cmd+K` (macOS).
2. Type directly to search, or use prefixes:
   - `/` — search menus, apps, modules
   - `@` — search users
   - `#` — search Discuss channels
   - `?` — search Knowledge articles
3. Use arrow keys to scroll results.
4. Press `Ctrl+Enter` to open in a new tab.

## Technical Reference

### Shortcut Table

| Action | Windows / Linux | macOS |
|--------|----------------|-------|
| Previous breadcrumb | `Alt+B` | `Ctrl+B` |
| Create new record | `Alt+C` | `Ctrl+C` |
| Odoo Home Page | `Alt+H` | `Ctrl+H` |
| Discard changes | `Alt+J` | `Ctrl+J` |
| Save changes | `Alt+S` | `Ctrl+S` |
| Next page | `Alt+N` | `Ctrl+N` |
| Previous page | `Alt+P` | `Ctrl+P` |
| Search | `Alt+Q` | `Ctrl+Q` |
| Select menus (1-9) | `Alt+1-9` | `Ctrl+1-9` |
| Create a new To-Do | `Alt+Shift+T` | `Ctrl+Shift+T` |
| Search Knowledge article | `Alt+F` | `Ctrl+F` |
| Share Knowledge article | `Alt+Shift+S` | `Ctrl+Shift+S` |
| Open command palette | `Ctrl+K` | `Cmd+K` |

### Command Palette Prefixes

| Prefix | Searches |
|--------|----------|
| `/` | Menus, applications, modules |
| `@` | Users |
| `#` | Discuss channels |
| `?` | Knowledge articles |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Browser/extension conflicts**: Some shortcuts may be intercepted by the browser or browser extensions, making them ineffective. Check for conflicts if a shortcut does not work.
- **Version-dependent availability**: Not all shortcuts are available on every Odoo version; behavior may vary.
- **macOS Ctrl vs. Cmd**: Most macOS shortcuts use `Ctrl`, not `Cmd`. Only the command palette uses `Cmd+K`.
- **Knowledge shortcuts require app**: The Knowledge article shortcuts only work when the Knowledge app is installed.
