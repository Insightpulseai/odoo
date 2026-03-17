# SAP Tax Compliance — Capability Taxonomy

This document maps the technical and business capabilities of SAP Tax Compliance based on the documentation crawl.

## 1. Domain: Data Foundation & Connectivity
### 1.1 Data Replication
- **Source System Integration:** Integration with SAP S/4HANA, SAP ERP, and non-SAP systems.
- **Data Provisioning:** Support for SAP HANA Smart Data Integration (SDI) and SlT.
- **Worklist Types:** Mechanism to define the data grain and structure for compliance checks.

### 1.2 Master Data Management
- **User Groups:** Grouping of users for task assignment (App F2412).
- **Organization Mapping:** Integration with SAP HR or local organizational structures for workflow routing.

## 2. Domain: Rule & Check Definition
### 2.1 Compliance Checks (App F2338)
- **Check View:** Leveraging ABAP CDS views for detection logic.
- **Check Parameters:** Runtime variables for filtering and logic adjustment.
- **Check Classes:** Support for complex ABAP logic beyond CDS capabilities.

### 2.2 Compliance Scenarios (App F2339)
- **Check Selection:** Selection of multiple checks into a scenario.
- **Filtering:** Scenario-level filters.
- **Scheduling:** Integration with SAP HANA background scheduling for recurring runs.

## 3. Domain: Detection & Hit Processing
### 3.1 Scenario Execution
- **Mass Processing:** Parallel execution of scenarios across large datasets.
- **Incremental Detection:** Identification of new or changed records.

### 3.2 Automatic Hit Processing
- **Logic-Based Status Update:** Automatically setting hit status (e.g., "Not a Hit") based on predefined rules.
- **Hit Suppression:** Ignoring known false positives.

## 4. Domain: Investigation & Remediation
### 4.1 Hit Investigation (App F2344)
- **Status Management:** Workflow stages (Open, Processing, Completed).
- **Conclusion Assignment:** Assigning standard outcomes to findings.
- **Root Cause Analysis:** Capture of evidence and documentation during investigation.

### 4.2 Task Management (Task Lists)
- **Task List Templates:** Pre-defined sets of remedial steps.
- **Task Assignment:** Direct assignment to processors or user groups.
- **Deadline Monitoring:** Tracking task completion against due dates.

## 5. Domain: Analytics & Reporting
### 5.1 Dashboard & KPIs
- **Compliance Results Overview:** High-level visualization of hit density, age, and remediation status.
- **Compliance Scenario History:** Visualization of run outcomes over time.

### 5.2 External Reporting
- **CDS-based Extraction:** Exposing compliance data to SAP Analytics Cloud or BW/4HANA.
- **Auditor Access:** Specialized views and exports for tax audit support.
