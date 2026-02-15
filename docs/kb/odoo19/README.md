# Odoo 19 Knowledge Base (Upstream Indexed)

## Source of Truth

- Upstream: https://github.com/odoo/documentation/tree/19.0

## Pinning policy

- Maintain a pinned upstream commit SHA in: docs/kb/odoo19/UPSTREAM_PIN.json
- All generated indexes MUST reference the pinned SHA.

## Layout

docs/kb/odoo19/
UPSTREAM_PIN.json
upstream/ # vendored snapshot (or git submodule) at pinned SHA
index/
manifest.json # file list + hashes
sections.json # extracted headings/anchors
topics.json # topic map -> sources
skills_coverage.json # skill-id -> covered sources

## What is indexed

- Administration / Odoo.sh
- Developer docs (ORM, security, tests, QWeb, views/actions, JS/OWL, perf)
- Apps/Services (Project, Timesheets, Field Service, Helpdesk, Planning, Appointments)
