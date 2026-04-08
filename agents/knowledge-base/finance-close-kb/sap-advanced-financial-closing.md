# SAP Advanced Financial Closing — Full Documentation Catalog

---

## 🗂️ PRODUCT OVERVIEW

**SAP Advanced Financial Closing (AFC)**
*Finance Function · SAP Business Technology Platform (Cloud Foundry)*

**What It Does:** Lets you define, automate, process, and monitor the entity close for your organization. Supports planning, processing, monitoring, and analyzing financial closing tasks for all legal entities in a group.

**Available With:** SAP BTP · SAP S/4HANA Cloud Public Edition · SAP S/4HANA Cloud Private Edition · SAP S/4HANA · SAP ERP

---

## 📚 DOCUMENTATION STRUCTURE

The SAP Help Portal for AFC is organized into the following top-level guides:

| Guide | Purpose |
|---|---|
| Feature Scope Description (PDF) | Lists all product features |
| User Guide | How to work with AFC apps |
| Administration Guide | How to set up and run the product |
| What's New | New/changed features (current year) |
| What's New Archive | Past releases + highlight videos |

---

## 1️⃣ USER GUIDE — Full Topic Catalog

### 1.1 Financial Closing (Concept Overview)
- **Purpose:** Introduction to the financial close process and the apps used in AFC
- **Use Cases:** Recurring periodic activities; multiple agents involved; fixed chronological sequence; shared uniform interface; full status documentation
- **Apps Covered (in process flow order):**
  1. Manage Closing Task Lists
  2. Process Closing Tasks
  3. Approve Closing Tasks
  4. Financial Close Overview (Deprecated)
  5. Closing Task Completion (Deprecated)
  6. Change Log

---

### 1.2 Manage Closing Task Lists

**Purpose:** Model, plan, and start a workflow comprising all activities required to close your entities. Create/edit task list templates and generate task lists for each closing cycle.

**Key Features:**
- One template usable for all closing types (month-end, quarter-end, year-end)
- Multiple communication systems per template — single task list across systems
- Flexible hierarchy for closing structure matching organizational requirements
- Define task dependencies (predecessor/successor)
- Assign single users or user groups as "user responsible" and "processing user"
- Parallel editing on folder level — multiple users simultaneously
- SAP-predelivered task list models for GL accounting, AP, AR, asset accounting, controlling

**Sub-Topics (How-To Articles):**

*Create Task List Templates:*
- How to Create Task List Templates
- How to Define and Edit the Closing Structure
- How to Add Communication Systems
- How to Create and Manage Folders (Structural, Org Units, Copy, Move, Delete, Mass Actions)
- How to Assign Task List Models / Update Models / Disconnect from Models
- How to Assign Task Groups / Update Task Groups in a Template
- How to Create and Manage Tasks (Create, Attachments, Language Codes, Parameters, Dependencies, Deactivate/Activate, Copy, Move, Delete, Mass Actions)
- [Compatibility] How to Set Up a Hierarchy by Controlling Area or Plant
- How to Perform Checks on Templates
- How to Generate and Release Task Lists
- How to Copy a Task List Template
- How to Delete Task List Templates and Task Lists

*Manage Task Group Templates (new as of Feb 2026):*
- How to Create Task Group Templates
- How to Define and Edit the Task Group Structure
- How to Create and Manage Folders in Task Group Templates
- How to Create and Manage Tasks in Task Group Templates (Web Application, Note task types)
- How to Maintain Task Parameters / Dependencies in Task Group Templates
- How to Copy/Move/Delete Tasks in Task Group Templates
- How to Delete Task Group Templates

**Supported Device Types:** Desktop

---

### 1.3 Process Closing Tasks

**Purpose:** Manually process, schedule, or automate closing tasks. Each task list represents one closing cycle for a key date.

**Key Features:**
- Update/edit tasks individually or in batches
- Schedule test runs for eligible jobs
- Display job logs / application logs for error resolution
- Jump to task-specific applications to see job run results
- Multiple views: List, Graph (dependency graph), Hierarchy (new)
- Colored bar chart showing task status distribution
- Full audit trail — comments and attachments on all actions

**Sub-Topics:**
- Task List and Task Details
- How to Process Tasks
- How to Change Task Attributes
- How to Edit Task Parameters (incl. parameter consistency check)
- How to Manage Notes and Attachments
- How to View Task Logs and Spool Lists

**Supported Device Types:** Desktop

---

### 1.4 Approve Closing Tasks

**Purpose:** Check and approve critical closing tasks subject to dual control.

