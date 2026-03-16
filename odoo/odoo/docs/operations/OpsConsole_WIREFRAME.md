# Ops Console Wireframe Specification

This document defines the wireframe and layout for the **OdooOps Console**, mirroring the core visibility surfaces of Odoo.sh while providing advanced "Engineering System Success" visibility.

## Layout Anatomy

### [Global Shell]

- **Sidebar (Left, 240px)**: Persistent navigation (Overview, Environments, Deployments, Gates, Modules, Logs, Runbooks).
- **Topbar (Top, 56px)**: Repo identifier (`Insightpulseai/odoo`), environment chip, health status, and user profile.
- **Content Area (12-col grid)**: Dynamic page content with responsive behavior.

## Core Screens

### 1. Overview Dashboard

- **KPI Cards**: Prod/Stage versions, Health status, DB status, Policy status.
- **Timeline**: Chronological list of the last 20 deployment events.
- **Drift Alerts**: Visual indicators for diagram or allowlist drift.

### 2. Environments Table

| Env       | Host      | DB         | SHA    | Health | Last Deploy |
| :-------- | :-------- | :--------- | :----- | :----- | :---------- |
| **PROD**  | 178...214 | odoo_prod  | v1.4.2 | Green  | 2h ago      |
| **STAGE** | local/dev | odoo_stage | main   | Green  | 4h ago      |

### 3. Deployments Feed

- **Filters**: Env, Status, Author.
- **List Item**: Deploy ID, Env, SHA/Tag, Status (Success/Failed), Duration, Author.
- **Detail View (Drawer)**: Preflight logs, Gate results, Build artifacts.

### 4. Policy Gates

- **Cards**: Single card per gate (OCA Allowlist, Risk-Tier, Diagrams Drift).
- **Status**: Latest result, Failing reasons (if any), Link to GitHub check run.

### 5. Module Waves

- **Wave Tabs (1-4)**: Lists modules in each wave.
- **Install Status**: Staging verified? Prod installed?
- **Evidence**: Links to build artifacts/logs.

## Design Tokens (Tokens.json)

- **Primary**: #2563EB (OdooOps Blue)
- **Success**: #10B981 (Green)
- **Warning**: #F59E0B (Amber)
- **Error**: #EF4444 (Red)
- **Bg-Gray**: #F9FAFB
