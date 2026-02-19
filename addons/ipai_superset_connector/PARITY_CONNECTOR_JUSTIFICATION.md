# Connector Justification: ipai_superset_connector

## What this module does
Enterprise-grade Apache Superset integration for Odoo CE, providing direct PostgreSQL read-replica connections, managed SQL analytics views for Sales/Finance/HR/Inventory, dataset registry with Superset API sync, row-level security based on Odoo ir.rule, and a dataset creation wizard.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module reaches 2,035 LOC because it implements three large model classes -- analytics view management (567 LOC) with SQL view generation for multiple Odoo domains, Superset API connection handling (480 LOC) with authentication and health checks, and dataset registry (529 LOC) with column metadata and relationship mapping -- plus a multi-step dataset creation wizard (290 LOC) and configuration settings. Each model handles a distinct integration surface between Odoo and Superset.

## Planned reduction path
- Extract SQL view generation templates from `superset_analytics_view.py` into declarative YAML/SQL template files
- Split `superset_connection.py` into a thin API client class and a connection model
- Move the dataset wizard into a separate `ipai_superset_wizard` sub-addon or consolidate with the dataset model