**Approval Types:**
- **No Approval Required** — task completes without approval
- **Completed Approval Required** — explicit approval needed before completion; successor tasks on hold until granted
- **Pending Approval Required** — subject to dual control but does not block subsequent steps

**Key Features:**
- Approve or reject tasks in batch
- View task-specific information in task details
- Use filters to display specific tasks
- Approved tab and To Be Approved tab for clear workflow separation

**Sub-Topics:**
- How to Approve and Reject Tasks
- How to Manage Notes and Attachments

**Supported Device Types:** Desktop

---

### 1.5 Manage Task Models

**Purpose:** View task models available in each communication system; find details on task model types, job variants, and parameter overviews.

**Key Features:**
- Overview of all task models per communication system
- Job Template Scope Status column (new 2026)
- Use for comparison of parameters across job variants

**Sub-Topics:**
- How to View Task Models

---

### 1.6 Reporting

#### 1.6.1 Financial Close Overview — Organizational Unit View
- High-level overview based on **task execution statuses**
- Overview cards by: completion rate, task status, errors count, delay

#### 1.6.2 Financial Close Overview — Task View
- High-level overview based on **overall task statuses**
- Overview cards by: completion rate, task status, errors count, delay
- New filters (2025): Approval Status, Offset in Day, Task Type
- New overview cards (2026): additional company code grouping characteristics, plants, controlling areas

#### 1.6.3 Closing Task Completion — Organizational Unit View
- Detailed reporting based on task execution statuses
- Features: filters, multiple chart types, multiple view options, task details drill-down

#### 1.6.4 Closing Task Completion — Task View
- Detailed reporting based on overall task statuses
- Features: filters, multiple chart types, multiple view options, task details drill-down

#### 1.6.5 How-To Articles
- How to Report on Task Level (Task View Apps)
- How to Report on Task Execution Level (Org Unit View Apps)

#### 1.6.6 Deprecated Reporting (restricted as of Feb 2026 — data limited to task lists generated before Feb 18, 2024)
- Financial Close Overview (Deprecated)
- Closing Task Completion (Deprecated)

---

### 1.7 Change Log
- How to Use the Change Log

---

### 1.8 Processes in Integration Scenarios

#### SAP Build Process Automation Integration
- How to Create Workflows in SAP Build Process Automation and Integrate Them into the Financial Close

#### Notification Scenarios
- Notifications in the Financial Close Workflow
- Notifications for Substitutes
- User Actions Menu
- SAP Fiori Notifications

**Available Notification Events:**
- Task ready to process
- Task approved (new 2025)
- Task invalidated (new 2025)
- Organizational units now included in notifications (2025)

#### Personal Settings
- How to Adjust Personal Settings for SAP Advanced Financial Closing

---

### 1.9 Concepts and Settings in SAP Advanced Financial Closing

#### Task List Templates / Task Lists
- Task Group Templates — centralized task management for reusable groups
- Task List Model Assignment — rules and results of model assignments
- Task List Generation and Release — what happens during generation/release
- Task List Status — all possible statuses and their meaning
- Allowed Attribute Changes Depending on Task List Status

#### Folders
- Folder Copying Process
- Allowed Attribute Changes Depending on Task List Status

#### Tasks
- Parameter Maintenance — types of parameters
- Dependency Types and Approval Types
- Start Date and Time Calculation — factory calendar and offset
- Offset Changes — how offset adjustments work
- Factory Calendar Settings and Use
- Critical Paths and Longest Paths
- Handling of Task Types Job and Workflow
- Integration of Tasks of Type Workflow
- User Assignments in Task Processing
- Task Scheduling
- Automation of Tasks
- Test Runs
- Job Name Derivation
- Task Status and Approval Status — relationship between statuses
- Definition of Statuses
- Task Status Derivation — how overall status is set
- Task Models — working with task models
- Allowed Attribute Changes Depending on Task List Status

#### General
- Different Object Representations — different views of task lists and tasks
- Company Code Groups
- Organizational Unit Assignments in the Financial Close
- Time Zone Handling
- Translation — handling of default description translations
- Authorization Concept
- Draft Handling
- How to Manage Views — save, manage, share views

---

## 2️⃣ ADMINISTRATION GUIDE — Full Topic Catalog

### 2.1 Overview
- About AFC (architecture, SAP BTP, Cloud Foundry environment)
- Data Flow from and to SAP Advanced Financial Closing
- Language Scope
- Technical Prerequisites
- Switch to SAP Cloud Identity Services — Identity Authentication (new default for new tenants, Feb 2026)

