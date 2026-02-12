# Close Orchestration Module - Constitution

## Non-Negotiable Rules

### 1. Three-Stage Workflow
- ALL close tasks must follow the Preparation → Review → Approval workflow
- No stage can be skipped
- Each stage requires explicit user action to advance

### 2. Role-Based Authorization
- Preparers can only mark their assigned tasks as prep complete
- Reviewers cannot review their own preparation work
- Final approval requires Controller (CKVC) or Finance Director (FD) role

### 3. Audit Trail
- All state changes must be logged with timestamp and user
- Approval actions require digital signature (user record)
- No deletion of completed tasks or cycles

### 4. Exception Handling
- Open exceptions block close cycle completion
- Critical exceptions must be escalated within 4 hours
- All exceptions require documented resolution

### 5. Period Locking
- Locked periods cannot be modified
- Lock action requires FD approval
- No backdating entries into locked periods

## Architecture Principles

### SAP AFC Alignment
- Follow SAP Advanced Financial Closing patterns
- Task categories map to SAP AFC task types
- Approval gates align with SAP workflow controls

### RACI Model
- Responsible: Task preparer
- Accountable: Task approver (Controller/FD)
- Consulted: Reviewer
- Informed: Cycle stakeholders via notifications

### Timeline Enforcement
- Default close cycle: 5-6 working days (Oct 24-29 pattern)
- Overdue tasks trigger automatic escalation
- KPI tracking for cycle time optimization
