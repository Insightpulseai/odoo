---
name: crm
description: Customer Relationship Management for tracking leads, opportunities, and sales pipeline
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# crm -- Odoo 19.0 Skill Reference

## Overview

Odoo CRM manages the full sales cycle from lead acquisition through opportunity tracking to deal closure. It provides a Kanban-based pipeline, lead scoring, automated assignment, email integration, and performance reporting. Used by sales teams, sales managers, and marketing staff to organize prospects, forecast revenue, and optimize conversion rates.

## Key Concepts

- **Lead**: An unqualified contact or prospect entering the system via email, website form, manual entry, or lead mining.
- **Opportunity**: A qualified lead actively being pursued in the sales pipeline; has expected revenue, probability, and a salesperson assigned.
- **Pipeline**: Kanban board of stages (e.g., New, Qualified, Proposition, Won) representing the sales process.
- **Sales Team**: A group of salespeople managed together with shared pipeline stages and targets.
- **Lead Scoring**: Predictive scoring system that assigns probability to leads/opportunities based on historical data and configurable criteria.
- **Lead Enrichment**: Automated enrichment of contact data (company info, social profiles) using external data services (IAP).
- **Lead Mining**: Generation of new leads from external databases via IAP credits.
- **Lost Reason**: Categorized reason why an opportunity was marked as lost; used for win/loss analysis.
- **Activity**: Scheduled follow-up action (call, meeting, email, to-do) linked to a lead or opportunity.
- **Expected Revenue**: Estimated deal value on an opportunity, used for forecasting.

## Core Workflows

### 1. Acquire and Convert Leads

1. Leads arrive via email alias, website form, live chat, manual creation, or lead mining.
2. Review incoming leads in the pipeline or lead list view.
3. Qualify and convert leads to opportunities: open the lead, click **Convert to Opportunity**.
4. Choose to create a new opportunity, merge with existing, or link to existing customer.
5. Assign to a salesperson and sales team.

### 2. Manage the Pipeline

1. Navigate to **CRM > Pipeline** to see opportunities in Kanban view.
2. Drag opportunities between stages as they progress (e.g., New > Qualified > Proposition > Won).
3. Update expected revenue, probability, and contact information on each opportunity form.
4. Schedule activities (calls, meetings, emails) from the opportunity form or the activity view.
5. Mark opportunities as **Won** or **Lost** (with a lost reason) when deals close.

### 3. Send Quotations from Opportunities

1. Open an opportunity in the pipeline.
2. Click **New Quotation** to create a linked sales order.
3. The quotation pre-fills customer data from the opportunity.
4. Send the quotation; the opportunity status updates automatically when the SO is confirmed.

### 4. Manage Sales Teams

1. Navigate to **CRM > Configuration > Sales Teams**.
2. Create or edit a team: set name, team leader, members, email alias, and invoicing target.
3. Configure assignment rules: manual, round-robin by leads, or round-robin by opportunities.
4. Each team member can have a domain-based assignment rule for automatic lead distribution.

### 5. Analyze Performance

1. Use **CRM > Reporting > Pipeline Analysis** for pipeline metrics.
2. Use the **Forecast** report to view expected revenue by close date.
3. Use the **Win/Loss** report to analyze conversion rates and lost reasons.
4. Use the **Expected Revenue** report to track projected income.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `crm.lead` | Leads and opportunities (unified model; `type` field distinguishes) |
| `crm.team` | Sales teams |
| `crm.stage` | Pipeline stages |
| `crm.lost.reason` | Lost reasons catalog |
| `crm.lead.scoring.frequency` | Lead scoring frequency data |
| `crm.recurring.plan` | Recurring revenue plans |

### Key Fields on `crm.lead`

| Field | Type | Description |
|-------|------|-------------|
| `type` | Selection | `lead` or `opportunity` |
| `stage_id` | Many2one | Current pipeline stage |
| `team_id` | Many2one | Sales team |
| `user_id` | Many2one | Salesperson |
| `partner_id` | Many2one | Customer/contact |
| `expected_revenue` | Monetary | Expected deal value |
| `probability` | Float | Win probability (0-100) |
| `automated_probability` | Float | ML-computed probability |
| `date_deadline` | Date | Expected closing date |
| `lost_reason_id` | Many2one | Reason for loss |
| `tag_ids` | Many2many | Tags |
| `priority` | Selection | 0 (Normal), 1 (Medium), 2 (High), 3 (Very High) |
| `activity_ids` | One2many | Scheduled activities |

### Key Views / XML IDs

- `crm.crm_case_tree_view_leads` -- Leads list view
- `crm.crm_lead_all_pipeline` -- Pipeline Kanban view
- `crm.crm_lead_view_form` -- Lead/opportunity form view
- `crm.crm_team_view_tree` -- Sales teams list
- `crm.crm_lead_stage_form` -- Stage form

### Menu Paths

- Pipeline: `CRM > Pipeline`
- My Activities: `CRM > My Activities`
- Configuration: `CRM > Configuration > Sales Teams / Stages / Lost Reasons`
- Reporting: `CRM > Reporting > Pipeline / Forecast / Win-Loss`

## API / RPC Patterns

<!-- TODO: CRM-specific external API examples not found in docs -->

Standard ORM access applies:

```python
# Search opportunities
env['crm.lead'].search([('type', '=', 'opportunity'), ('stage_id.is_won', '=', False)])

# Convert lead to opportunity
lead.convert_opportunity(partner_id, user_ids=False, team_id=False)

# Mark as won
opportunity.action_set_won()

# Mark as lost
opportunity.action_set_lost(lost_reason_id=reason_id)
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not found in docs. The documentation reviewed is for the current version without explicit migration notes. -->

- Odoo 19.0 uses Python 3.12+.
- Lead scoring uses predictive/ML-based probability computed automatically.
- Lead enrichment and lead mining rely on IAP credits (not available in CE without IAP).

## Common Pitfalls

- **Lead vs. Opportunity confusion**: Both use `crm.lead` model; `type` field distinguishes them. Enable "Leads" in CRM settings to use the two-step flow; otherwise all entries are opportunities.
- **Lead mining and enrichment require IAP credits**: These are paid services via odoo.com; not available in pure CE offline deployments.
- **Assignment rules need proper domain configuration**: Misconfigured domains on sales team members result in unassigned leads.
- **Lost reasons must be created before use**: If no lost reasons exist, users cannot categorize why deals were lost, degrading reporting quality.
- **Activities are not auto-created**: Salespeople must manually schedule activities or configure automated actions to ensure follow-up happens.
