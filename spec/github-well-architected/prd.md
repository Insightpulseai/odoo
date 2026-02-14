# PRD: GitHub Well-Architected Assessment System

## Goal

Implement a systematic assessment framework to validate the repository against GitHub's Well-Architected Framework 5 pillars.

## Pillars

1. **Productivity (0.25)**: Generator determinism, CI efficiency, Makefile automation.
2. **Collaboration (0.20)**: Documentation currency, templates, CODEOWNERS.
3. **Application Security (0.25)**: Secrets, Dependabot, RLS, Branch protection.
4. **Governance (0.15)**: Drift gates, specs, approvals.
5. **Architecture (0.15)**: SSOT patterns, layer separation, determinism.

## Functional Requirements

- **Audit Script**: Python script to run checks and calculate scores.
- **Local Mode**: Run checks that don't need GitHub API (file existence, git metadata).
- **API Mode**: Run checks requiring GitHub API (settings, alerts).
- **Reporting**: Console summary + JSON evidence.
- **CI Gates**: Block PRs on critical violations or low maturity.

## Non-Functional Requirements

- **Performance**: Local checks < 10s.
- **Traceability**: All checks linked to WAF pillars.
- **Usability**: Clear error messages and remediation steps.
