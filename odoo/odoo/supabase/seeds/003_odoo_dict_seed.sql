-- =============================================================================
-- Seed: Odoo Data Dictionary - Finance PPM Fields
-- Purpose: Populate odoo_dict.fields with finance PPM model definitions
-- Models: project.project, project.task, hr.employee, project.tags
-- =============================================================================

-- Clear existing entries for idempotent seed
TRUNCATE TABLE odoo_dict.templates RESTART IDENTITY CASCADE;
TRUNCATE TABLE odoo_dict.fields RESTART IDENTITY CASCADE;

-- =============================================================================
-- PROJECT.PROJECT Fields
-- =============================================================================

INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value, default_value,
    domain, sequence
) VALUES
-- Key field
('project.project', 'x_external_ref', 'External Reference', 'char', true, true,
 NULL, 'External ID',
 'Stable key for this project across environments. Used for idempotent imports.',
 'FIN_CLOSE_TBWA', NULL,
 'project', 10),

-- Core fields
('project.project', 'name', 'Project Name', 'char', true, false,
 NULL, 'Name',
 'Human-friendly project name displayed in UI.',
 'Month-end Closing & Tax Filing', NULL,
 'project', 20),

('project.project', 'description', 'Description', 'html', false, false,
 NULL, 'Description',
 'Rich text description of the project scope and objectives.',
 '<p>Finance PPM for month-end close and BIR tax compliance</p>', NULL,
 'project', 30),

-- Relational fields
('project.project', 'partner_id', 'Customer', 'many2one', false, false,
 'res.partner', 'Customer',
 'Legal entity or client owning this project. Can be internal or external.',
 'TBWA SMP', NULL,
 'project', 40),

('project.project', 'company_id', 'Company', 'many2one', true, false,
 'res.company', 'Company',
 'Odoo company owning this project. Required for multi-company finance.',
 'TBWA\\SMP', NULL,
 'project', 50),

('project.project', 'user_id', 'Project Manager', 'many2one', false, false,
 'res.users', 'Project Manager',
 'User responsible for overall project delivery.',
 'Rey Meran', NULL,
 'project', 60),

-- Settings (CE-compatible)
('project.project', 'privacy_visibility', 'Visibility', 'selection', false, false,
 NULL, 'Visibility',
 'Who can see this project: portal (external), employees, or followers only.',
 'employees', 'employees',
 'project', 70),

('project.project', 'allow_task_dependencies', 'Allow Dependencies', 'boolean', false, false,
 NULL, 'Allow Task Dependencies',
 'Enable task dependency tracking (CE feature).',
 'True', 'True',
 'project', 80),

-- Dates
('project.project', 'date_start', 'Start Date', 'date', false, false,
 NULL, 'Start Date',
 'Planned project start date.',
 '2026-01-01', NULL,
 'project', 90),

('project.project', 'date', 'End Date', 'date', false, false,
 NULL, 'Deadline',
 'Planned project end date or deadline.',
 '2026-12-31', NULL,
 'project', 100),

-- Status
('project.project', 'active', 'Active', 'boolean', false, false,
 NULL, 'Active',
 'Whether the project is active. Inactive projects are archived.',
 'True', 'True',
 'project', 110);

-- =============================================================================
-- PROJECT.TASK Fields
-- =============================================================================

INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value, default_value,
    domain, sequence
) VALUES
-- Key field
('project.task', 'x_external_ref', 'External Reference', 'char', true, true,
 NULL, 'External ID',
 'Stable key for this task. Used for idempotent imports and dependency references.',
 'FIN_CLOSE_DAY3_TRIALBAL', NULL,
 'finance', 10),

-- Core fields
('project.task', 'name', 'Task Name', 'char', true, false,
 NULL, 'Name of the Tasks?',
 'Name of the finance/closing task.',
 'Post Trial Balance & Adjustments', NULL,
 'finance', 20),

('project.task', 'description', 'Description', 'html', false, false,
 NULL, 'Description',
 'Rich text description of what this task entails.',
 '<p>Run trial balance, post adjusting entries, verify account reconciliations</p>', NULL,
 'finance', 30),

-- Project linkage
('project.task', 'project_id', 'Project', 'many2one', true, false,
 'project.project', 'Project',
 'Parent project containing this task.',
 'Month-end Closing & Tax Filing', NULL,
 'finance', 40),

-- Company (multi-company)
('project.task', 'company_id', 'Company', 'many2one', true, false,
 'res.company', 'Company',
 'Odoo company for multi-company finance setup.',
 'TBWA\\SMP', NULL,
 'finance', 50),

-- Assignment
('project.task', 'user_ids', 'Assigned to', 'many2many', false, false,
 'res.users', 'Assigned to',
 'One or more assignees (Finance Director, Sr Finance Manager, etc.).',
 'Rey Meran', NULL,
 'finance', 60),

