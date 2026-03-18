---
name: plm
description: Product Lifecycle Management for engineering change orders, BoM version control, and design file management.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# PLM — Odoo 19.0 Skill Reference

## Overview

Odoo Product Lifecycle Management (PLM) provides a systematic approach for managing product changes across concept development, design, manufacturing, and post-launch support stages. It uses Engineering Change Orders (ECOs) to track, implement, and revert changes to products and bills of materials, with approval workflows to ensure stakeholder review before changes go live. PLM also manages BoM version history and design file attachments. Used by product engineers, design teams, quality managers, and manufacturing operations leads.

## Key Concepts

- **Engineering Change Order (ECO)**: A tracked change request for a product or its BoM. Contains proposed component/operation changes, approval status, and revision history.
- **ECO Type**: A category that organizes ECOs into projects (e.g., `New Product Introduction`, `BOM Updates`, `Regulatory Compliance`). Each ECO type has its own Kanban board with stages.
- **ECO Stage**: Progress stages within an ECO type (e.g., New, In Progress, Validated, Done). Stages can be configured as `New` (open), `In Progress`, verification (requires approval), or closing (applies changes).
- **Approval**: Approvers assigned to verification stages who must accept changes before they can be applied. Approval types: `Is required to approve`, `Approves, but the approval is optional`, `Comments only`.
- **Revision**: A versioned copy of a BoM created when `Start Revision` is clicked on an ECO. Revisions are archived until changes are applied.
- **Version (BoM)**: Incremental version number (V1, V2, V3...) tracked in the `Miscellaneous` tab of a BoM. Updated when ECO changes are applied.
- **BoM Changes Tab**: Summary on an ECO showing differences between current production BoM and the revised BoM (added/updated/removed components in blue/black/red text).
- **Operation Changes Tab**: Summary on an ECO showing differences in operations between production and revised BoMs.
- **Apply Changes**: Action that archives the old production BoM and makes the revised BoM the new production BoM.
- **Apply Rebase**: Resolves merge conflicts when multiple ECOs modify the same BoM concurrently. Applies previous ECO changes to the current ECO's revision without overwriting its own changes.
- **Design Files**: CAD files, PDFs, images, or other documents attached to BoMs and managed through ECOs via the `Documents` smart button.
- **Effective Date**: When the ECO becomes live — `As soon as possible` (applied immediately) or a specific date.

## Core Workflows

### 1. Create and Apply an Engineering Change Order

1. Navigate to the PLM app, select an ECO type (e.g., `BOM Updates`).
2. Click `New` on the Engineering Change Orders page.
3. Fill in: `Description`, `Product`, `Bill of Materials`, `Apply on` (Bill of Materials or Product Only).
4. Set `Effective` date and assign a `Responsible` user.
5. Click `Start Revision`. This creates an archived copy of the production BoM and assigns a version number.
6. Click the `Revision` smart button to open the revised BoM. Make changes to components and/or operations.
7. Return to the ECO to view the `BoM Changes` and `Operation Changes` tabs for a diff summary.
8. Move the ECO to a verification stage. Approvers review and click `Approve`.
9. Once approved, click `Apply Changes`. The revised BoM becomes the new production BoM.

### 2. Manage BoM Version History

1. Go to `Manufacturing > Products > Bills of Materials`, select a BoM.
2. Click the `ECO` smart button to view all ECOs associated with this BoM.
3. Switch to list view and filter by `Done` to see the revision history.
4. Each ECO shows the responsible user, effective date, and version number.
5. Click an ECO to view past components, operations, and design files.

### 3. Configure Approval Workflow

1. Open the PLM app, hover over the desired stage of an ECO type, click the gear icon, then `Edit`.
2. In the stage edit popup, click `Add a line` under `Approvals`.
3. Enter a `Role` (e.g., Engineering Manager), select a `User`, and set `Approval Type`.
4. Required approvers must click `Approve` before `Apply Changes` becomes available.

### 4. Manage Design Files

1. Open an active ECO, click the `Documents` smart button.
2. On the Attachments page, upload new files via the `Upload` button.
3. To replace a file, hover over it, click the three-dot menu, and select `Remove`.
4. Upload the replacement file.
5. When `Apply Changes` is clicked, new files are linked to the production BoM and removed files are archived.

### 5. Resolve Concurrent ECO Conflicts (Rebase)

1. When a production BoM is updated by one ECO while another ECO is still open for the same BoM, a `Previous Eco Bom Changes` tab appears on the second ECO.
2. Review the changes from the previously applied ECO.
3. Click `Apply Rebase` to incorporate those changes into the current ECO's revision without losing the current ECO's own modifications.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `mrp.eco` | Engineering Change Order |
| `mrp.eco.type` | ECO type (project category) |
| `mrp.eco.stage` | ECO stage within a type |
| `mrp.eco.approval` | Approval record for an ECO stage |
| `mrp.bom` | Bill of Materials (versioned via PLM) |

### Key Fields

- `mrp.eco.name`: ECO description
- `mrp.eco.type_id`: ECO type
- `mrp.eco.stage_id`: Current stage
- `mrp.eco.product_tmpl_id`: Product template
- `mrp.eco.bom_id`: Associated BoM
- `mrp.eco.new_bom_id`: Revised BoM (created by Start Revision)
- `mrp.eco.effectivity`: `'asap'` or `'date'`
- `mrp.eco.effectivity_date`: Specific effective date (if `'date'`)
- `mrp.eco.state`: `'confirmed'`, `'progress'`, `'rebase'`, `'done'`
- `mrp.eco.approval_ids`: Approval records
- `mrp.bom.version`: BoM version number (integer, incremented by ECO)

### Important XML IDs

- `mrp_plm.mrp_eco_action_main` — ECO main action
- `mrp_plm.mrp_eco_type_action` — ECO types action

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 PLM docs do not cover JSON-RPC or XML-RPC examples directly. -->

## Version Notes (19.0)

- **BoM version tracking** in the `Miscellaneous` tab of BoMs is available when PLM is installed.
- **ECO email alias**: ECO types can have an email alias that auto-creates ECOs from incoming emails.
- **Rebase functionality**: Concurrent ECO conflict resolution via `Apply Rebase` is a mature feature in 19.0.

<!-- TODO: specific breaking changes between 18.0 and 19.0 not documented in PLM RST source -->

## Common Pitfalls

- **Start Revision is required before making changes**: The `Revision` smart button and archived BoM copy only appear after clicking `Start Revision`. Modifying the production BoM directly bypasses version control.
- **Apply Changes requires approval from required approvers**: If any approver with `Is required to approve` type has not approved, the `Apply Changes` button will not work (though no blocking error is shown if no required approver exists).
- **Revision smart button only appears for BoM changes**: If `Apply on` is set to `Product Only`, the Revision smart button does not appear since no BoM copy is created.
- **Concurrent ECOs can conflict**: If two ECOs modify the same BoM and one is applied first, the second ECO works on an outdated BoM. The `Apply Rebase` button must be used to synchronize. Ignoring this can overwrite the first ECO's changes.
- **Archived files are not permanently deleted**: Files removed via ECOs remain accessible in the previous ECO or as archived attachments. There is no permanent deletion from the ECO workflow.
