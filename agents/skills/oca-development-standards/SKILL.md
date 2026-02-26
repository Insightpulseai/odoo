---
name: oca-development-standards
description: Elite OCA (Odoo Community Association) development and review standards. Use for forking, module scaffolding, PR management, and peer reviews.
license: AGPL-3
metadata:
  author: InsightPulseAI
  version: "1.0.0"
---

# OCA Development & Review Standards

Adhering to the Odoo Community Association's elite quality and collaboration standards.

## 1. Module Development Standards

- **Manifest**: Use strict versioning (`[Odoo Version].[Major].[Minor].[Patch].[Revision]`).
- **Licensing**: Default to `AGPL-3` unless specified otherwise.
- **Linting**: All modules must pass `Pylint-Odoo` and `Flake8`.
- **Naming**: Directory name must match module technical name. Prefix custom modules with `ipai_` if applicable, but follow OCA prefixing for community contributions.

## 2. GitHub & PR Workflow

- **Branch Strategy**: One branch per feature/bugfix. Target the specific Odoo version branch (e.g., `18.0`, `19.0`).
- **Commits**: Clear, atomic commits with descriptive messages.
- **PR Description**: Must contain a clear summary and a test scenario.
- **Quality Gates**: All automated tests (MQT/Travis/GHA) must be green before requesting review.

## 3. Review Process (Peer Review)

- **Tooling**: Use `Runboat` (or `Runbot`) to test the contribution in a live instance.
- **Testing Databases**:
  - `baseonly`: To test installation in a clean environment.
  - `all modules`: To test integration and potential conflicts.
- **Review Feedback**:
  - **Approve**: Only after manual verification and code audit.
  - **Request Changes**: Provide clear, actionable feedback with code snippets if possible.
- **Merge Threshold**: 3 positive reviews within 5 days is the gold standard for OCA modules.

## 4. Quality Assurance (QA)

- **Coverage**: Aim for 100% test coverage with Odoo unit tests.
- **Documentation**: Include `README.rst` or `static/description/index.html`.
- **Security**: Strict enforcement of `ir.model.access.csv` and Record Rules.

## Integration Checklist

- [ ] Is the license correctly set to AGPL-3?
- [ ] Does the version number match the OCA/IPAI standard?
- [ ] Has the module been tested on a clean database (`baseonly`)?
- [ ] Are all Pylint-Odoo warnings resolved?
