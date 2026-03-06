# Odoo Workspace OS — Product Requirements

> Five product layers replacing enterprise SaaS with Odoo CE + AI.

## Layer 1: PPM (Project Portfolio Management)
**Replaces**: Microsoft Clarity / Project Online

### Problem
Enterprise PPM tools are expensive ($30-55/user/month), poorly integrated with ERP, and require separate licensing.

### Solution: ipai_ppm
- **Base**: Odoo Project + Timesheet + OCA project extensions
- **Delta**: `ipai_ppm` adds portfolio views, resource capacity planning, milestone tracking, cross-project dependencies
- **Key Features**:
  - Portfolio dashboard with RAG status
  - Resource utilization heatmap
  - Budget vs. actual tracking (linked to Odoo Accounting)
  - Milestone burndown with EVM metrics
  - Cross-project dependency graph

## Layer 2: Expense (AI-Powered Expense Management)
**Replaces**: SAP Concur

### Problem
Manual expense processing costs $15-25/report, high error rates, slow reimbursement cycles.

### Solution: ipai_expense_ai
- **Base**: Odoo Expense + OCA expense extensions
- **Delta**: `ipai_expense_ai` adds OCR receipt scanning, policy auto-enforcement, anomaly detection
- **Key Features**:
  - Receipt OCR via PaddleOCR-VL (self-hosted, no per-scan fees)
  - Automatic policy validation (per diem limits, category matching, duplicate detection)
  - AI-powered anomaly flagging (unusual amounts, frequency patterns)
  - Mobile capture workflow
  - Auto-categorization using historical patterns

## Layer 3: Workspace (Intelligent Workspace)
**Replaces**: Notion AI / Confluence + AI

### Problem
Knowledge is scattered across tools, no unified search, no ERP-aware context.

### Solution: ipai_workspace
- **Base**: Odoo Documents + Knowledge + OCA document extensions
- **Delta**: `ipai_workspace` adds semantic search, document grounding, meeting summaries, task extraction
- **Key Features**:
  - Semantic search across all Odoo records and documents
  - Document grounding for AI responses (cite sources)
  - Meeting summary → action item extraction → Odoo task creation
  - Knowledge base with auto-tagging
  - Context-aware search (understands project, expense, accounting context)

## Layer 4: Copilot (ERP Copilot)
**Replaces**: SAP Joule / Microsoft Copilot for ERP

### Problem
ERP systems have steep learning curves, complex navigation, and repetitive data entry.

### Solution: ipai_copilot
- **Base**: Odoo Discuss + OCA chat extensions
- **Delta**: `ipai_copilot` adds natural language ERP interaction, task automation, guided workflows
- **Key Features**:
  - Natural language queries: "Show me all overdue invoices for Project X"
  - Guided workflows: "Help me submit an expense report"
  - Bulk operations via chat: "Approve all timesheets for last week"
  - Anomaly alerts: "3 expenses flagged for review"
  - Context-aware suggestions based on user role and recent activity

## Layer 5: Close Control (Month-End Close Orchestration)
**Replaces**: BlackLine / FloQast

### Problem
Month-end close is manual, error-prone, takes 5-10 business days, poor visibility into blockers.

### Solution: ipai_close_control
- **Base**: Odoo Accounting + OCA accounting extensions
- **Delta**: `ipai_close_control` adds close checklist automation, reconciliation tracking, variance analysis
- **Key Features**:
  - Configurable close checklist with dependencies
  - Automated reconciliation status tracking
  - Variance analysis with threshold alerts
  - Close calendar with SLA tracking
  - Blocker identification and escalation
  - Historical close analytics (cycle time trends)
