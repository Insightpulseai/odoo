# GitHub Well-Architected Assessment Report

**Date:** {{ date }}
**Assessor:** {{ assessor }}
**Outcome:** {{ outcome }} (Score: {{ total_score }}/4.0)

## Executive Summary

This report details the results of the GitHub Well-Architected Framework assessment for the current repository. The assessment evaluates maturity across 5 pillars: Productivity, Collaboration, Security, Governance, and Architecture.

## Scoring Summary

| Pillar            | Score (0-4)    | Weight   | Weighted Score        |
| :---------------- | :------------- | :------- | :-------------------- |
| **Productivity**  | {{ p1_score }} | 0.25     | {{ p1_weighted }}     |
| **Collaboration** | {{ p2_score }} | 0.20     | {{ p2_weighted }}     |
| **Security**      | {{ p3_score }} | 0.25     | {{ p3_weighted }}     |
| **Governance**    | {{ p4_score }} | 0.15     | {{ p4_weighted }}     |
| **Architecture**  | {{ p5_score }} | 0.15     | {{ p5_weighted }}     |
| **TOTAL**         |                | **1.00** | **{{ total_score }}** |

## Critical Violations

> [!IMPORTANT]
> Any checks listed here MUST be resolved immediately as they block compliance.

- {{ critical_violation_1 }}
- {{ critical_violation_2 }}

## Detailed findings

### P1: Productivity

- **Passed:** {{ p1_passed }}/{{ p1_total }}
- **Failures:**
  - `{{ check_id }}`: {{ failure_description }}

### P2: Collaboration

- **Passed:** {{ p2_passed }}/{{ p2_total }}
- **Failures:**
  - `{{ check_id }}`: {{ failure_description }}

### P3: Security

- **Passed:** {{ p3_passed }}/{{ p3_total }}
- **Failures:**
  - `{{ check_id }}`: {{ failure_description }}

### P4: Governance

- **Passed:** {{ p4_passed }}/{{ p4_total }}
- **Failures:**
  - `{{ check_id }}`: {{ failure_description }}

### P5: Architecture

- **Passed:** {{ p5_passed }}/{{ p5_total }}
- **Failures:**
  - `{{ check_id }}`: {{ failure_description }}

## Remediation Plan

### Immediate Actions (Next 24h)

1. Fix critical violations.
2. ...

### Short Term (Next Sprint)

1. Address P3 Security failures.
2. ...

### Medium Term

1. Improve maturity scores < 2.0.
2. ...

## Evidence

Artifacts are stored in: `{{ evidence_path }}`