-- Stage
('project.task', 'stage_id', 'Stage', 'many2one', false, false,
 'project.task.type', 'Stage',
 'Current workflow stage of the task.',
 'To Do', 'To Do',
 'finance', 70),

-- Planning
('project.task', 'planned_hours', 'Allocated Time', 'float', false, false,
 NULL, 'Allocated Time',
 'Planned effort in hours for this task per cycle.',
 '4.0', '0',
 'finance', 80),

('project.task', 'date_deadline', 'Deadline', 'date', true, false,
 NULL, 'Planned Date',
 'Operational due date (e.g., Day 3, Day 5, BIR statutory cutoffs).',
 '2026-01-05', NULL,
 'finance', 90),

-- Tags
('project.task', 'tag_ids', 'Tags', 'many2many', false, false,
 'project.tags', 'Tags',
 'Classification tags: Month-End, Tax Filing, Risk, Must-Do, etc.',
 'Month-End,Tax Filing', NULL,
 'finance', 100),

-- Priority
('project.task', 'priority', 'Priority', 'selection', false, false,
 NULL, 'Priority',
 'Task priority: 0=Normal, 1=Important.',
 '1', '0',
 'finance', 110),

-- Dependencies (CE feature)
('project.task', 'depend_on_ids', 'Dependencies', 'many2many', false, false,
 'project.task', 'Depends on',
 'Tasks that must complete before this task can start.',
 'FIN_CLOSE_DAY1_CUTOFF', NULL,
 'finance', 120),

-- Sequence
('project.task', 'sequence', 'Sequence', 'integer', false, false,
 NULL, 'Sequence',
 'Order of task in project view. Lower = earlier.',
 '10', '10',
 'finance', 130),

-- Parent task (for subtasks)
('project.task', 'parent_id', 'Parent Task', 'many2one', false, false,
 'project.task', 'Parent Task',
 'Parent task if this is a subtask.',
 NULL, NULL,
 'finance', 140),

-- Status
('project.task', 'active', 'Active', 'boolean', false, false,
 NULL, 'Active',
 'Whether the task is active. Inactive tasks are archived.',
 'True', 'True',
 'finance', 150);

-- =============================================================================
-- PROJECT.TAGS Fields
-- =============================================================================

INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value, default_value,
    domain, sequence
) VALUES
-- Key field
('project.tags', 'x_external_ref', 'External Reference', 'char', false, true,
 NULL, 'External ID',
 'Stable key for this tag.',
 'TAG_MONTH_END', NULL,
 'project', 10),

-- Core fields
('project.tags', 'name', 'Tag Name', 'char', true, false,
 NULL, 'Name',
 'Display name of the tag.',
 'Month-End', NULL,
 'project', 20),

('project.tags', 'color', 'Color', 'integer', false, false,
 NULL, 'Color Index',
 'Color index (0-11) for visual differentiation.',
 '2', '0',
 'project', 30);

-- =============================================================================
-- PROJECT.TASK.TYPE (Stages) Fields
-- =============================================================================

INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value, default_value,
    domain, sequence
) VALUES
-- Key field
('project.task.type', 'x_external_ref', 'External Reference', 'char', false, true,
 NULL, 'External ID',
 'Stable key for this stage.',
 'STAGE_TODO', NULL,
 'project', 10),

-- Core fields
('project.task.type', 'name', 'Stage Name', 'char', true, false,
 NULL, 'Name',
 'Display name of the stage.',
 'To Do', NULL,
 'project', 20),

('project.task.type', 'sequence', 'Sequence', 'integer', false, false,
 NULL, 'Sequence',
 'Order of stage in kanban. Lower = earlier.',
 '1', '1',
 'project', 30),

('project.task.type', 'fold', 'Folded', 'boolean', false, false,
 NULL, 'Folded in Kanban',
 'Whether this stage is collapsed by default in kanban.',
 'False', 'False',
 'project', 40),

('project.task.type', 'project_ids', 'Projects', 'many2many', false, false,
 'project.project', 'Projects',
 'Projects that use this stage.',
 'Month-end Closing & Tax Filing', NULL,
 'project', 50);

-- =============================================================================
-- HR.EMPLOYEE Fields (for assignee reference)
-- =============================================================================

INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value, default_value,
    domain, sequence
) VALUES
-- Key field
('hr.employee', 'x_external_ref', 'External Reference', 'char', false, true,
 NULL, 'External ID',
 'Stable key for this employee.',
 'EMP_FINANCE_DIR', NULL,
 'hr', 10),

-- Core fields
('hr.employee', 'name', 'Employee Name', 'char', true, false,
 NULL, 'Name',
 'Full name of the employee.',
 'Rey Meran', NULL,
 'hr', 20),

