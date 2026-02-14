# Infrastructure Well-Architected Assessment Report

**Date:** {{ DATE }}
**Assessor:** Automated Assessment System
**Score:** {{ SCORE }} / 4.0

## Executive Summary

This report details the findings of the automated assessment of the DigitalOcean/Docker/Cloudflare infrastructure against the Well-Architected Framework.

### Pillar Scores

| Pillar                     | Score                   | Weight | Status                   |
| :------------------------- | :---------------------- | :----- | :----------------------- |
| **Reliability**            | {{ RELIABILITY_SCORE }} | 0.25   | {{ RELIABILITY_STATUS }} |
| **Security**               | {{ SECURITY_SCORE }}    | 0.25   | {{ SECURITY_STATUS }}    |
| **Cost Optimization**      | {{ COST_SCORE }}        | 0.20   | {{ COST_STATUS }}        |
| **Operational Excellence** | {{ OPS_SCORE }}         | 0.15   | {{ OPS_STATUS }}         |
| **Performance Efficiency** | {{ PERF_SCORE }}        | 0.15   | {{ PERF_STATUS }}        |

## Critical Findings

> [!IMPORTANT]
> The following issues require immediate attention (P0/P1).

- **[CHECK_ID]**: {{ DESCRIPTION }}
  - _Impact_: {{ IMPACT }}
  - _Remediation_: {{ REMEDIATION_STEPS }}

## Detailed Findings

### Reliability

- [ ] Docker Restart Policy: {{ STATUS }}
- [ ] Healthchecks: {{ STATUS }}
- [ ] Database Backups: {{ STATUS }}

### Security

- [ ] Secrets in Code: {{ STATUS }}
- [ ] Cloudflare Proxy: {{ STATUS }}

### Operations

- [ ] Logging Drivers: {{ STATUS }}
- [ ] Image Pinning: {{ STATUS }}

## Remediation Plan

Refer to `docs/runbooks/infra-waf-remediation.md` for detailed instructions on fixing the identified issues.
