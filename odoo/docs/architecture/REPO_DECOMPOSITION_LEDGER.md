# Repo Decomposition Ledger

This file tracks top-level directories currently present in `Insightpulseai/odoo` that do not belong permanently to the ERP runtime boundary.

## Status classes

- KEEP: required for ERP runtime, build, deploy, test, or ERP governance
- MOVE: should be migrated to another canonical repo
- REVIEW: ownership unclear; requires bounded decision
- ARCHIVE: legacy/obsolete and should not remain active

## Current classification

### KEEP
- addons
- config
- docker
- scripts
- tests
- docs
- spec
- ssot
- .github
- .devcontainer
- deploy
- db
- data
- audit
- evidence
- security
- contracts
- seeds
- oca-aggregate.yml
- oca.lock.json
- requirements*.txt
- pyproject.toml
- docker-compose*.yml
- Dockerfile
- odoo-bin
- Makefile

### MOVE → `agents`
- skills
- skillpack
- prompts
- third_party/anthropic_skills
- agent-library
- agent-library-pack
- contains-studio-agents
- docs-assistant

### MOVE → `web`
- apps
- marketplace
- figma
- design
- docflow-agentic-finance
- api
- clients

### MOVE → `infra`
- pipelines/templates
- artifacts/dns
- ops
- fastlane

### MOVE → `ops-platform`
- supabase
- platform
- ipai-platform
- packages
- schemas

### MOVE → `lakehouse`
- src/lakehouse
- dbt
- datasets
- eval

### MOVE → `automations`
- automations
- notion-n8n-monthly-close
- calendar

### REVIEW
- architecture-review
- baselines
- catalog
- registry
- runtime
- services
- tools
- vendor
- work
- platform-kit
- releasekit
- parity
- reports
- memory
- handbook
- kb

### ARCHIVE / DELETE CANDIDATES
- odoo19
- odoo-schema-mirror
- dot-github-repo
- dev
- archive
- odoo (residue from previous normalization attempts)
