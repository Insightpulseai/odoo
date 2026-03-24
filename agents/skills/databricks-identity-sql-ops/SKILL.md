---
name: databricks-identity-sql-ops
description: Manage Databricks identity, auth profiles, and SQL warehouses via CLI
microsoft_capability_family: "Azure / Databricks"
---

# Databricks Identity & SQL Ops Skill

## Purpose

Manage Databricks identity (auth profiles, users, groups, service principals) and SQL warehouses (warehouses, queries, dashboards) via the Databricks CLI (v0.205+).

## Owner

databricks-cli-operator

## Preconditions

- Databricks CLI v0.205+ installed
- Account-level admin permissions for identity operations
- SQL warehouse permissions for SQL operations

## Covered Operations

### Authentication Profiles

- `databricks auth profiles` — list configured authentication profiles
- `databricks auth login --host <host>` — configure authentication
- `databricks auth token --host <host>` — get current token (metadata only)
- `databricks auth env` — show authentication environment variables

### Users

- `databricks users list` — list workspace users
- `databricks users get --id <id>` — get user details
- `databricks users create --json <spec>` — create user
- `databricks users update --id <id> --json <spec>` — update user
- `databricks users delete --id <id>` — remove user (destructive)

### Groups

- `databricks groups list` — list workspace groups
- `databricks groups get --id <id>` — get group details
- `databricks groups create --json <spec>` — create group
- `databricks groups delete --id <id>` — delete group (destructive)

### Service Principals

- `databricks service-principals list` — list service principals
- `databricks service-principals get --id <id>` — get SP details
- `databricks service-principals create --json <spec>` — create SP
- `databricks service-principals delete --id <id>` — delete SP (destructive)

### SQL Warehouses

- `databricks warehouses list` — list SQL warehouses
- `databricks warehouses get --id <id>` — get warehouse details
- `databricks warehouses create --json <spec>` — create warehouse
- `databricks warehouses start --id <id>` — start warehouse
- `databricks warehouses stop --id <id>` — stop warehouse
- `databricks warehouses delete --id <id>` — delete warehouse (destructive)

### SQL Queries and Dashboards

- `databricks queries list` — list saved queries
- `databricks queries get --id <id>` — get query details
- `databricks dashboards list` — list dashboards
- `databricks dashboards get --id <id>` — get dashboard details

## Disallowed Operations

- Interactive SQL execution (use SQL warehouses via API/UI)
- Direct database/catalog creation (use Unity Catalog APIs)
- Workspace management (use databricks-workspace-ops)

## Output Contract

- All commands use `--output json`
- User/group/SP operations return SCIM-format objects
- Warehouse operations return `id`, `name`, `state`, `cluster_size`
- Query/dashboard operations return metadata objects

## Verification

- After user create: `users get` returns user details
- After warehouse create: poll `warehouses get` until state is `RUNNING`
- After warehouse stop: `warehouses get` shows state `STOPPED`
