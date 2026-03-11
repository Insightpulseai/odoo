---
name: esg
description: Environment, Social, and Governance reporting with automated carbon footprint tracking, sex parity analysis, and sustainability initiatives.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# esg — Odoo 19.0 Skill Reference

## Overview

The Odoo ESG (Environment, Social, and Governance) app automates ESG data collection by integrating with Accounting, Fleet, Payroll, and Employees apps. It tracks carbon emissions from accounting records, employee commuting, and manual inputs; measures sex parity and pay gaps; and provides project-based sustainability initiatives. Data is updated in real time for continuous monitoring and CSRD/ESRS compliance reporting.

## Key Concepts

- **Carbon Footprint**: Automated emissions tracking computed as `Activity Data x Emission Factor`, measured in kgCO2e (CO2 equivalents).
- **Emission Factor**: Coefficient indicating greenhouse gas emission rate for a specific activity. Sourced from certified databases (e.g., ADEME) or manually defined.
- **GHG Protocol Scopes**: Scope 1 (direct emissions, e.g., company vehicles), Scope 2 (indirect from purchased energy), Scope 3 (all other indirect, e.g., purchased goods, travel, waste).
- **Assignation Rules**: Rules that automatically match emission factors to accounting journal entries based on product, partner, and/or account criteria.
- **Compute Method**: Physical (quantity-based, e.g., kg, liters) or Monetary (amount-based, e.g., EUR spent) calculation approach for emissions.
- **Gas Emission Lines**: Per-emission-factor breakdown by greenhouse gas type (CO2, CH4, N2O, HFCs, PFCs, SF6) with Global Warming Potential (GWP) conversion.
- **Sex Parity**: Workforce distribution analysis by sex across departments, job positions, contract types, leadership levels, and countries. Supports CSRD ESRS S1 reporting.
- **Pay Gap**: Calculated as `((Average male salary - Average female salary) / Average male salary) x 100`, using wages from Payroll contracts for the same jobs.
- **Initiatives**: ESG action items managed as Projects with estimated CO2 savings per task, progress tracking, and team assignments.

## Core Workflows

### 1. Set Up Carbon Footprint Tracking

1. Import emission factor database: ESG > Configuration > Source Databases, click Download on ADEME.
2. Configure assignation rules: ESG > Configuration > Emission Factors, select a factor, go to Assignations tab, add lines matching Product, Partner, and/or Account.
3. Ensure units of measure match between product cost UoM and emission factor UoM.
4. Apply retroactively: select emission factor, click Assign, define Application Period.
5. Bulk assign: select multiple factors in list view, Actions > Assign Emission Factors.

### 2. Track Employee Commuting Emissions

1. Set weekly office attendance: ESG > Configuration > Settings > Weekly Office Attendance.
2. Configure vehicle CO2 emissions: Fleet > Configuration > Models, set CO2 Emissions per model.
3. Set employee home-work distance: Employees app > select employee > Home-Work Distance.
4. Ensure employee vehicle Start Date (and End Date if applicable) are set.
5. View pivot table: ESG > Collect > Employee Commuting.
6. Click Add Emissions, define Emissions Period, Save.

Formula: `Days x Home-work distance x 2 x (Office days / 7) x Vehicle CO2 emissions`

### 3. Enter Manual Emissions

1. Go to ESG > Collect > Emitted Emissions, click New.
2. Name the activity, select Date, choose Emission Factor, enter Quantity.
3. Save. Entry appears in emitted emissions and carbon footprint report.

### 4. Analyze Sex Parity and Pay Gap

1. Set employee gender: Employees app > select employee > Private Information > Gender.
2. Ensure Payroll contracts have wages set for pay gap calculation.
3. View measures: ESG > Measure > Sex Parity / Pay Gap.
4. Use Group By options: Leadership Level, Department, Job Position, Contract Type, Country.

### 5. Manage Sustainability Initiatives

1. Go to ESG > Act > Initiatives.
2. Create project tasks with estimated CO2 savings, deadlines, and team assignments.
3. Track progress using standard Project app features.

## Technical Reference

### Data Sources for Carbon Footprint

| Source | Account Types Used | Integration |
|--------|-------------------|-------------|
| Accounting | Fixed Assets, Expenses, Other Expenses, Cost of Revenue | Journal entries posted to expense/asset accounts |
| Fleet | Employee vehicle data | CO2 emissions per vehicle model x commuting distance |
| Manual | Any activity | Direct entry of quantity x emission factor |

### Emission Factor Configuration

- **Source**: Scope assignment (1, 2, or 3) with hierarchical sub-categories
- **Uncertainty**: Margin of error percentage for data quality assessment
- **Compute Method**: Physical (quantity) or Monetary (amount)
- **Gas Emission Lines**: Multiple gases per factor, each with GWP conversion to kgCO2e
- **Assignation Rules**: Product + Partner + Account matching with priority hierarchy

### Assignation Rule Priority

1. Product (most specific)
2. Partner
3. Account (least specific)

When multiple rules match at the same specificity level, the rule with more attributes defined takes priority.

### Menu Paths

- Dashboard: ESG (main)
- Emitted Emissions: ESG > Collect > Emitted Emissions
- Employee Commuting: ESG > Collect > Employee Commuting
- Emission Factors: ESG > Configuration > Emission Factors
- Source Databases: ESG > Configuration > Source Databases
- Gases: ESG > Configuration > Gases
- Sex Parity / Pay Gap: ESG > Measure > Sex Parity / Pay Gap
- Initiatives: ESG > Act > Initiatives
- Settings: ESG > Configuration > Settings

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- **ESG is a new app** in Odoo 19.0. No prior version comparison available.
- Follows the *Bilan Carbone* methodology for accounting-based emissions.
- Supports the six Kyoto Protocol greenhouse gases (CO2, CH4, N2O, HFCs, PFCs, SF6).
- ADEME is the first supported source database for emission factors.
- Sex parity and pay gap features target CSRD reporting under ESRS S1 and future VSME standards.

## Common Pitfalls

- **Unit of measure mismatch**: The product's Cost UoM must match the emission factor's UoM. If Units of Measure are not visible, enable them in Accounting > Configuration > Settings.
- **Missing emission factors on journal entries**: Check the "Emissions to define" count on the ESG dashboard's Collect Emissions card to find unassigned entries.
- **Estimated CO2 from initiatives do not reduce footprint**: Initiative task CO2 savings are projections only. Actual impact shows only when reflected in operational data (accounting records, fleet changes).
- **Employee vehicle dates required**: Commuting emissions depend on the vehicle's Start Date and End Date. Missing dates produce incorrect calculations.
- **Pay gap requires Payroll contracts**: The pay gap calculation uses wages from Payroll contracts, not from other salary data sources. Employees without contracts are excluded.