### 2.2 System Landscape & Onboarding
- Automated Setup for Production Tenant
- How to Automate Setup Using a Booster
- Accessing SAP Advanced Financial Closing
- How to Verify / Change the Default URL

### 2.3 User Management
- How to Manage Static Role Templates
- Static Roles for SAP Advanced Financial Closing
- How to Manage Users (upload, language codes, statuses, deletion)

### 2.4 User Access Management
**Scopes and Access Types:**

| Scope | Access Levels |
|---|---|
| Task List Creation | General / Specific Objects |
| Task Processing | General / System-Wide / Specific Objects / By Org Units |
| Task Group Management | General |
| Task Model Management | General / Specific Objects |
| Direct User Assignment | By Direct Assignment |

**Additional:**
- How to Copy/Assign User Roles
- How to Manage User Groups
- How to Manage User Access Using the SCIM API
- Authorizations Required in the Communication System

### 2.5 Connectivity — Communication Systems

**Supported System Types:**

| System | Connection Method |
|---|---|
| SAP S/4HANA Cloud Public Edition | OData services; communication arrangement setup; launchpad tile |
| SAP S/4HANA Cloud Private Edition | OData services |
| SAP S/4HANA | OData services + Cloud Connector + technical communication user |
| SAP ERP | REST service + SAP ERP Connector + Cloud Connector |
| SAP Build Process Automation | Destination in SAP BTP Cockpit |
| SAP Accounting Automation by BlackLine | Destination in SAP BTP Cockpit (new Feb 2026) |
| External Systems | SDK / OpenAPI spec (new Feb 2026) |

**Synchronization & Disruption Handling:**
- Synchronization Business Logs
- Disrupted System Connection scenarios (no restore needed / restore needed / AFC unavailable)

### 2.6 System Monitoring
- Monitor Communication Systems
- Check System Information / Overall System Status
- Tackle Connection Issues / Synchronization Issues / Scheduling Issues
- Notifications About Communication System Errors

### 2.7 Business Configuration Apps

| App | Purpose |
|---|---|
| Manage Authorization Groups | Define authorization groups |
| Manage Email Notification Configurations | Configure notification emails |
| Manage Company Code Groups | Group company codes |
| Manage User Groups | Manage user groupings |
| Manage User Roles | Define and assign roles |
| Manage Compliance Settings | Set compliance requirements |
| Manage General Settings | Global settings (e.g., successor task invalidation) |
| Manage Status Change Settings | Configure comment requirements on status changes (new Feb 2026) |
| Manage Task Models | View task models and job variants |
| Manage Users | User administration |
| Manage User Role Assignments | Assign roles to users |
| Manage Country/Region Groups | (Deprecated) |

### 2.8 Integration Capabilities

| Integration | Purpose |
|---|---|
| SCIM API | Manage users, groups, roles via dedicated API |
| SAP Build Process Automation | Trigger workflows from AFC task lists |
| SAP Accounting Automation by BlackLine | Trigger BlackLine processes from AFC task lists |
| External Systems | Trigger jobs in external system via scheduling provider service SDK/OpenAPI |
| SAP Build Work Zone | Access AFC from unified launchpad |
| SAP Task Center | Unified task inbox (requires global user IDs via custom IAS) |
| Process Automation via ABAP | Automate job processing using SAP Build Process Automation or SAP Intelligent RPA |

### 2.9 Task List Archiving
- Manage Archived Closing Task Lists

### 2.10 Data Management & Privacy
- Data Protection and Privacy
- Legal Basis for Data Processing
- Data Archiving in Communication Systems (AFC_OBJSTR, AFC_MSG)
- Data Destruction in Communication Systems (AFC_STRUC)
- Deletion of Personal Data

### 2.11 Security
- User Administration, Authentication, and Authorizations
- Authorization Handling During System Communication
- Session Security
- Data Storage Security
- Data Used for API Integrations
- File Security
- Audit Log Integration
- Theme Customization

### 2.12 Monitoring and Troubleshooting
- How to Sign Up for Update Notifications
- Error Handling
- Logging

### 2.13 Offboarding & Migration (Deprecated)
- Migrate Configuration Data (read-only)
- Migrate Closing Task Lists (read-only)

---

## 3️⃣ WHAT'S NEW — Key 2025/2026 Releases

