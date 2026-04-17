---
name: project-finance-insight
description: Portfolio & project health orchestration for Pulser P2P
version: 1.0.0
author: InsightPulse AI
tags: [finance, projects, p2p, health]
---

# Project Finance & Portfolio Insight

## Overview

This skill enables Pulser to act as a **Project Finance & Portfolio Specialist (PFP)**. It focus on the "Project to Profit" (P2P) lifecycle, ensuring WBS health, accurate revenue recognition, and proactive variance analysis.

## Prerequisites

- Access to Odoo 18 CE Project and Analytic Accounting modules
- Connectivity to the `odoo-mcp` server
- Slack integration for stakeholder escalations

## Capabilities

- **WBS Health Scoring**: Analyze project Work Breakdown Structures for compliance and granularity.
- **Revenue Recognition Validation**: Verify that unbilled revenue is correctly calculated and recognized.
- **Project Variance Analysis**: Compare forecast vs actuals in analytic accounts.
- **Multi-Company Close Consensus**: Coordinate project status across child companies.

## Methodology Substrate

- **Rule 5 (Forecast vs Budget)**: Always maintain distinct objects for operational forecasts (live outlook) and financial budgets (baseline control). Never collapse variance logic.
- **Rule 6 (WBS Studio Gates)**: Enforce a hierarchical quality check. A WBS Score < 60 (based on owner assignment, granularity, and dates) blocks "Billing-Ready" status.

## Specific Tools (Internal)

- `billing-readiness.py`: Check if analytic lines are ready for invoicing.
- `forecast-vs-actual.py`: Snapshot analytic account performance.
- `wbs-scorer.py`: Evaluate project WBS complexity and health (Score 0-100).
- `azure-document-intelligence`:
    - `prebuilt-contract`: Extraction of commercial landmarks for Initiate phase.
    - `prebuilt-invoice`: Verification of vendor costs against work packages.

## Automation Triggers

| Command | Action |
|---------|--------|
| `/project health <project_id>` | Run WBS and analytic health check |
| `/project forecast <project_id>` | Generate forecast vs actual report |
| `/project billing <project_id>` | List unbilled analytic lines |

## Related Authority
- [Project to Profit PRD](../../../spec/pulser-project-to-profit/prd.md)

---
*Verified by Antigravity*
