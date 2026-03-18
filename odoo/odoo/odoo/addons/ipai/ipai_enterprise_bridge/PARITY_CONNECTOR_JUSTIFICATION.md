# Connector Justification: ipai_enterprise_bridge

## What this module does
Replaces Odoo Enterprise/IAP features with CE+OCA alternatives, providing IoT device management with MQTT bridging, HR expense integration, maintenance equipment tracking, project task automation, month-end close checklists, OAuth provider configuration, mail server setup, and a webhook utility layer.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module reaches 2,055 LOC because it bridges twelve distinct Enterprise feature gaps across unrelated Odoo domains: IoT devices (98 LOC) + MQTT bridge (100 LOC), HR expense integration (180 LOC), maintenance equipment (147 LOC), project task automation (221 LOC), close checklists (101 LOC), job queue (150 LOC), policy management (52 LOC), Mailgun mailgate controller (309 LOC), AI mixin (54 LOC), purchase order extensions (37 LOC), product template extensions (48 LOC), and centralized config settings (139 LOC). Each integration target requires its own model and business logic.

## Planned reduction path
- Split into domain-specific sub-addons: `ipai_iot_bridge`, `ipai_hr_bridge`, `ipai_maintenance_bridge`, `ipai_project_bridge`
- Extract the Mailgun mailgate controller (309 LOC) into a standalone `ipai_mailgate` addon
- Move shared utilities (`ipai_webhook.py`, `ipai_job.py`) into a common `ipai_core` library module