| Release Date | Feature |
|---|---|
| Mar 2026 | Create Tasks from Models Using a Spreadsheet |
| Mar 2026 | Export tasks to create spreadsheet for transfer across templates/instances |
| Mar 2026 | SAP-Delivered Views to Filter for Task Groups |
| Mar 2026 | Batch spreadsheet creation for tasks in Task Group Templates |
| Mar 2026 | Job Template Scope Status in Manage Task Models |
| Feb 2026 | Connect SAP Accounting Automation by BlackLine |
| Feb 2026 | Connect External Systems (SDK/OpenAPI) |
| Feb 2026 | New SAP Cloud Identity Services default authentication for new tenants |
| Feb 2026 | Task Group Templates (centralized task management for Web App & Note tasks) |
| Feb 2026 | Manage Status Change Settings app |
| Feb 2026 | Restrictions for deprecated reporting apps (data limited to pre-Feb 2024) |
| Nov 2025 | Closing Type column on Task List Generations tab |
| Nov 2025 | Additional task detail columns (job template, transaction, program, etc.) |
| Oct 2025 | Hierarchical View of Tasks in Process Closing Tasks |
| Oct 2025 | Additional filters in Financial Close Overview (Approval Status, Offset, Task Type) |
| Sep 2025 | Vietnamese language added to UI |
| Sep 2025 | Launchpad tile in SAP S/4HANA Cloud Public Edition for direct navigation |
| Sep 2025 | Custom time-related parameter rules for ABAP programs |
| Sep 2025 | New UI5 version (visual/theme changes) |
| Sep 2025 | Navigation to workflow definitions in SAP Build Process Automation |
| Jul 2025 | Additional file types for attachments (XLSM, CSV) |
| Jul 2025 | Task List Generations tab with background generation and error log persistence |
| Jun 2025 | User Group popover showing member details |
| May 2025 | Move Tasks across folders in task list templates |
| May 2025 | Secondary Communication System for Workflow tasks |
| May 2025 | Note count columns in Tasks table |
| May 2025 | "Processed Task Approved" notification scenario |
| Mar 2025 | Manage Task Models app released |
| Mar 2025 | Draft Exists column |
| Mar 2025 | Spreadsheet export of closing structure |
| Mar 2025 | "Task Invalidated" notification scenario |
| Feb 2025 | New folder type "Communication System" |
| Feb 2025 | Invalidation of Successor Tasks setting |
| Feb 2025 | Parameter consistency/completeness check |
| Feb 2025 | Attachment count columns in Tasks table |
| Feb 2025 | Enhanced read authorization for task processing scope |

---

## 4️⃣ KEY USERS / PERSONAS

| Persona | Primary Apps |
|---|---|
| Accounting Manager / Close Controller | Manage Closing Task Lists, Financial Close Overview |
| Finance Operations / Close Analyst | Process Closing Tasks, Closing Task Completion |
| Approver / Compliance Officer | Approve Closing Tasks |
| System Administrator | Administration Guide apps (User Mgmt, Connectivity, Business Config) |
| Accounting Expert | Business Configuration, Manage General/Compliance Settings |

---

## 5️⃣ BUSINESS IMPACT AREAS

- **Faster Financial Close** → Automated task scheduling, dependency management, parallel editing
- **Improved Operational Efficiency** → Reduction in manual coordination; predelivered SAP task models
- **Error Reduction** → Dependency enforcement; dual-control approval; parameter consistency checks
- **Regulatory Compliance** → Audit trail on all actions; compliance settings; data protection/privacy framework
- **Employee Experience** → Unified SAP Fiori interface; notifications; mobile-compatible views

---

## 6️⃣ TYPICAL WORKFLOW (6-Step Close Process)

```
1. TEMPLATE SETUP
   Manage Closing Task Lists → Define closing structure, assign org units,
   add tasks, set dependencies, assign users

2. MODEL ASSIGNMENT
   Assign SAP-predelivered task list models (GL, AP, AR, Assets, Controlling)

3. TASK LIST GENERATION & RELEASE
   Generate task list for specific key date → Release to make tasks processable

4. PROCESS TASKS
   Process Closing Tasks → Schedule jobs, process manual tasks, review logs,
   handle errors, manage dependencies

5. APPROVE TASKS
   Approve Closing Tasks → Dual-control approval (Completed or Pending Approval Required)

6. MONITOR & REPORT
   Financial Close Overview (Org Unit View / Task View)
   Closing Task Completion (Org Unit View / Task View)
   Change Log
```

---

*Catalog compiled from: https://help.sap.com/docs/advanced-financial-closing — User Guide, Administration Guide, What's New (2025/2026), Integration Capabilities, and all sub-pages. As of March 21, 2026.*
