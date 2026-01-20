# CI/CD with Supabase + n8n — Product Requirements

## Overview

Implement a unified CI/CD pipeline that orchestrates deployments across the InsightPulse AI stack:
- **Supabase**: Database migrations and Edge Functions
- **Odoo CE**: Custom modules and Docker deployments
- **n8n**: Workflow automation and orchestration

## Goals

1. **Automated Deployments**: Push to branch triggers appropriate deployments
2. **Smart Detection**: Only deploy components with actual changes
3. **Bidirectional Integration**: n8n can trigger and receive deployment events
4. **Observability**: Full audit trail of all deployments
5. **Safety**: Production deployments require approval

## User Stories

### As a Developer

- I want to push Supabase migrations and have them automatically deployed
- I want to push n8n workflow changes and have them synced to the n8n instance
- I want to see deployment status notifications in Slack/Mattermost

### As an Operator

- I want to trigger deployments from chat commands via n8n
- I want production deployments to require explicit approval
- I want all deployments logged for audit purposes

### As a DevOps Engineer

- I want path-based change detection to minimize unnecessary deployments
- I want parallel deployment of independent components
- I want rollback capability for failed deployments

## Functional Requirements

### FR1: Supabase CI/CD

| ID | Requirement | Priority |
|----|-------------|----------|
| FR1.1 | Auto-deploy migrations on push to main/develop | P0 |
| FR1.2 | Auto-deploy Edge Functions on push | P0 |
| FR1.3 | Validate migration syntax in PRs | P1 |
| FR1.4 | Support staging/production environments | P0 |
| FR1.5 | Notify n8n webhook on deployment | P1 |

### FR2: n8n Orchestration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR2.1 | Validate n8n workflow JSON on push | P0 |
| FR2.2 | Sync workflows to n8n instance via API | P1 |
| FR2.3 | Receive deployment notifications from GitHub Actions | P0 |
| FR2.4 | Trigger GitHub Actions via webhook | P1 |
| FR2.5 | Log deployments to Supabase | P1 |

### FR3: Unified Pipeline

| ID | Requirement | Priority |
|----|-------------|----------|
| FR3.1 | Path-based change detection | P0 |
| FR3.2 | Parallel deployment of independent components | P1 |
| FR3.3 | Unified deployment summary | P0 |
| FR3.4 | Manual workflow dispatch | P0 |
| FR3.5 | Environment-based deployment targets | P0 |

## Non-Functional Requirements

### Performance

- Deployment time: < 5 minutes for individual components
- Change detection: < 30 seconds
- Webhook response: < 2 seconds

### Reliability

- Pipeline success rate: > 99%
- Notification delivery: Best effort (non-blocking)
- Rollback time: < 5 minutes

### Security

- All secrets in GitHub Secrets
- No credential exposure in logs
- Production requires manual approval

## Success Metrics

| Metric | Target |
|--------|--------|
| Deployment frequency | > 5/day (staging) |
| Lead time for changes | < 30 minutes |
| Deployment success rate | > 95% |
| Mean time to recovery | < 15 minutes |

## Out of Scope

- Multi-region deployments
- Blue-green deployments
- Canary releases
- Custom approval workflows beyond Slack reactions
