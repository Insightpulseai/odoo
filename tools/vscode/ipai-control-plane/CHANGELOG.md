# Changelog

All notable changes to the IPAI Control Plane extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-15

### Added

#### Control Plane Core
- **SaaS-grade control plane** for Odoo CE + OCA + IPAI development
- **Project & environment discovery** (dev/stage/prod isolation)
- **v1 API** with deterministic operations (plan → execute → evidence)

#### Operations
- **Install Modules** workflow with:
  - Pre-execution validation (naming, EE detection)
  - Diff preview (SQL schema + XML views)
  - Evidence bundle generation
  - Operation status tracking

#### Validators
- **Manifest validation** (`__manifest__.py`)
  - Required keys check
  - Dependency existence
  - EE-only module detection
- **XML validation**
  - Deprecated `<tree>` → `<list>` detection (Odoo 19+)
  - External ID collision scanner
  - View mode consistency
- **Security validation**
  - Access rule coverage
  - RLS (record rules) completeness

#### Tree Views
- **Projects & Environments** - Visual project/environment explorer
- **Validation Status** - Real-time validation results
- **Evidence Bundles** - Audit trail viewer

#### Developer Experience
- **Context menus** on environments (right-click → Install Modules)
- **Diff preview webview** with VS Code theming
- **Evidence bundles** with immutable audit trails
- **Real-time status polling** for long-running operations

### Infrastructure
- Python/FastAPI control plane server
- TypeScript VS Code extension (stateless)
- Vitest unit tests
- ESLint 9 + TypeScript strict mode
- CI/CD pipeline (lint → test → build → package)

### Documentation
- Complete Spec Kit bundle (constitution, prd, plan, tasks)
- API contract v0 specification
- Control plane README
- Extension README with usage examples

## [Unreleased]

### Planned Features
- Real Odoo execution (replace simulation)
- Database rollback (snapshot + restore)
- Migration operations
- Upgrade operations
- AI-assisted patch generation
- Enhanced diff syntax highlighting
- Web control plane UI
- Multi-runtime support

---

**Format**: `[version] - YYYY-MM-DD`

**Types of changes**:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
