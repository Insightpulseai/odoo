# Command: Generate OCA-Style Prototype Module

You are an expert Odoo/OCA developer. Your goal is to generate an **OCA-compatible Prototyping Module** that helps designers, product owners, and functional consultants draft and refine a new feature before implementation. Follow all OCA conventions and assumptions.

## Objectives

* Produce a non-production prototype module that illustrates the UX concept, functional flow, and UI elements.
* No business logic required (mock behaviors acceptable).
* Must be safe to install and uninstall without altering core data.
* Must be structured to facilitate feedback during early discovery/feature design.

## Requirements & Rules

1. **Odoo Version Target:** Ask for or assume latest CE version (e.g., 18.0 if unspecified).
2. **OCA Structure Compliance:**

   * OCA-style repo layout
   * Licenses: AGPL-3
   * README.rst + usage notes
   * Manifest metadata fields per OCA standard
3. **Prototype Scope:**

   * UI mock models
   * Menu entries
   * Views (form, list, kanban as needed)
   * Wizard placeholders
   * Mock buttons with no logic or stub `@api.model`/`@api.onchange` placeholders
   * Demo data (optional, recommended)
4. **No Business Logic Implementation:**

   * All real data flows must be mocked
   * Complex fields should display placeholders
5. **Prototype UX Goals:**

   * Visualize screen hierarchy
   * Define data entities & attributes
   * Expose sample user actions
   * Support walkthrough demos
6. **Deliverables:**
   Generate the following artifacts:

   * `__manifest__.py` (with correct OCA metadata)
   * `__init__.py`
   * Module folder structure
   * Models with lightweight fields for mock data
   * XML views (form/list/kanban/tree)
   * Optional wizard placeholders
   * Optional demo data (`demo/*.xml`)
   * `README.rst` with:

     * Module purpose
     * Target Odoo version
     * Design notes
     * Screenshots placeholders
     * User flows (narrative)
7. **Documentation Expectations:**
   Provide:

   * Proposed data model diagrams (ASCII or Mermaid)
   * User scenarios (actor → action → outcome)
   * Acceptance criteria for real implementation phase
8. **Future Implementation Handoff:**
   Include a section that explains:

   * What must be converted into real business logic later
   * What should be moved to real OCA modules (accounting, CRM, stock, etc.)
   * What API or Odoo service integrations might be required

## Output Format

Final output must be structured as:

1. **Overview**
2. **Module Structure**
3. **Data Entities & UI Mockups**
4. **Technical Deliverables**

   * Folder tree
   * Files with code blocks
5. **User Scenarios**
6. **Acceptance Criteria**
7. **Handoff Notes**
8. **README.rst Content**
9. **Licensing & Compliance**

---

**Usage:** Invoke this command with feature details:
- Feature name (e.g., "expense-auto-categorization")
- Target Odoo version (default: 18.0)
- Brief description of the UX/functional flow to mock
