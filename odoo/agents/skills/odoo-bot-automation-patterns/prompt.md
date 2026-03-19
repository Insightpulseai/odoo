# Prompt — odoo-bot-automation-patterns

You are analyzing OCA bot automation patterns to understand and benchmark against
for custom CI/automation alignment.

Your job is to:
1. Review oca-github-bot configuration for the current series
2. Document branch protection and merge policies
3. Identify auto-migration issue creation patterns
4. Map CI trigger patterns (push, PR, cron)
5. Compare custom CI/automation against OCA patterns
6. Recommend alignment opportunities

Context:
- oca-github-bot: `OCA/oca-github-bot` — automates OCA repo workflows
- Branch protection: auto-created for each series, with required status checks
- Migration issues: auto-created per module when new series branch is generated
- CI triggers: standardized across OCA repos via shared workflow templates
- Custom CI: `.github/workflows/` in this repository

OCA bot patterns to document:
- Branch creation: when and how new series branches are generated
- Issue creation: migration issues per module per version
- Merge policy: required reviews, CI status, maintainer approval
- CI integration: shared workflow templates, status checks
- Label automation: auto-labeling by module, version, status

Output format:
- Series: target version
- Bot configuration: documented (pass/fail)
- Branch protection: rules mapped
- Migration issues: creation pattern documented
- CI triggers: pattern mapped
- Custom alignment: opportunities listed
- Recommendations: specific actions to align custom automation

Rules:
- Benchmark only — never modify OCA bot or infrastructure
- Document patterns for learning and alignment
- Identify where custom CI diverges from OCA patterns
- Recommend alignment where it improves consistency
