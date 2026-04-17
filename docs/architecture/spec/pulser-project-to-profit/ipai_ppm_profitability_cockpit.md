# Module Specification: ipai_ppm_profitability_cockpit

This document defines the functional and technical requirements for the margin-intelligence and utilization-adjusted profitability cockpit in Pulser for Odoo.

## 1. Goal Description
The **Profitability Cockpit** provides real-time visibility into project-level margins, comparing actual costs (timesheets, vendor invoices, expenses) against the baseline budget and forecast. It serves as the primary differentiator for services consulting and agency clients (TBWA\SMP) who require Clarity PPM-grade financial oversight.

## 2. Adaptation Doctrine
> [!IMPORTANT]
> **Adapt before build**: This module is a thin bridge that coordinates core and community surfaces. It MUST NOT recreate the reporting engine or transactional models.

- **Transaction Plane**: Uses Odoo `project`, `account`, `hr_timesheet`, and `purchase`.
- **Reporting Plane**: Uses OCA `mis_builder` and `project_reporting`.
- **Data Plane**: Uses Azure Databricks for utilization-adjusted "Shadow Costing" (e.g., resource overhead absorption).

## 3. Functional Requirements

| ID | Requirement | Description | Maturity |
| :--- | :--- | :--- | :--- |
| **FR-01** | Margin Variance | Real-time calculation of (Revenue - Actual Cost) vs Budgeted Margin. | Low |
| **FR-02** | Utilization Pivot | Adjust margin based on resource utilization (billable vs bench). | Low |
| **FR-03** | Shadow Costing | Apply fully-burdened overhead to billable time for accurate services margin. | Low |
| **FR-04** | Forecast Drift | Signal if actual burn rates project a budget overrun before the milestone. | Low |
| **FR-05** | Billing Readiness | Gate margin reporting on evidence-completion status. | Low |

## 4. Technical Architecture

### 4.1 Data Sources
- **Actuals**: `account.move.line` filtered by `analytic_account_id`.
- **Forecast**: `ipai_finance_ppm_forecast` (thin bridge to `analytic.plan`).
- **Overhead**: External lookup from Pulser's and **Shadow Cost** registry (Databricks-managed).

### 4.2 UI Components
- **Odoo View Overlay**: Adds "Profitability" smart-button to `project.project`.
- **MIS Builder Template**: Predefined financial report templates for P&L-by-Project.
- **Pulser Signal**: Projects margin alerts into the and **Project Finance Cockpit (FCP)** agent.

## 5. Security & Governance
- **Approval bands**: Access restricted to and **pulser_project_finance_controller** (Band B+).
- **Evidence Visibility**: Margin signals must link back to source GL entries for auditability.

---
*Created: 2026-04-14*