('hr.employee', 'work_email', 'Work Email', 'char', false, false,
 NULL, 'Work Email',
 'Corporate email address.',
 'rey.meran@tbwa.com.ph', NULL,
 'hr', 30),

('hr.employee', 'job_title', 'Job Title', 'char', false, false,
 NULL, 'Job Title',
 'Current job title/position.',
 'Finance Director', NULL,
 'hr', 40),

('hr.employee', 'department_id', 'Department', 'many2one', false, false,
 'hr.department', 'Department',
 'Department this employee belongs to.',
 'Finance', NULL,
 'hr', 50),

('hr.employee', 'company_id', 'Company', 'many2one', true, false,
 'res.company', 'Company',
 'Company this employee works for.',
 'TBWA\\SMP', NULL,
 'hr', 60),

('hr.employee', 'user_id', 'Related User', 'many2one', false, false,
 'res.users', 'Related User',
 'Odoo user account linked to this employee.',
 'rey.meran@tbwa.com.ph', NULL,
 'hr', 70),

('hr.employee', 'active', 'Active', 'boolean', false, false,
 NULL, 'Active',
 'Whether the employee is currently active.',
 'True', 'True',
 'hr', 80);

-- =============================================================================
-- ACCOUNT.ANALYTIC.ACCOUNT Fields (for project cost tracking)
-- =============================================================================

INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value, default_value,
    domain, sequence
) VALUES
-- Key field
('account.analytic.account', 'x_external_ref', 'External Reference', 'char', false, true,
 NULL, 'External ID',
 'Stable key for this analytic account.',
 'AA_FIN_CLOSE_2026', NULL,
 'finance', 10),

-- Core fields
('account.analytic.account', 'name', 'Name', 'char', true, false,
 NULL, 'Name',
 'Name of the analytic account.',
 'Finance Close 2026', NULL,
 'finance', 20),

('account.analytic.account', 'code', 'Reference', 'char', false, false,
 NULL, 'Reference',
 'Short code/reference for the analytic account.',
 'FIN-CLOSE-26', NULL,
 'finance', 30),

('account.analytic.account', 'plan_id', 'Analytic Plan', 'many2one', true, false,
 'account.analytic.plan', 'Analytic Plan',
 'Plan this account belongs to.',
 'Projects', NULL,
 'finance', 40),

('account.analytic.account', 'company_id', 'Company', 'many2one', false, false,
 'res.company', 'Company',
 'Company owning this analytic account.',
 'TBWA\\SMP', NULL,
 'finance', 50),

('account.analytic.account', 'active', 'Active', 'boolean', false, false,
 NULL, 'Active',
 'Whether the analytic account is active.',
 'True', 'True',
 'finance', 60);

-- =============================================================================
-- PREDEFINED TEMPLATES
-- =============================================================================

INSERT INTO odoo_dict.templates (slug, name, description, model_name, field_names, domain)
VALUES
-- Finance PPM Tasks (full)
('finance-ppm-tasks', 'Finance PPM Tasks', 'Full task import for month-end closing and tax filing',
 'project.task',
 ARRAY['x_external_ref', 'name', 'description', 'project_id', 'company_id', 'user_ids', 'stage_id', 'planned_hours', 'date_deadline', 'tag_ids', 'priority', 'depend_on_ids', 'sequence'],
 'finance'),

-- Finance PPM Tasks (minimal)
('finance-ppm-tasks-minimal', 'Finance PPM Tasks (Minimal)', 'Minimal task import with required fields only',
 'project.task',
 ARRAY['x_external_ref', 'name', 'project_id', 'company_id', 'date_deadline'],
 'finance'),

-- Finance Projects
('finance-ppm-projects', 'Finance PPM Projects', 'Project import for finance programs',
 'project.project',
 ARRAY['x_external_ref', 'name', 'description', 'company_id', 'user_id', 'date_start', 'date'],
 'finance'),

-- Task Stages
('project-stages', 'Project Stages', 'Stage definitions for project kanban',
 'project.task.type',
 ARRAY['x_external_ref', 'name', 'sequence', 'fold'],
 'project'),

-- Project Tags
('project-tags', 'Project Tags', 'Tag definitions for task categorization',
 'project.tags',
 ARRAY['x_external_ref', 'name', 'color'],
 'project'),

-- HR Employees
('hr-employees', 'HR Employees', 'Employee master data for assignment references',
 'hr.employee',
 ARRAY['x_external_ref', 'name', 'work_email', 'job_title', 'department_id', 'company_id'],
 'hr'),

-- Analytic Accounts
('analytic-accounts', 'Analytic Accounts', 'Analytic accounts for project cost tracking',
 'account.analytic.account',
 ARRAY['x_external_ref', 'name', 'code', 'plan_id', 'company_id'],
 'finance');
