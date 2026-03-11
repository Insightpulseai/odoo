-- =============================================================================
-- ODOO SHADOW SCHEMA - Auto-generated from ODOO_MODEL_INDEX.json
-- Generated: 2026-01-20T04:25:34.862724
-- Source: ODOO_MODEL_INDEX.json
-- Models: 357
-- 
-- DO NOT EDIT MANUALLY - Regenerate via:
--   python scripts/generate_shadow_ddl.py
-- =============================================================================

-- Create shadow schema if not exists
CREATE SCHEMA IF NOT EXISTS odoo_shadow;

-- Set search path for this session
SET search_path TO public;

-- =============================================================================
-- Shadow Metadata Registry
-- =============================================================================

CREATE TABLE IF NOT EXISTS odoo_shadow_meta (
    id bigserial PRIMARY KEY,
    table_name text NOT NULL UNIQUE,
    odoo_model text NOT NULL,
    odoo_module text,
    field_count integer,
    last_sync_at timestamptz,
    row_count bigint,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- =============================================================================
-- Shadow Tables
-- =============================================================================

-- Model: a1.check
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_check (
    id bigint PRIMARY KEY,
    active boolean,
    check_type text,
    close_gate_template_id bigint,
    code text,
    company_id bigint,
    description text,
    fail_action text,
    name text,
    pass_criteria text,
    sequence bigint,
    severity text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_check_write_date
    ON odoo_shadow_a1_check (_odoo_write_date DESC);

-- Model: a1.check.result
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_check_result (
    id bigint PRIMARY KEY,
    check_id bigint,
    evidence text,
    executed_by bigint,
    executed_date timestamptz,
    result text,
    result_notes text,
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_check_result_write_date
    ON odoo_shadow_a1_check_result (_odoo_write_date DESC);

-- Model: a1.export.run
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_export_run (
    id bigint PRIMARY KEY,
    company_id bigint,
    created_count bigint,
    error_count bigint,
    log text,
    run_type text,
    seed_hash text,
    seed_json text,
    status text,
    unchanged_count bigint,
    updated_count bigint,
    webhook_url text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_export_run_write_date
    ON odoo_shadow_a1_export_run (_odoo_write_date DESC);

-- Model: a1.role
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_role (
    id bigint PRIMARY KEY,
    active boolean,
    code text,
    company_id bigint,
    default_user_id bigint,
    description text,
    fallback_user_id bigint,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_role_write_date
    ON odoo_shadow_a1_role (_odoo_write_date DESC);

-- Model: a1.task
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_task (
    id bigint PRIMARY KEY,
    approval_deadline date,
    approval_done_by bigint,
    approval_done_date timestamptz,
    approver_id bigint,
    approver_role text,
    checklist_progress double precision,  -- computed, stored
    close_task_id bigint,
    company_id bigint,
    external_key text,
    name text,
    notes text,
    owner_id bigint,
    owner_role text,
    prep_deadline date,
    prep_done_by bigint,
    prep_done_date timestamptz,
    review_deadline date,
    review_done_by bigint,
    review_done_date timestamptz,
    reviewer_id bigint,
    reviewer_role text,
    sequence bigint,
    state text,
    tasklist_id bigint,
    template_id bigint,
    workstream_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_task_write_date
    ON odoo_shadow_a1_task (_odoo_write_date DESC);

-- Model: a1.task.checklist
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_task_checklist (
    id bigint PRIMARY KEY,
    code text,
    done_by bigint,
    done_date timestamptz,
    is_done boolean,
    is_required boolean,
    item_type text,
    name text,
    sequence bigint,
    task_id bigint,
    template_item_id bigint,
    value_attachment_id bigint,
    value_text text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_task_checklist_write_date
    ON odoo_shadow_a1_task_checklist (_odoo_write_date DESC);

-- Model: a1.tasklist
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_tasklist (
    id bigint PRIMARY KEY,
    close_cycle_id bigint,
    company_id bigint,
    name text,
    notes text,
    period_end date,
    period_label text,  -- computed, stored
    period_start date,
    progress double precision,  -- computed, stored
    state text,
    task_count bigint,  -- computed, stored
    task_done_count bigint,  -- computed, stored
    webhook_url text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_tasklist_write_date
    ON odoo_shadow_a1_tasklist (_odoo_write_date DESC);

-- Model: a1.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_template (
    id bigint PRIMARY KEY,
    active boolean,
    approval_days double precision,
    approver_role text,
    close_template_id bigint,
    code text,
    company_id bigint,
    description text,
    name text,
    owner_role text,
    phase_code text,
    prep_days double precision,
    review_days double precision,
    reviewer_role text,
    sequence bigint,
    total_days double precision,  -- computed, stored
    workstream_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_template_write_date
    ON odoo_shadow_a1_template (_odoo_write_date DESC);

-- Model: a1.template.checklist
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_template_checklist (
    id bigint PRIMARY KEY,
    code text,
    instructions text,
    is_required boolean,
    item_type text,
    name text,
    sequence bigint,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_template_checklist_write_date
    ON odoo_shadow_a1_template_checklist (_odoo_write_date DESC);

-- Model: a1.template.step
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_template_step (
    id bigint PRIMARY KEY,
    assignee_role text,
    code text,
    deadline_offset_days bigint,
    effort_days double precision,
    name text,
    sequence bigint,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_template_step_write_date
    ON odoo_shadow_a1_template_step (_odoo_write_date DESC);

-- Model: a1.workstream
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_a1_workstream (
    id bigint PRIMARY KEY,
    active boolean,
    close_category_id bigint,
    code text,
    company_id bigint,
    description text,
    name text,
    owner_role_id bigint,
    owner_user_id bigint,  -- computed, stored
    phase_code text,
    sequence bigint,
    template_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_a1_workstream_write_date
    ON odoo_shadow_a1_workstream (_odoo_write_date DESC);

-- Model: account.account
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_account_account (
    id bigint PRIMARY KEY,
    centralized boolean,
    hide_in_cash_flow boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_account_write_date
    ON odoo_shadow_account_account (_odoo_write_date DESC);

-- Model: account.account.reconcile.data
-- Module: account_reconcile_oca
CREATE TABLE IF NOT EXISTS odoo_shadow_account_account_reconcile_data (
    id bigint PRIMARY KEY,
    data jsonb,
    reconcile_id bigint,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_account_reconcile_data_write_date
    ON odoo_shadow_account_account_reconcile_data (_odoo_write_date DESC);

-- Model: account.age.report.configuration
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_account_age_report_configuration (
    id bigint PRIMARY KEY,
    company_id bigint,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_age_report_configuration_write_date
    ON odoo_shadow_account_age_report_configuration (_odoo_write_date DESC);

-- Model: account.age.report.configuration.line
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_account_age_report_configuration_line (
    id bigint PRIMARY KEY,
    account_age_report_config_id bigint,
    inferior_limit bigint,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_age_report_configuration_line_write_date
    ON odoo_shadow_account_age_report_configuration_line (_odoo_write_date DESC);

-- Model: account.analytic.line
-- Module: project_task_ancestor
CREATE TABLE IF NOT EXISTS odoo_shadow_account_analytic_line (
    id bigint PRIMARY KEY,
    ancestor_task_id bigint,
    date_time timestamptz,
    date_time_end timestamptz,  -- computed, stored
    show_time_control text,  -- computed, stored
    stock_move_id bigint,
    stock_task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_analytic_line_write_date
    ON odoo_shadow_account_analytic_line (_odoo_write_date DESC);

-- Model: account.bank.statement.line
-- Module: account_reconcile_analytic_tag
CREATE TABLE IF NOT EXISTS odoo_shadow_account_bank_statement_line (
    id bigint PRIMARY KEY,
    aggregate_id bigint,  -- computed, stored
    aggregate_name text,  -- computed, stored
    can_reconcile boolean,
    reconcile_aggregate text,  -- computed, stored
    reconcile_data jsonb,
    reconcile_data_info jsonb,
    reconcile_mode text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_bank_statement_line_write_date
    ON odoo_shadow_account_bank_statement_line (_odoo_write_date DESC);

-- Model: account.group
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_account_group (
    id bigint PRIMARY KEY,
    complete_code text,  -- computed, stored
    complete_name text,  -- computed, stored
    level bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_group_write_date
    ON odoo_shadow_account_group (_odoo_write_date DESC);

-- Model: account.journal
-- Module: account_move_base_import
CREATE TABLE IF NOT EXISTS odoo_shadow_account_journal (
    id bigint PRIMARY KEY,
    autovalidate_completed_move boolean,
    commission_account_id bigint,
    commission_analytic_account_id bigint,
    company_currency_id bigint,
    create_counterpart boolean,
    import_type text,
    last_import_date timestamptz,
    launch_import_completion boolean,
    partner_id bigint,
    receivable_account_id bigint,
    reconcile_aggregate text,
    reconcile_mode text,
    split_counterpart boolean,
    used_for_completion boolean,
    used_for_import boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_journal_write_date
    ON odoo_shadow_account_journal (_odoo_write_date DESC);

-- Model: account.move
-- Module: account_in_payment
CREATE TABLE IF NOT EXISTS odoo_shadow_account_move (
    id bigint PRIMARY KEY,
    bir_2307_date date,
    bir_2307_generated boolean,
    completion_logs text,
    ewt_amount numeric(16, 2),  -- computed, stored
    financial_type text,  -- computed, stored
    import_partner_id bigint,
    transaction_id text,
    used_for_completion boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_move_write_date
    ON odoo_shadow_account_move (_odoo_write_date DESC);

-- Model: account.move.completion.rule
-- Module: account_move_base_import
CREATE TABLE IF NOT EXISTS odoo_shadow_account_move_completion_rule (
    id bigint PRIMARY KEY,
    function_to_call text,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_move_completion_rule_write_date
    ON odoo_shadow_account_move_completion_rule (_odoo_write_date DESC);

-- Model: account.move.line
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_account_move_line (
    id bigint PRIMARY KEY,
    already_completed boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_move_line_write_date
    ON odoo_shadow_account_move_line (_odoo_write_date DESC);

-- Model: account.reconcile.abstract
-- Module: account_reconcile_analytic_tag
CREATE TABLE IF NOT EXISTS odoo_shadow_account_reconcile_abstract (
    id bigint PRIMARY KEY,
    company_currency_id bigint,
    company_id bigint,
    currency_id bigint,
    foreign_currency_id bigint,
    reconcile_data_info jsonb,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_reconcile_abstract_write_date
    ON odoo_shadow_account_reconcile_abstract (_odoo_write_date DESC);

-- Model: account.reconcile.model
-- Module: account_reconcile_model_oca
CREATE TABLE IF NOT EXISTS odoo_shadow_account_reconcile_model (
    id bigint PRIMARY KEY,
    unique_matching boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_reconcile_model_write_date
    ON odoo_shadow_account_reconcile_model (_odoo_write_date DESC);

-- Model: account.tax
-- Module: account_tax_balance
CREATE TABLE IF NOT EXISTS odoo_shadow_account_tax (
    id bigint PRIMARY KEY,
    balance double precision,  -- computed, stored
    balance_refund double precision,  -- computed, stored
    balance_regular double precision,  -- computed, stored
    base_balance double precision,  -- computed, stored
    base_balance_refund double precision,  -- computed, stored
    base_balance_regular double precision,  -- computed, stored
    has_moves boolean,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_tax_write_date
    ON odoo_shadow_account_tax (_odoo_write_date DESC);

-- Model: account_financial_report_abstract_wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_account_financial_report_abstract_wizard (
    id bigint PRIMARY KEY,
    company_id bigint,
    label_text_limit bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_account_financial_report_abstract_wizard_write_date
    ON odoo_shadow_account_financial_report_abstract_wizard (_odoo_write_date DESC);

-- Model: activity.statement.wizard
-- Module: partner_statement
CREATE TABLE IF NOT EXISTS odoo_shadow_activity_statement_wizard (
    id bigint PRIMARY KEY,
    date_start date,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_activity_statement_wizard_write_date
    ON odoo_shadow_activity_statement_wizard (_odoo_write_date DESC);

-- Model: advisor.category
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_advisor_category (
    id bigint PRIMARY KEY,
    active boolean,
    code text,
    color bigint,
    description text,
    high_count bigint,  -- computed, stored
    icon text,
    latest_score bigint,  -- computed, stored
    name text,
    open_count bigint,  -- computed, stored
    recommendation_count bigint,  -- computed, stored
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_advisor_category_write_date
    ON odoo_shadow_advisor_category (_odoo_write_date DESC);

-- Model: advisor.playbook
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_advisor_playbook (
    id bigint PRIMARY KEY,
    active boolean,
    automation_kind text,
    automation_params text,
    automation_ref text,
    code text,
    description text,
    name text,
    recommendation_count bigint,  -- computed, stored
    steps_md text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_advisor_playbook_write_date
    ON odoo_shadow_advisor_playbook (_odoo_write_date DESC);

-- Model: advisor.recommendation
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_advisor_recommendation (
    id bigint PRIMARY KEY,
    category_code text,
    category_id bigint,
    confidence double precision,
    currency_id bigint,
    date_due date,
    date_resolved date,
    description text,
    estimated_savings numeric(16, 2),
    evidence text,
    external_link text,
    impact_score bigint,
    name text,
    owner_id bigint,
    playbook_id bigint,
    remediation_steps text,
    resource_ref text,
    resource_type text,
    severity text,
    severity_order bigint,  -- computed, stored
    snooze_until date,
    source text,
    status text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_advisor_recommendation_write_date
    ON odoo_shadow_advisor_recommendation (_odoo_write_date DESC);

-- Model: advisor.score
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_advisor_score (
    id bigint PRIMARY KEY,
    as_of timestamptz,
    category_code text,
    category_id bigint,
    critical_count bigint,
    high_count bigint,
    inputs_json text,
    open_count bigint,
    resolved_count bigint,
    score bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_advisor_score_write_date
    ON odoo_shadow_advisor_score (_odoo_write_date DESC);

-- Model: advisor.tag
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_advisor_tag (
    id bigint PRIMARY KEY,
    color bigint,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_advisor_tag_write_date
    ON odoo_shadow_advisor_tag (_odoo_write_date DESC);

-- Model: aged.partner.balance.report.wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_aged_partner_balance_report_wizard (
    id bigint PRIMARY KEY,
    account_code_from bigint,
    account_code_to bigint,
    age_partner_config_id bigint,
    date_at date,
    date_from date,
    payable_accounts_only boolean,
    receivable_accounts_only boolean,
    show_move_line_details boolean,
    target_move text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_aged_partner_balance_report_wizard_write_date
    ON odoo_shadow_aged_partner_balance_report_wizard (_odoo_write_date DESC);

-- Model: attachment.queue
-- Module: attachment_queue
CREATE TABLE IF NOT EXISTS odoo_shadow_attachment_queue (
    id bigint PRIMARY KEY,
    attachment_id bigint,
    date_done timestamptz,
    failure_emails text,  -- computed, stored
    file_type text,
    fs_storage_id bigint,
    method_type text,
    state text,
    state_message text,
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_attachment_queue_write_date
    ON odoo_shadow_attachment_queue (_odoo_write_date DESC);

-- Model: attachment.synchronize.task
-- Module: attachment_synchronize
CREATE TABLE IF NOT EXISTS odoo_shadow_attachment_synchronize_task (
    id bigint PRIMARY KEY,
    active boolean,
    after_import text,
    avoid_duplicated_files boolean,
    backend_id bigint,
    count_attachment_done bigint,  -- computed, stored
    count_attachment_failed bigint,  -- computed, stored
    count_attachment_pending bigint,  -- computed, stored
    failure_emails text,
    file_type text,
    filepath text,
    method_type text,
    move_path text,
    name text,
    new_name text,
    pattern text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_attachment_synchronize_task_write_date
    ON odoo_shadow_attachment_synchronize_task (_odoo_write_date DESC);

-- Model: auditlog.http.request
-- Module: auditlog
CREATE TABLE IF NOT EXISTS odoo_shadow_auditlog_http_request (
    id bigint PRIMARY KEY,
    display_name text,  -- computed, stored
    http_session_id bigint,
    name text,
    root_url text,
    user_context text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_auditlog_http_request_write_date
    ON odoo_shadow_auditlog_http_request (_odoo_write_date DESC);

-- Model: auditlog.http.session
-- Module: auditlog
CREATE TABLE IF NOT EXISTS odoo_shadow_auditlog_http_session (
    id bigint PRIMARY KEY,
    display_name text,  -- computed, stored
    name text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_auditlog_http_session_write_date
    ON odoo_shadow_auditlog_http_session (_odoo_write_date DESC);

-- Model: auditlog.log
-- Module: auditlog
CREATE TABLE IF NOT EXISTS odoo_shadow_auditlog_log (
    id bigint PRIMARY KEY,
    http_request_id bigint,
    http_session_id bigint,
    log_type text,
    method text,
    model_id bigint,
    model_model text,
    model_name text,
    name text,
    res_id bigint,
    res_ids text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_auditlog_log_write_date
    ON odoo_shadow_auditlog_log (_odoo_write_date DESC);

-- Model: auditlog.log.line
-- Module: auditlog
CREATE TABLE IF NOT EXISTS odoo_shadow_auditlog_log_line (
    id bigint PRIMARY KEY,
    field_description text,
    field_id bigint,
    field_name text,
    log_id bigint,
    new_value text,
    new_value_text text,
    old_value text,
    old_value_text text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_auditlog_log_line_write_date
    ON odoo_shadow_auditlog_log_line (_odoo_write_date DESC);

-- Model: auditlog.rule
-- Module: auditlog
CREATE TABLE IF NOT EXISTS odoo_shadow_auditlog_rule (
    id bigint PRIMARY KEY,
    action_id bigint,
    capture_record boolean,
    log_create boolean,
    log_export_data boolean,
    log_read boolean,
    log_type text,
    log_unlink boolean,
    log_write boolean,
    model_id bigint,
    model_model text,
    model_name text,
    name text,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_auditlog_rule_write_date
    ON odoo_shadow_auditlog_rule (_odoo_write_date DESC);

-- Model: base
-- Module: autovacuum_message_attachment
CREATE TABLE IF NOT EXISTS odoo_shadow_base (
    id bigint PRIMARY KEY,
    smart_search text,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_base_write_date
    ON odoo_shadow_base (_odoo_write_date DESC);

-- Model: base.exception
-- Module: base_exception
CREATE TABLE IF NOT EXISTS odoo_shadow_base_exception (
    id bigint PRIMARY KEY,
    exceptions_summary text,  -- computed, stored
    ignore_exception boolean,
    main_exception_id bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_base_exception_write_date
    ON odoo_shadow_base_exception (_odoo_write_date DESC);

-- Model: base.exception.test.purchase
-- Module: base_exception
CREATE TABLE IF NOT EXISTS odoo_shadow_base_exception_test_purchase (
    id bigint PRIMARY KEY,
    active boolean,
    amount_total double precision,  -- computed, stored
    name text,
    partner_id bigint,
    state text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_base_exception_test_purchase_write_date
    ON odoo_shadow_base_exception_test_purchase (_odoo_write_date DESC);

-- Model: base.exception.test.purchase.line
-- Module: base_exception
CREATE TABLE IF NOT EXISTS odoo_shadow_base_exception_test_purchase_line (
    id bigint PRIMARY KEY,
    amount double precision,
    lead_id bigint,
    name text,
    qty double precision,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_base_exception_test_purchase_line_write_date
    ON odoo_shadow_base_exception_test_purchase_line (_odoo_write_date DESC);

-- Model: base.sequence.tester
-- Module: base_sequence_option
CREATE TABLE IF NOT EXISTS odoo_shadow_base_sequence_tester (
    id bigint PRIMARY KEY,
    name text,
    test_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_base_sequence_tester_write_date
    ON odoo_shadow_base_sequence_tester (_odoo_write_date DESC);

-- Model: bir.alphalist
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_alphalist (
    id bigint PRIMARY KEY,
    company_id bigint,
    currency_id bigint,
    fiscal_year bigint,
    form_type text,
    name text,
    state text,
    total_gross numeric(16, 2),  -- computed, stored
    total_wht numeric(16, 2),  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_alphalist_write_date
    ON odoo_shadow_bir_alphalist (_odoo_write_date DESC);

-- Model: bir.alphalist.line
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_alphalist_line (
    id bigint PRIMARY KEY,
    alphalist_id bigint,
    currency_id bigint,
    gross_income numeric(16, 2),
    income_type text,
    partner_id bigint,
    tin text,
    wht_amount numeric(16, 2),
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_alphalist_line_write_date
    ON odoo_shadow_bir_alphalist_line (_odoo_write_date DESC);

-- Model: bir.filing.deadline
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_filing_deadline (
    id bigint PRIMARY KEY,
    company_id bigint,
    deadline_date date,
    form_type text,
    name text,
    period_month bigint,
    period_year bigint,
    reminder_date date,  -- computed, stored
    return_id bigint,
    state text,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_filing_deadline_write_date
    ON odoo_shadow_bir_filing_deadline (_odoo_write_date DESC);

-- Model: bir.return
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_return (
    id bigint PRIMARY KEY,
    bir_reference text,
    company_id bigint,
    currency_id bigint,
    exempt_sales numeric(16, 2),
    filed_by bigint,
    filed_date timestamptz,
    form_type text,
    input_vat numeric(16, 2),
    interest numeric(16, 2),
    name text,  -- computed, stored
    notes text,
    output_vat numeric(16, 2),
    payment_date date,
    payment_reference text,
    penalty numeric(16, 2),
    period_end date,
    period_start date,
    state text,
    task_id bigint,
    tax_base numeric(16, 2),
    tax_credits numeric(16, 2),
    tax_due numeric(16, 2),
    tax_payable numeric(16, 2),  -- computed, stored
    total_due numeric(16, 2),  -- computed, stored
    total_payments numeric(16, 2),
    total_wht numeric(16, 2),
    vatable_sales numeric(16, 2),
    zero_rated_sales numeric(16, 2),
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_return_write_date
    ON odoo_shadow_bir_return (_odoo_write_date DESC);

-- Model: bir.return.line
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_return_line (
    id bigint PRIMARY KEY,
    amount numeric(16, 2),
    currency_id bigint,
    description text,
    move_id bigint,
    partner_id bigint,
    return_id bigint,
    sequence bigint,
    tax_amount numeric(16, 2),
    tin text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_return_line_write_date
    ON odoo_shadow_bir_return_line (_odoo_write_date DESC);

-- Model: bir.tax.return
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_tax_return (
    id bigint PRIMARY KEY,
    bir_reference text,
    company_id bigint,
    currency_id bigint,
    days_until_due bigint,  -- computed, stored
    due_date date,  -- computed, stored
    filed_by bigint,
    filed_date timestamptz,
    form_type text,
    frequency text,  -- computed, stored
    interest numeric(16, 2),
    is_overdue boolean,  -- computed, stored
    name text,
    notes text,
    payment_date date,
    payment_reference text,
    penalty numeric(16, 2),
    period_end date,
    period_start date,
    state text,
    tax_base numeric(16, 2),
    tax_category text,  -- computed, stored
    tax_credits numeric(16, 2),
    tax_due numeric(16, 2),
    tax_payable numeric(16, 2),  -- computed, stored
    total_amount_due numeric(16, 2),  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_tax_return_write_date
    ON odoo_shadow_bir_tax_return (_odoo_write_date DESC);

-- Model: bir.tax.return.line
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_tax_return_line (
    id bigint PRIMARY KEY,
    currency_id bigint,
    description text,
    move_id bigint,
    partner_id bigint,
    return_id bigint,
    sequence bigint,
    tax_amount numeric(16, 2),
    tax_base numeric(16, 2),
    tax_rate double precision,
    tin text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_tax_return_line_write_date
    ON odoo_shadow_bir_tax_return_line (_odoo_write_date DESC);

-- Model: bir.vat.line
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_vat_line (
    id bigint PRIMARY KEY,
    amount_untaxed numeric(16, 2),
    currency_id bigint,
    invoice_date date,
    invoice_id bigint,
    line_type text,
    partner_id bigint,
    return_id bigint,
    tin text,
    vat_amount numeric(16, 2),
    vat_category text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_vat_line_write_date
    ON odoo_shadow_bir_vat_line (_odoo_write_date DESC);

-- Model: bir.vat.return
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_vat_return (
    id bigint PRIMARY KEY,
    excess_input_vat numeric(16, 2),  -- computed, stored
    excess_input_vat_previous numeric(16, 2),
    exempt_sales numeric(16, 2),
    importations numeric(16, 2),
    net_vat_payable numeric(16, 2),  -- computed, stored
    output_vat numeric(16, 2),  -- computed, stored
    purchase_of_services numeric(16, 2),
    total_input_vat numeric(16, 2),  -- computed, stored
    total_sales numeric(16, 2),  -- computed, stored
    vatable_purchases numeric(16, 2),
    vatable_sales numeric(16, 2),
    zero_rated_sales numeric(16, 2),
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_vat_return_write_date
    ON odoo_shadow_bir_vat_return (_odoo_write_date DESC);

-- Model: bir.withholding.line
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_withholding_line (
    id bigint PRIMARY KEY,
    currency_id bigint,
    gross_income numeric(16, 2),
    income_type text,
    move_id bigint,
    partner_id bigint,
    payslip_id bigint,
    return_id bigint,
    tin text,
    wht_amount numeric(16, 2),
    wht_rate double precision,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_withholding_line_write_date
    ON odoo_shadow_bir_withholding_line (_odoo_write_date DESC);

-- Model: bir.withholding.return
-- Module: ipai_bir_tax_compliance
CREATE TABLE IF NOT EXISTS odoo_shadow_bir_withholding_return (
    id bigint PRIMARY KEY,
    compensation_tax_withheld numeric(16, 2),
    employee_count bigint,
    expanded_wht_amount numeric(16, 2),
    final_wht_amount numeric(16, 2),
    taxable_compensation numeric(16, 2),
    total_compensation numeric(16, 2),
    total_payments numeric(16, 2),
    withholding_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_bir_withholding_return_write_date
    ON odoo_shadow_bir_withholding_return (_odoo_write_date DESC);

-- Model: cleanup.create_indexes.line
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_create_indexes_line (
    id bigint PRIMARY KEY,
    field_id bigint,
    purged boolean,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_create_indexes_line_write_date
    ON odoo_shadow_cleanup_create_indexes_line (_odoo_write_date DESC);

-- Model: cleanup.purge.line
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line (
    id bigint PRIMARY KEY,
    name text,
    purged boolean,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_write_date
    ON odoo_shadow_cleanup_purge_line (_odoo_write_date DESC);

-- Model: cleanup.purge.line.column
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_column (
    id bigint PRIMARY KEY,
    model_id bigint,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_column_write_date
    ON odoo_shadow_cleanup_purge_line_column (_odoo_write_date DESC);

-- Model: cleanup.purge.line.data
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_data (
    id bigint PRIMARY KEY,
    data_id bigint,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_data_write_date
    ON odoo_shadow_cleanup_purge_line_data (_odoo_write_date DESC);

-- Model: cleanup.purge.line.field
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_field (
    id bigint PRIMARY KEY,
    field_id bigint,
    model_id bigint,
    model_name text,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_field_write_date
    ON odoo_shadow_cleanup_purge_line_field (_odoo_write_date DESC);

-- Model: cleanup.purge.line.menu
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_menu (
    id bigint PRIMARY KEY,
    menu_id bigint,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_menu_write_date
    ON odoo_shadow_cleanup_purge_line_menu (_odoo_write_date DESC);

-- Model: cleanup.purge.line.model
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_model (
    id bigint PRIMARY KEY,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_model_write_date
    ON odoo_shadow_cleanup_purge_line_model (_odoo_write_date DESC);

-- Model: cleanup.purge.line.module
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_module (
    id bigint PRIMARY KEY,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_module_write_date
    ON odoo_shadow_cleanup_purge_line_module (_odoo_write_date DESC);

-- Model: cleanup.purge.line.table
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_cleanup_purge_line_table (
    id bigint PRIMARY KEY,
    table_type text,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_cleanup_purge_line_table_write_date
    ON odoo_shadow_cleanup_purge_line_table (_odoo_write_date DESC);

-- Model: close.approval.gate
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_approval_gate (
    id bigint PRIMARY KEY,
    actual_value double precision,
    approved_by bigint,
    approved_date timestamptz,
    approver_id bigint,
    block_reason text,
    company_id bigint,
    cycle_id bigint,
    gate_type text,
    name text,
    notes text,
    sequence bigint,
    state text,
    template_id bigint,
    threshold_value double precision,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_approval_gate_write_date
    ON odoo_shadow_close_approval_gate (_odoo_write_date DESC);

-- Model: close.approval.gate.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_approval_gate_template (
    id bigint PRIMARY KEY,
    a1_check_id bigint,
    active boolean,
    code text,
    company_id bigint,
    description text,
    gate_type text,
    name text,
    pass_criteria text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_approval_gate_template_write_date
    ON odoo_shadow_close_approval_gate_template (_odoo_write_date DESC);

-- Model: close.cycle
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_cycle (
    id bigint PRIMARY KEY,
    a1_tasklist_id bigint,
    company_id bigint,
    exception_count bigint,  -- computed, stored
    gates_ready boolean,  -- computed, stored
    name text,
    notes text,
    open_exception_count bigint,  -- computed, stored
    period_end date,
    period_label text,  -- computed, stored
    period_start date,
    progress double precision,  -- computed, stored
    state text,
    task_count bigint,  -- computed, stored
    task_done_count bigint,  -- computed, stored
    webhook_url text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_cycle_write_date
    ON odoo_shadow_close_cycle (_odoo_write_date DESC);

-- Model: close.exception
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_exception (
    id bigint PRIMARY KEY,
    assigned_to bigint,
    company_id bigint,
    cycle_id bigint,
    description text,
    escalated_to bigint,
    escalation_count bigint,
    escalation_deadline timestamptz,
    exception_type text,
    last_escalated timestamptz,
    name text,
    reported_by bigint,
    resolution text,
    resolved_by bigint,
    resolved_date timestamptz,
    severity text,
    state text,
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_exception_write_date
    ON odoo_shadow_close_exception (_odoo_write_date DESC);

-- Model: close.task
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_task (
    id bigint PRIMARY KEY,
    a1_task_id bigint,
    approval_deadline date,
    approval_done_by bigint,
    approval_done_date timestamptz,
    approver_id bigint,
    category_id bigint,
    checklist_progress double precision,  -- computed, stored
    company_id bigint,
    cycle_id bigint,
    external_key text,
    has_open_exceptions boolean,  -- computed, stored
    name text,
    notes text,
    prep_deadline date,
    prep_done_by bigint,
    prep_done_date timestamptz,
    preparer_id bigint,
    review_deadline date,
    review_done_by bigint,
    review_done_date timestamptz,
    reviewer_id bigint,
    sequence bigint,
    state text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_task_write_date
    ON odoo_shadow_close_task (_odoo_write_date DESC);

-- Model: close.task.category
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_task_category (
    id bigint PRIMARY KEY,
    a1_workstream_id bigint,
    active boolean,
    code text,
    color bigint,
    company_id bigint,
    description text,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_task_category_write_date
    ON odoo_shadow_close_task_category (_odoo_write_date DESC);

-- Model: close.task.checklist
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_task_checklist (
    id bigint PRIMARY KEY,
    code text,
    done_by bigint,
    done_date timestamptz,
    instructions text,
    is_done boolean,
    is_required boolean,
    name text,
    sequence bigint,
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_task_checklist_write_date
    ON odoo_shadow_close_task_checklist (_odoo_write_date DESC);

-- Model: close.task.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_task_template (
    id bigint PRIMARY KEY,
    a1_template_id bigint,
    active boolean,
    approval_days double precision,
    approval_offset bigint,
    approver_id bigint,
    approver_role text,
    category_id bigint,
    code text,
    company_id bigint,
    description text,
    name text,
    prep_days double precision,
    prep_offset bigint,
    preparer_id bigint,
    preparer_role text,
    review_days double precision,
    review_offset bigint,
    reviewer_id bigint,
    reviewer_role text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_task_template_write_date
    ON odoo_shadow_close_task_template (_odoo_write_date DESC);

-- Model: close.task.template.checklist
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_close_task_template_checklist (
    id bigint PRIMARY KEY,
    code text,
    instructions text,
    is_required boolean,
    name text,
    sequence bigint,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_close_task_template_checklist_write_date
    ON odoo_shadow_close_task_template_checklist (_odoo_write_date DESC);

-- Model: closing.period
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_closing_period (
    id bigint PRIMARY KEY,
    bir_tasks bigint,  -- computed, stored
    company_id bigint,
    completed_tasks bigint,  -- computed, stored
    last_workday date,  -- computed, stored
    month_end_tasks bigint,  -- computed, stored
    name text,  -- computed, stored
    notes text,
    overdue_tasks bigint,  -- computed, stored
    period_date date,
    period_month bigint,  -- computed, stored
    period_year bigint,  -- computed, stored
    progress double precision,  -- computed, stored
    state text,
    total_tasks bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_closing_period_write_date
    ON odoo_shadow_closing_period (_odoo_write_date DESC);

-- Model: compliance.check
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_compliance_check (
    id bigint PRIMARY KEY,
    actual_value double precision,
    check_type text,
    checked_by bigint,
    checked_date timestamptz,
    closing_id bigint,
    expected_value double precision,
    name text,
    result_text text,
    sequence bigint,
    status text,
    tolerance double precision,
    variance double precision,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_compliance_check_write_date
    ON odoo_shadow_compliance_check (_odoo_write_date DESC);

-- Model: credit.statement.import
-- Module: account_move_base_import
CREATE TABLE IF NOT EXISTS odoo_shadow_credit_statement_import (
    id bigint PRIMARY KEY,
    commission_account_id bigint,
    file_name text,
    input_statement bytea,
    journal_id bigint,
    partner_id bigint,
    receivable_account_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_credit_statement_import_write_date
    ON odoo_shadow_credit_statement_import (_odoo_write_date DESC);

-- Model: crm.lead
-- Module: ipai_crm_pipeline
CREATE TABLE IF NOT EXISTS odoo_shadow_crm_lead (
    id bigint PRIMARY KEY,
    days_in_stage bigint,  -- computed, stored
    last_call_date timestamptz,
    last_meeting_date timestamptz,
    stage_entry_date timestamptz,
    stage_missing_fields text,  -- computed, stored
    stage_rule_validated boolean,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_crm_lead_write_date
    ON odoo_shadow_crm_lead (_odoo_write_date DESC);

-- Model: crm.stage
-- Module: ipai_crm_pipeline
CREATE TABLE IF NOT EXISTS odoo_shadow_crm_stage (
    id bigint PRIMARY KEY,
    ipai_automation_notes text,
    ipai_enforce_rules boolean,
    ipai_sla_days bigint,
    ipai_stage_color text,
    ipai_stage_icon text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_crm_stage_write_date
    ON odoo_shadow_crm_stage (_odoo_write_date DESC);

-- Model: db.backup
-- Module: auto_backup
CREATE TABLE IF NOT EXISTS odoo_shadow_db_backup (
    id bigint PRIMARY KEY,
    backup_format text,
    days_to_keep bigint,
    folder text,
    method text,
    name text,  -- computed, stored
    sftp_host text,
    sftp_password text,
    sftp_port bigint,
    sftp_private_key text,
    sftp_user text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_db_backup_write_date
    ON odoo_shadow_db_backup (_odoo_write_date DESC);

-- Model: detailed.activity.statement.wizard
-- Module: partner_statement
CREATE TABLE IF NOT EXISTS odoo_shadow_detailed_activity_statement_wizard (
    id bigint PRIMARY KEY,
    show_aging_buckets boolean,
    show_balance boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_detailed_activity_statement_wizard_write_date
    ON odoo_shadow_detailed_activity_statement_wizard (_odoo_write_date DESC);

-- Model: discuss.channel
-- Module: ipai_ask_ai
CREATE TABLE IF NOT EXISTS odoo_shadow_discuss_channel (
    id bigint PRIMARY KEY,
    is_ai_channel boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_discuss_channel_write_date
    ON odoo_shadow_discuss_channel (_odoo_write_date DESC);

-- Model: exception.rule
-- Module: base_exception
CREATE TABLE IF NOT EXISTS odoo_shadow_exception_rule (
    id bigint PRIMARY KEY,
    active boolean,
    code text,
    description text,
    domain text,
    exception_type text,
    is_blocking boolean,
    method text,
    model text,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_exception_rule_write_date
    ON odoo_shadow_exception_rule (_odoo_write_date DESC);

-- Model: exception.rule.confirm
-- Module: base_exception
CREATE TABLE IF NOT EXISTS odoo_shadow_exception_rule_confirm (
    id bigint PRIMARY KEY,
    ignore boolean,
    related_model_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_exception_rule_confirm_write_date
    ON odoo_shadow_exception_rule_confirm (_odoo_write_date DESC);

-- Model: exception.rule.confirm.test.purchase
-- Module: base_exception
CREATE TABLE IF NOT EXISTS odoo_shadow_exception_rule_confirm_test_purchase (
    id bigint PRIMARY KEY,
    related_model_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_exception_rule_confirm_test_purchase_write_date
    ON odoo_shadow_exception_rule_confirm_test_purchase (_odoo_write_date DESC);

-- Model: export.xlsx.wizard
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_export_xlsx_wizard (
    id bigint PRIMARY KEY,
    data bytea,
    name text,
    res_ids text,
    res_model text,
    state text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_export_xlsx_wizard_write_date
    ON odoo_shadow_export_xlsx_wizard (_odoo_write_date DESC);

-- Model: fetchmail.attach.mail.manually
-- Module: fetchmail_attach_from_folder
CREATE TABLE IF NOT EXISTS odoo_shadow_fetchmail_attach_mail_manually (
    id bigint PRIMARY KEY,
    folder_id bigint,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_fetchmail_attach_mail_manually_write_date
    ON odoo_shadow_fetchmail_attach_mail_manually (_odoo_write_date DESC);

-- Model: fetchmail.attach.mail.manually.mail
-- Module: fetchmail_attach_from_folder
CREATE TABLE IF NOT EXISTS odoo_shadow_fetchmail_attach_mail_manually_mail (
    id bigint PRIMARY KEY,
    body text,
    date timestamptz,
    email_from text,
    msgid text,
    object_id jsonb,
    subject text,
    wizard_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_fetchmail_attach_mail_manually_mail_write_date
    ON odoo_shadow_fetchmail_attach_mail_manually_mail (_odoo_write_date DESC);

-- Model: fetchmail.server
-- Module: fetchmail_attach_from_folder
CREATE TABLE IF NOT EXISTS odoo_shadow_fetchmail_server (
    id bigint PRIMARY KEY,
    cleanup_days bigint,
    cleanup_folder text,
    error_notice_template_id bigint,
    folders_available text,  -- computed, stored
    folders_only boolean,
    object_id bigint,
    purge_days bigint,
    server_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_fetchmail_server_write_date
    ON odoo_shadow_fetchmail_server (_odoo_write_date DESC);

-- Model: fetchmail.server.folder
-- Module: fetchmail_attach_from_folder
CREATE TABLE IF NOT EXISTS odoo_shadow_fetchmail_server_folder (
    id bigint PRIMARY KEY,
    action_id bigint,
    active boolean,
    archive_path text,
    delete_matching boolean,
    domain text,
    fetch_unseen_only boolean,
    flag_nonmatching boolean,
    mail_field text,
    match_algorithm text,
    match_first boolean,
    model_field text,
    model_id bigint,
    model_order text,
    msg_state text,
    path text,
    sequence bigint,
    server_id bigint,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_fetchmail_server_folder_write_date
    ON odoo_shadow_fetchmail_server_folder (_odoo_write_date DESC);

-- Model: finance.bir.deadline
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_bir_deadline (
    id bigint PRIMARY KEY,
    active boolean,
    deadline_date date,
    description text,
    display_name text,  -- computed, stored
    form_type text,
    name text,
    period_covered text,
    responsible_approval_id bigint,
    responsible_prep_id bigint,
    responsible_review_id bigint,
    state text,
    target_payment_approval_date date,  -- computed, stored
    target_prep_date date,  -- computed, stored
    target_report_approval_date date,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_bir_deadline_write_date
    ON odoo_shadow_finance_bir_deadline (_odoo_write_date DESC);

-- Model: finance.ppm.bir.calendar
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_ppm_bir_calendar (
    id bigint PRIMARY KEY,
    description text,
    filing_deadline date,
    form_code text,
    form_name text,
    period text,
    responsible_role text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_ppm_bir_calendar_write_date
    ON odoo_shadow_finance_ppm_bir_calendar (_odoo_write_date DESC);

-- Model: finance.ppm.dashboard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_ppm_dashboard (
    id bigint PRIMARY KEY,
    failures_24h bigint,
    last_message text,
    last_run_at timestamptz,
    last_status text,
    name text,
    next_scheduled_at timestamptz,
    sequence bigint,
    status_color text,  -- computed, stored
    total_runs bigint,
    workflow_code text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_ppm_dashboard_write_date
    ON odoo_shadow_finance_ppm_dashboard (_odoo_write_date DESC);

-- Model: finance.ppm.import.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_ppm_import_wizard (
    id bigint PRIMARY KEY,
    error_log text,
    file_data bytea,
    file_name text,
    file_type text,  -- computed, stored
    import_summary text,
    import_type text,
    records_created bigint,
    records_failed bigint,
    records_skipped bigint,
    records_updated bigint,
    skip_header boolean,
    state text,
    update_existing boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_ppm_import_wizard_write_date
    ON odoo_shadow_finance_ppm_import_wizard (_odoo_write_date DESC);

-- Model: finance.ppm.logframe
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_ppm_logframe (
    id bigint PRIMARY KEY,
    code text,
    description text,
    kpi_baseline text,
    kpi_measure text,
    kpi_target text,
    level text,
    measurement_frequency text,
    name text,
    parent_id bigint,
    parent_path text,
    responsible_role text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_ppm_logframe_write_date
    ON odoo_shadow_finance_ppm_logframe (_odoo_write_date DESC);

-- Model: finance.ppm.ph.holiday
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_ppm_ph_holiday (
    id bigint PRIMARY KEY,
    date date,
    description text,
    holiday_type text,
    is_nationwide boolean,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_ppm_ph_holiday_write_date
    ON odoo_shadow_finance_ppm_ph_holiday (_odoo_write_date DESC);

-- Model: finance.ppm.tdi.audit
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_ppm_tdi_audit (
    id bigint PRIMARY KEY,
    display_name text,  -- computed, stored
    error_log text,
    file_name text,
    has_errors boolean,  -- computed, stored
    import_date timestamptz,
    import_summary text,
    import_type text,
    records_created bigint,
    records_failed bigint,
    records_skipped bigint,
    records_updated bigint,
    state text,
    success_rate double precision,  -- computed, stored
    total_records bigint,  -- computed, stored
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_ppm_tdi_audit_write_date
    ON odoo_shadow_finance_ppm_tdi_audit (_odoo_write_date DESC);

-- Model: finance.task
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_task (
    id bigint PRIMARY KEY,
    approve_done boolean,
    approve_done_by bigint,
    approve_done_date timestamptz,
    approve_due_date date,
    approve_user_id bigint,
    bir_form_type text,
    bir_reference text,
    bir_return_id bigint,
    closing_id bigint,
    company_id bigint,
    days_overdue bigint,  -- computed, stored
    filed_date timestamptz,
    filing_due_date date,
    is_overdue boolean,  -- computed, stored
    name text,
    notes text,
    phase text,
    prep_done boolean,
    prep_done_by bigint,
    prep_done_date timestamptz,
    prep_due_date date,
    prep_user_id bigint,
    review_done boolean,
    review_done_by bigint,
    review_done_date timestamptz,
    review_due_date date,
    review_user_id bigint,
    sequence bigint,
    state text,  -- computed, stored
    task_type text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_task_write_date
    ON odoo_shadow_finance_task (_odoo_write_date DESC);

-- Model: finance.task.template
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_finance_task_template (
    id bigint PRIMARY KEY,
    active boolean,
    approve_day_offset bigint,
    approve_user_id bigint,
    bir_form_type text,
    description text,
    filing_day_offset bigint,
    frequency text,
    name text,
    oca_module text,
    odoo_model text,
    phase text,
    prep_day_offset bigint,
    prep_user_id bigint,
    review_day_offset bigint,
    review_user_id bigint,
    sequence bigint,
    task_count bigint,  -- computed, stored
    task_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_finance_task_template_write_date
    ON odoo_shadow_finance_task_template (_odoo_write_date DESC);

-- Model: fs.storage
-- Module: attachment_synchronize
CREATE TABLE IF NOT EXISTS odoo_shadow_fs_storage (
    id bigint PRIMARY KEY,
    export_task_count bigint,  -- computed, stored
    import_task_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_fs_storage_write_date
    ON odoo_shadow_fs_storage (_odoo_write_date DESC);

-- Model: general.ledger.report.wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_general_ledger_report_wizard (
    id bigint PRIMARY KEY,
    account_code_from bigint,
    account_code_to bigint,
    centralize boolean,
    date_from date,
    date_range_id bigint,
    date_to date,
    domain text,
    foreign_currency boolean,
    fy_start_date date,  -- computed, stored
    grouped_by text,
    hide_account_at_0 boolean,
    only_one_unaffected_earnings_account boolean,
    payable_accounts_only boolean,
    receivable_accounts_only boolean,
    show_cost_center boolean,
    target_move text,
    unaffected_earnings_account bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_general_ledger_report_wizard_write_date
    ON odoo_shadow_general_ledger_report_wizard (_odoo_write_date DESC);

-- Model: hr.employee
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_hr_employee (
    id bigint PRIMARY KEY,
    x_master_control_offboarded boolean,
    x_master_control_onboarded boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_hr_employee_write_date
    ON odoo_shadow_hr_employee (_odoo_write_date DESC);

-- Model: hr.expense
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_hr_expense (
    id bigint PRIMARY KEY,
    project_id bigint,
    requires_project boolean,  -- computed, stored
    travel_request_id bigint,
    x_master_control_submitted boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_hr_expense_write_date
    ON odoo_shadow_hr_expense (_odoo_write_date DESC);

-- Model: hr.timesheet.switch
-- Module: project_timesheet_time_control
CREATE TABLE IF NOT EXISTS odoo_shadow_hr_timesheet_switch (
    id bigint PRIMARY KEY,
    analytic_line_id bigint,
    company_id bigint,
    date_time timestamptz,
    date_time_end timestamptz,
    name text,
    project_id bigint,  -- computed, stored
    running_timer_duration double precision,  -- computed, stored
    running_timer_id bigint,
    running_timer_start timestamptz,
    task_id bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_hr_timesheet_switch_write_date
    ON odoo_shadow_hr_timesheet_switch (_odoo_write_date DESC);

-- Model: hr.timesheet.time_control.mixin
-- Module: project_timesheet_time_control
CREATE TABLE IF NOT EXISTS odoo_shadow_hr_timesheet_time_control_mixin (
    id bigint PRIMARY KEY,
    show_time_control text,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_hr_timesheet_time_control_mixin_write_date
    ON odoo_shadow_hr_timesheet_time_control_mixin (_odoo_write_date DESC);

-- Model: iap.account
-- Module: iap_alternative_provider
CREATE TABLE IF NOT EXISTS odoo_shadow_iap_account (
    id bigint PRIMARY KEY,
    provider text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_iap_account_write_date
    ON odoo_shadow_iap_account (_odoo_write_date DESC);

-- Model: import.xlsx.wizard
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_import_xlsx_wizard (
    id bigint PRIMARY KEY,
    datas bytea,
    filename text,
    fname text,
    import_file bytea,
    res_id bigint,
    res_model text,
    state text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_import_xlsx_wizard_write_date
    ON odoo_shadow_import_xlsx_wizard (_odoo_write_date DESC);

-- Model: ipai.agent.knowledge_source
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_agent_knowledge_source (
    id bigint PRIMARY KEY,
    attachment_id bigint,
    content_text text,
    is_active boolean,
    key text,
    kind text,
    model_name text,
    name text,
    tags text,
    url text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_agent_knowledge_source_write_date
    ON odoo_shadow_ipai_agent_knowledge_source (_odoo_write_date DESC);

-- Model: ipai.agent.run
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_agent_run (
    id bigint PRIMARY KEY,
    completed_at timestamptz,
    duration_seconds double precision,  -- computed, stored
    error_text text,
    input_json text,
    input_text text,
    name text,
    output_json text,
    output_text text,
    skill_id bigint,
    skill_key text,
    started_at timestamptz,
    state text,
    tool_trace_json text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_agent_run_write_date
    ON odoo_shadow_ipai_agent_run (_odoo_write_date DESC);

-- Model: ipai.agent.skill
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_agent_skill (
    id bigint PRIMARY KEY,
    description text,
    guardrails text,
    intents text,
    is_active boolean,
    key text,
    name text,
    run_count bigint,  -- computed, stored
    version text,
    workflow_json text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_agent_skill_write_date
    ON odoo_shadow_ipai_agent_skill (_odoo_write_date DESC);

-- Model: ipai.agent.tool
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_agent_tool (
    id bigint PRIMARY KEY,
    description text,
    input_schema_json text,
    is_active boolean,
    key text,
    name text,
    output_schema_json text,
    requires_admin boolean,
    target_method text,
    target_model text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_agent_tool_write_date
    ON odoo_shadow_ipai_agent_tool (_odoo_write_date DESC);

-- Model: ipai.ai_studio.run
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_ai_studio_run (
    id bigint PRIMARY KEY,
    generated_files_json text,
    module_name text,
    name text,
    prompt text,
    spec_json text,
    state text,
    validation_ok boolean,
    validation_report text,
    workspace_path text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_ai_studio_run_write_date
    ON odoo_shadow_ipai_ai_studio_run (_odoo_write_date DESC);

-- Model: ipai.approval.mixin
-- Module: ipai_platform_approvals
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_approval_mixin (
    id bigint PRIMARY KEY,
    approval_notes text,
    approval_requested boolean,
    approval_requested_by bigint,
    approval_requested_date timestamptz,
    current_approver_id bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_approval_mixin_write_date
    ON odoo_shadow_ipai_approval_mixin (_odoo_write_date DESC);

-- Model: ipai.ask_ai_chatter.request
-- Module: ipai_ask_ai_chatter
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_ask_ai_chatter_request (
    id bigint PRIMARY KEY,
    error text,
    model text,
    payload_json text,
    question text,
    requested_by bigint,
    res_id bigint,
    response text,
    response_json text,
    source_message_id bigint,
    state text,
    uuid text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_ask_ai_chatter_request_write_date
    ON odoo_shadow_ipai_ask_ai_chatter_request (_odoo_write_date DESC);

-- Model: ipai.asset
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_asset (
    id bigint PRIMARY KEY,
    active_checkout_id bigint,  -- computed, stored
    barcode text,
    category_id bigint,
    code text,
    currency_id bigint,
    current_value numeric(16, 2),  -- computed, stored
    custodian_id bigint,
    description text,
    image jsonb,
    location_id bigint,
    name text,
    purchase_date date,
    purchase_value numeric(16, 2),
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_asset_write_date
    ON odoo_shadow_ipai_asset (_odoo_write_date DESC);

-- Model: ipai.asset.category
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_asset_category (
    id bigint PRIMARY KEY,
    allow_reservations boolean,
    asset_count bigint,  -- computed, stored
    code text,
    description text,
    max_checkout_days bigint,
    name text,
    requires_approval boolean,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_asset_category_write_date
    ON odoo_shadow_ipai_asset_category (_odoo_write_date DESC);

-- Model: ipai.asset.checkout
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_asset_checkout (
    id bigint PRIMARY KEY,
    actual_return_date timestamptz,
    approval_date timestamptz,
    approved_by bigint,
    asset_id bigint,
    checkout_date timestamptz,
    checkout_notes text,
    condition_on_return text,
    employee_id bigint,
    expected_return_date date,
    name text,  -- computed, stored
    return_notes text,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_asset_checkout_write_date
    ON odoo_shadow_ipai_asset_checkout (_odoo_write_date DESC);

-- Model: ipai.asset.reservation
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_asset_reservation (
    id bigint PRIMARY KEY,
    asset_id bigint,
    employee_id bigint,
    end_date date,
    name text,  -- computed, stored
    notes text,
    start_date date,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_asset_reservation_write_date
    ON odoo_shadow_ipai_asset_reservation (_odoo_write_date DESC);

-- Model: ipai.audit.log
-- Module: ipai_platform_audit
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_audit_log (
    id bigint PRIMARY KEY,
    action text,
    display_name text,  -- computed, stored
    field_name text,
    new_value text,
    old_value text,
    res_id bigint,
    res_model text,
    res_name text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_audit_log_write_date
    ON odoo_shadow_ipai_audit_log (_odoo_write_date DESC);

-- Model: ipai.audit.mixin
-- Module: ipai_platform_audit
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_audit_mixin (
    id bigint PRIMARY KEY,
    audit_log_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_audit_mixin_write_date
    ON odoo_shadow_ipai_audit_mixin (_odoo_write_date DESC);

-- Model: ipai.bir.dat.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_bir_dat_wizard (
    id bigint PRIMARY KEY,
    currency_id bigint,
    date_end date,
    date_start date,
    file_data bytea,
    file_name text,
    record_count bigint,
    report_type text,
    state text,
    total_amount numeric(16, 2),
    total_tax numeric(16, 2),
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_bir_dat_wizard_write_date
    ON odoo_shadow_ipai_bir_dat_wizard (_odoo_write_date DESC);

-- Model: ipai.bir.form.schedule
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_bir_form_schedule (
    id bigint PRIMARY KEY,
    approval_date date,
    bir_deadline date,
    filing_date date,
    form_code text,
    last_reminder_sent timestamptz,
    period text,
    prep_date date,
    reminder_count bigint,
    responsible_approval_id bigint,
    responsible_prep_id bigint,
    responsible_review_id bigint,
    review_date date,
    status text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_bir_form_schedule_write_date
    ON odoo_shadow_ipai_bir_form_schedule (_odoo_write_date DESC);

-- Model: ipai.bir.process.step
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_bir_process_step (
    id bigint PRIMARY KEY,
    detail text,
    person_id bigint,
    role text,
    schedule_id bigint,
    step_no bigint,
    target_offset bigint,
    title text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_bir_process_step_write_date
    ON odoo_shadow_ipai_bir_process_step (_odoo_write_date DESC);

-- Model: ipai.bir.schedule.item
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_bir_schedule_item (
    id bigint PRIMARY KEY,
    active boolean,
    bir_form text,
    deadline date,
    im_xml_id text,
    period_covered text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_bir_schedule_item_write_date
    ON odoo_shadow_ipai_bir_schedule_item (_odoo_write_date DESC);

-- Model: ipai.bir.schedule.line
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_bir_schedule_line (
    id bigint PRIMARY KEY,
    approve_by_code text,
    approve_due_date date,
    bir_form text,
    deadline_date date,
    notes text,
    period_label text,
    prep_by_code text,
    prep_due_date date,
    review_by_code text,
    review_due_date date,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_bir_schedule_line_write_date
    ON odoo_shadow_ipai_bir_schedule_line (_odoo_write_date DESC);

-- Model: ipai.bir.schedule.step
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_bir_schedule_step (
    id bigint PRIMARY KEY,
    activity_type text,
    business_days_before bigint,
    item_id bigint,
    on_or_before_deadline boolean,
    role_code text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_bir_schedule_step_write_date
    ON odoo_shadow_ipai_bir_schedule_step (_odoo_write_date DESC);

-- Model: ipai.close.generated.map
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_close_generated_map (
    id bigint PRIMARY KEY,
    external_key text,
    generation_run_id bigint,
    operation text,
    run_id bigint,
    seed_hash text,
    seed_hash_at_generation text,
    task_id bigint,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_close_generated_map_write_date
    ON odoo_shadow_ipai_close_generated_map (_odoo_write_date DESC);

-- Model: ipai.close.generation.run
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_close_generation_run (
    id bigint PRIMARY KEY,
    created_count bigint,
    cycle_code text,
    cycle_key text,
    cycle_type text,  -- computed, stored
    dry_run boolean,
    duration_seconds bigint,  -- computed, stored
    end_time timestamptz,
    error_count bigint,  -- computed, stored
    name text,  -- computed, stored
    obsolete_marked_count bigint,
    period_end date,
    period_start date,
    project_id bigint,
    report_json jsonb,
    report_status text,  -- computed, stored
    seed_id text,
    seed_version text,
    start_time timestamptz,
    status text,
    task_count_created bigint,
    task_count_obsolete bigint,
    task_count_skipped bigint,
    task_count_updated bigint,
    unchanged_count bigint,
    unresolved_assignee_count bigint,
    updated_count bigint,
    user_id bigint,
    warning_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_close_generation_run_write_date
    ON odoo_shadow_ipai_close_generation_run (_odoo_write_date DESC);

-- Model: ipai.close.generator
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_close_generator (
    id bigint PRIMARY KEY,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_close_generator_write_date
    ON odoo_shadow_ipai_close_generator (_odoo_write_date DESC);

-- Model: ipai.close.task.step
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_close_task_step (
    id bigint PRIMARY KEY,
    default_employee_code text,
    sequence bigint,
    step_code text,
    step_name text,
    template_id bigint,
    user_id bigint,  -- computed, stored
    x_legacy_template_code text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_close_task_step_write_date
    ON odoo_shadow_ipai_close_task_step (_odoo_write_date DESC);

-- Model: ipai.close.task.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_close_task_template (
    id bigint PRIMARY KEY,
    category_code text,
    category_name text,
    category_seq bigint,
    critical_path boolean,
    cycle_code text,
    duration_days bigint,
    employee_code text,
    is_active boolean,
    offset_from_period_end bigint,
    phase_code text,
    phase_name text,
    phase_seq bigint,
    phase_type text,
    recurrence_rule text,
    responsible_role text,
    seed_hash text,  -- computed, stored
    step_code text,
    step_seq bigint,
    task_description text,
    task_name_template text,
    template_code text,
    template_seq bigint,
    template_version text,
    wbs_code_template text,
    workstream_code text,
    workstream_name text,
    workstream_seq bigint,
    x_legacy_migration boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_close_task_template_write_date
    ON odoo_shadow_ipai_close_task_template (_odoo_write_date DESC);

-- Model: ipai.convert.phases.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_convert_phases_wizard (
    id bigint PRIMARY KEY,
    im1_keywords text,
    im1_name text,
    im2_keywords text,
    im2_name text,
    move_tasks_by_keyword boolean,
    parent_project_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_convert_phases_wizard_write_date
    ON odoo_shadow_ipai_convert_phases_wizard (_odoo_write_date DESC);

-- Model: ipai.directory.person
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_directory_person (
    id bigint PRIMARY KEY,
    active boolean,
    code text,
    email text,
    name text,
    role text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_directory_person_write_date
    ON odoo_shadow_ipai_directory_person (_odoo_write_date DESC);

-- Model: ipai.equipment.asset
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_equipment_asset (
    id bigint PRIMARY KEY,
    booking_count bigint,  -- computed, stored
    category_id bigint,
    company_id bigint,
    condition text,
    image_1920 jsonb,
    incident_count bigint,  -- computed, stored
    location_id bigint,
    name text,
    product_id bigint,
    serial_number text,
    status text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_equipment_asset_write_date
    ON odoo_shadow_ipai_equipment_asset (_odoo_write_date DESC);

-- Model: ipai.equipment.booking
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_equipment_booking (
    id bigint PRIMARY KEY,
    asset_id bigint,
    borrower_id bigint,
    end_datetime timestamptz,
    is_overdue boolean,  -- computed, stored
    name text,
    project_id bigint,
    start_datetime timestamptz,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_equipment_booking_write_date
    ON odoo_shadow_ipai_equipment_booking (_odoo_write_date DESC);

-- Model: ipai.equipment.incident
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_equipment_incident (
    id bigint PRIMARY KEY,
    asset_id bigint,
    booking_id bigint,
    description text,
    name text,
    reported_by bigint,
    severity text,
    status text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_equipment_incident_write_date
    ON odoo_shadow_ipai_equipment_incident (_odoo_write_date DESC);

-- Model: ipai.finance.bir_schedule
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_bir_schedule (
    id bigint PRIMARY KEY,
    approval_deadline date,
    approval_task_id bigint,
    approver_id bigint,
    completion_pct double precision,
    filing_deadline date,
    logframe_id bigint,
    name text,
    period_covered text,
    prep_deadline date,
    prep_task_id bigint,
    review_deadline date,
    review_task_id bigint,
    reviewer_id bigint,
    status text,
    supervisor_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_bir_schedule_write_date
    ON odoo_shadow_ipai_finance_bir_schedule (_odoo_write_date DESC);

-- Model: ipai.finance.close.generate.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_close_generate_wizard (
    id bigint PRIMARY KEY,
    calendar_id bigint,
    month bigint,
    year bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_close_generate_wizard_write_date
    ON odoo_shadow_ipai_finance_close_generate_wizard (_odoo_write_date DESC);

-- Model: ipai.finance.directory
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_directory (
    id bigint PRIMARY KEY,
    active boolean,
    code text,
    email text,
    name text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_directory_write_date
    ON odoo_shadow_ipai_finance_directory (_odoo_write_date DESC);

-- Model: ipai.finance.logframe
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_logframe (
    id bigint PRIMARY KEY,
    assumptions text,
    code text,
    indicators text,
    level text,
    means_of_verification text,
    name text,
    sequence bigint,
    task_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_logframe_write_date
    ON odoo_shadow_ipai_finance_logframe (_odoo_write_date DESC);

-- Model: ipai.finance.person
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_person (
    id bigint PRIMARY KEY,
    code text,
    email text,
    name text,
    role text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_person_write_date
    ON odoo_shadow_ipai_finance_person (_odoo_write_date DESC);

-- Model: ipai.finance.ppm.golive.checklist
-- Module: ipai_finance_ppm_golive
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_ppm_golive_checklist (
    id bigint PRIMARY KEY,
    completed_items bigint,  -- computed, stored
    completion_pct double precision,  -- computed, stored
    create_date timestamptz,
    created_by bigint,
    director_id bigint,
    director_notes text,
    director_review_date timestamptz,
    director_signoff_date timestamptz,
    name text,
    senior_supervisor_id bigint,
    senior_supervisor_notes text,
    senior_supervisor_review_date timestamptz,
    state text,
    supervisor_id bigint,
    supervisor_notes text,
    supervisor_review_date timestamptz,
    total_items bigint,  -- computed, stored
    version text,
    write_date timestamptz,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_ppm_golive_checklist_write_date
    ON odoo_shadow_ipai_finance_ppm_golive_checklist (_odoo_write_date DESC);

-- Model: ipai.finance.ppm.golive.item
-- Module: ipai_finance_ppm_golive
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_ppm_golive_item (
    id bigint PRIMARY KEY,
    checked_by bigint,
    checked_date timestamptz,
    description text,
    evidence_url text,
    is_checked boolean,
    is_critical boolean,
    name text,
    notes text,
    section_id bigint,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_ppm_golive_item_write_date
    ON odoo_shadow_ipai_finance_ppm_golive_item (_odoo_write_date DESC);

-- Model: ipai.finance.ppm.golive.section
-- Module: ipai_finance_ppm_golive
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_ppm_golive_section (
    id bigint PRIMARY KEY,
    completed_items bigint,  -- computed, stored
    completion_pct double precision,  -- computed, stored
    description text,
    name text,
    section_type text,
    sequence bigint,
    total_items bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_ppm_golive_section_write_date
    ON odoo_shadow_ipai_finance_ppm_golive_section (_odoo_write_date DESC);

-- Model: ipai.finance.seed.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_seed_wizard (
    id bigint PRIMARY KEY,
    strict boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_seed_wizard_write_date
    ON odoo_shadow_ipai_finance_seed_wizard (_odoo_write_date DESC);

-- Model: ipai.finance.task.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_finance_task_template (
    id bigint PRIMARY KEY,
    active boolean,
    anchor text,
    approval_duration double precision,
    approve_by_code text,
    approved_by_id bigint,
    bir_form_id bigint,
    category text,
    day_of_month bigint,
    default_duration_days bigint,
    description text,
    employee_code_id bigint,
    name text,
    offset_days bigint,
    prep_by_code text,
    prep_duration double precision,
    review_by_code text,
    review_duration double precision,
    reviewed_by_id bigint,
    sequence bigint,
    task_category text,
    trigger_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_finance_task_template_write_date
    ON odoo_shadow_ipai_finance_task_template (_odoo_write_date DESC);

-- Model: ipai.generate.bir.tasks.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_generate_bir_tasks_wizard (
    id bigint PRIMARY KEY,
    date_from date,
    date_to date,
    dry_run boolean,
    program_project_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_generate_bir_tasks_wizard_write_date
    ON odoo_shadow_ipai_generate_bir_tasks_wizard (_odoo_write_date DESC);

-- Model: ipai.generate.im.projects.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_generate_im_projects_wizard (
    id bigint PRIMARY KEY,
    create_bir_tasks boolean,
    create_children boolean,
    create_month_end_tasks boolean,
    project_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_generate_im_projects_wizard_write_date
    ON odoo_shadow_ipai_generate_im_projects_wizard (_odoo_write_date DESC);

-- Model: ipai.generate.month.end.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_generate_month_end_wizard (
    id bigint PRIMARY KEY,
    anchor_date date,
    dry_run boolean,
    program_project_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_generate_month_end_wizard_write_date
    ON odoo_shadow_ipai_generate_month_end_wizard (_odoo_write_date DESC);

-- Model: ipai.grid.column
-- Module: ipai_grid_view
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_grid_column (
    id bigint PRIMARY KEY,
    alignment text,
    cell_css_class text,
    clickable boolean,
    column_type text,
    css_class text,
    currency_field text,
    date_format text,
    decimal_places bigint,
    display_name text,  -- computed, stored
    editable boolean,
    field_name text,
    field_type text,
    filterable boolean,
    format_string text,
    grid_view_id bigint,
    header_css_class text,
    is_action_column boolean,
    is_avatar_column boolean,
    is_primary boolean,
    is_selection_column boolean,
    label text,
    max_width bigint,
    min_width bigint,
    resizable boolean,
    searchable boolean,
    sequence bigint,
    sortable boolean,
    visible boolean,
    widget_options text,
    width bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_grid_column_write_date
    ON odoo_shadow_ipai_grid_column (_odoo_write_date DESC);

-- Model: ipai.grid.filter
-- Module: ipai_grid_view
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_grid_filter (
    id bigint PRIMARY KEY,
    active boolean,
    color text,
    condition_count bigint,  -- computed, stored
    domain text,
    filter_json text,
    grid_view_id bigint,
    icon text,
    is_default boolean,
    is_global boolean,
    name text,
    sequence bigint,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_grid_filter_write_date
    ON odoo_shadow_ipai_grid_filter (_odoo_write_date DESC);

-- Model: ipai.grid.filter.condition
-- Module: ipai_grid_view
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_grid_filter_condition (
    id bigint PRIMARY KEY,
    field_label text,
    field_name text,
    field_type text,
    filter_id bigint,
    operator text,
    value_boolean boolean,
    value_char text,
    value_date date,
    value_datetime timestamptz,
    value_float double precision,
    value_integer bigint,
    value_many2one bigint,
    value_selection text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_grid_filter_condition_write_date
    ON odoo_shadow_ipai_grid_filter_condition (_odoo_write_date DESC);

-- Model: ipai.grid.view
-- Module: ipai_grid_view
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_grid_view (
    id bigint PRIMARY KEY,
    active boolean,
    active_filter_id bigint,
    column_count bigint,  -- computed, stored
    config_json text,
    enable_column_reorder boolean,
    enable_column_resize boolean,
    enable_export boolean,
    enable_quick_search boolean,
    enable_row_selection boolean,
    model_id bigint,
    model_name text,
    name text,
    page_size bigint,
    page_size_options text,
    sequence bigint,
    show_checkboxes boolean,
    show_row_numbers boolean,
    sort_json text,
    view_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_grid_view_write_date
    ON odoo_shadow_ipai_grid_view (_odoo_write_date DESC);

-- Model: ipai.month.end.closing
-- Module: ipai_month_end
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_month_end_closing (
    id bigint PRIMARY KEY,
    company_id bigint,
    completed_tasks bigint,  -- computed, stored
    last_workday date,  -- computed, stored
    name text,
    overdue_tasks bigint,  -- computed, stored
    period_date date,
    progress double precision,  -- computed, stored
    state text,
    total_tasks bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_month_end_closing_write_date
    ON odoo_shadow_ipai_month_end_closing (_odoo_write_date DESC);

-- Model: ipai.month.end.task
-- Module: ipai_month_end
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_month_end_task (
    id bigint PRIMARY KEY,
    approve_done boolean,
    approve_done_by bigint,
    approve_done_date timestamptz,
    approve_due_date date,
    approve_user_id bigint,
    closing_id bigint,
    days_overdue bigint,  -- computed, stored
    is_overdue boolean,  -- computed, stored
    name text,
    notes text,
    phase text,
    prep_done boolean,
    prep_done_by bigint,
    prep_done_date timestamptz,
    prep_due_date date,
    prep_user_id bigint,
    review_done boolean,
    review_done_by bigint,
    review_done_date timestamptz,
    review_due_date date,
    review_user_id bigint,
    sequence bigint,
    state text,  -- computed, stored
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_month_end_task_write_date
    ON odoo_shadow_ipai_month_end_task (_odoo_write_date DESC);

-- Model: ipai.month.end.task.template
-- Module: ipai_month_end
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_month_end_task_template (
    id bigint PRIMARY KEY,
    active boolean,
    approve_day_offset bigint,
    approve_user_id bigint,
    description text,
    name text,
    oca_module text,
    odoo_model text,
    phase text,
    prep_day_offset bigint,
    prep_user_id bigint,
    review_day_offset bigint,
    review_user_id bigint,
    sequence bigint,
    task_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_month_end_task_template_write_date
    ON odoo_shadow_ipai_month_end_task_template (_odoo_write_date DESC);

-- Model: ipai.month.end.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_month_end_template (
    id bigint PRIMARY KEY,
    active boolean,
    category text,
    default_im_xml_id text,
    task_base_name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_month_end_template_write_date
    ON odoo_shadow_ipai_month_end_template (_odoo_write_date DESC);

-- Model: ipai.month.end.template.step
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_month_end_template_step (
    id bigint PRIMARY KEY,
    activity_type text,
    business_days_before bigint,
    offset_days bigint,
    role_code text,
    sequence bigint,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_month_end_template_step_write_date
    ON odoo_shadow_ipai_month_end_template_step (_odoo_write_date DESC);

-- Model: ipai.ocr.job
-- Module: ipai_ocr_gateway
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_ocr_job (
    id bigint PRIMARY KEY,
    attachment_id bigint,
    attachment_mimetype text,
    attachment_name text,
    completed_at timestamptz,
    confidence_score double precision,
    duration_seconds double precision,  -- computed, stored
    error_message text,
    name text,
    output_attachment_id bigint,
    provider_id bigint,
    res_id bigint,
    res_model text,
    result_json text,
    result_text text,
    retry_count bigint,
    started_at timestamptz,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_ocr_job_write_date
    ON odoo_shadow_ipai_ocr_job (_odoo_write_date DESC);

-- Model: ipai.ocr.provider
-- Module: ipai_ocr_gateway
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_ocr_provider (
    id bigint PRIMARY KEY,
    active boolean,
    auth_param_key text,
    auth_type text,
    base_url text,
    job_count bigint,  -- computed, stored
    max_retries bigint,
    name text,
    notes text,
    provider_type text,
    sequence bigint,
    supported_formats text,
    timeout bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_ocr_provider_write_date
    ON odoo_shadow_ipai_ocr_provider (_odoo_write_date DESC);

-- Model: ipai.permission
-- Module: ipai_platform_permissions
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_permission (
    id bigint PRIMARY KEY,
    active boolean,
    group_id bigint,
    name text,
    permission_level text,
    role text,
    scope_ref jsonb,
    scope_type text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_permission_write_date
    ON odoo_shadow_ipai_permission (_odoo_write_date DESC);

-- Model: ipai.ph.holiday
-- Module: ipai_month_end
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_ph_holiday (
    id bigint PRIMARY KEY,
    date date,
    holiday_type text,
    name text,
    year bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_ph_holiday_write_date
    ON odoo_shadow_ipai_ph_holiday (_odoo_write_date DESC);

-- Model: ipai.share.token
-- Module: ipai_platform_permissions
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_share_token (
    id bigint PRIMARY KEY,
    active boolean,
    created_by bigint,
    expires_at timestamptz,
    is_public boolean,
    name text,
    permission_level text,
    scope_ref jsonb,
    scope_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_share_token_write_date
    ON odoo_shadow_ipai_share_token (_odoo_write_date DESC);

-- Model: ipai.sms.message
-- Module: ipai_sms_gateway
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_sms_message (
    id bigint PRIMARY KEY,
    body text,
    cost double precision,
    delivered_at timestamptz,
    error_code text,
    error_message text,
    external_id text,
    from_number text,
    name text,
    partner_id bigint,
    provider_id bigint,
    raw_response text,
    res_id bigint,
    res_model text,
    retry_count bigint,
    segments bigint,
    sent_at timestamptz,
    state text,
    to_number text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_sms_message_write_date
    ON odoo_shadow_ipai_sms_message (_odoo_write_date DESC);

-- Model: ipai.sms.provider
-- Module: ipai_sms_gateway
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_sms_provider (
    id bigint PRIMARY KEY,
    account_sid text,
    active boolean,
    auth_param_key text,
    base_url text,
    max_retries bigint,
    message_count bigint,  -- computed, stored
    name text,
    notes text,
    provider_type text,
    sender_id text,
    sequence bigint,
    timeout bigint,
    webhook_enabled boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_sms_provider_write_date
    ON odoo_shadow_ipai_sms_provider (_odoo_write_date DESC);

-- Model: ipai.studio.ai.history
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_studio_ai_history (
    id bigint PRIMARY KEY,
    analysis text,
    automation_id bigint,
    command text,
    command_type text,
    confidence double precision,
    feedback_comment text,
    feedback_score text,
    field_id bigint,
    model_id bigint,
    model_name text,
    result text,
    result_message text,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_studio_ai_history_write_date
    ON odoo_shadow_ipai_studio_ai_history (_odoo_write_date DESC);

-- Model: ipai.studio.ai.wizard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_studio_ai_wizard (
    id bigint PRIMARY KEY,
    analysis_json text,
    command text,
    command_type text,
    confidence double precision,
    context_model_id bigint,
    created_field_id bigint,
    field_label text,
    field_name text,
    field_required boolean,
    field_type text,
    history_id bigint,
    is_ready boolean,
    message text,
    relation_model_id bigint,
    result_message text,
    selection_options text,
    state text,
    target_model_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_studio_ai_wizard_write_date
    ON odoo_shadow_ipai_studio_ai_wizard (_odoo_write_date DESC);

-- Model: ipai.travel.request
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_travel_request (
    id bigint PRIMARY KEY,
    company_id bigint,
    currency_id bigint,
    destination text,
    employee_id bigint,
    end_date date,
    estimated_budget numeric(16, 2),
    name text,
    project_id bigint,
    purpose text,
    start_date date,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_travel_request_write_date
    ON odoo_shadow_ipai_travel_request (_odoo_write_date DESC);

-- Model: ipai.workflow.mixin
-- Module: ipai_platform_workflow
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workflow_mixin (
    id bigint PRIMARY KEY,
    workflow_state text,
    workflow_state_date timestamptz,
    workflow_state_user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workflow_mixin_write_date
    ON odoo_shadow_ipai_workflow_mixin (_odoo_write_date DESC);

-- Model: ipai.workos.block
-- Module: ipai_workos_blocks
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_block (
    id bigint PRIMARY KEY,
    attachment_id bigint,
    block_type text,
    callout_color text,
    callout_icon text,
    content_html text,  -- computed, stored
    content_json text,
    content_text text,  -- computed, stored
    is_checked boolean,
    is_collapsed boolean,
    name text,  -- computed, stored
    page_id bigint,
    parent_block_id bigint,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_block_write_date
    ON odoo_shadow_ipai_workos_block (_odoo_write_date DESC);

-- Model: ipai.workos.canvas
-- Module: ipai_workos_canvas
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_canvas (
    id bigint PRIMARY KEY,
    active boolean,
    name text,
    nodes_json text,
    page_id bigint,
    viewport_json text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_canvas_write_date
    ON odoo_shadow_ipai_workos_canvas (_odoo_write_date DESC);

-- Model: ipai.workos.comment
-- Module: ipai_workos_collab
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_comment (
    id bigint PRIMARY KEY,
    anchor_block_id bigint,
    author_id bigint,
    content text,
    content_text text,  -- computed, stored
    is_resolved boolean,
    parent_id bigint,
    reply_count bigint,  -- computed, stored
    resolved_at timestamptz,
    resolved_by bigint,
    target_id bigint,
    target_model text,
    target_name text,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_comment_write_date
    ON odoo_shadow_ipai_workos_comment (_odoo_write_date DESC);

-- Model: ipai.workos.database
-- Module: ipai_workos_db
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_database (
    id bigint PRIMARY KEY,
    active boolean,
    description text,
    icon text,
    name text,
    page_id bigint,
    row_count bigint,  -- computed, stored
    space_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_database_write_date
    ON odoo_shadow_ipai_workos_database (_odoo_write_date DESC);

-- Model: ipai.workos.page
-- Module: ipai_workos_core
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_page (
    id bigint PRIMARY KEY,
    active boolean,
    child_count bigint,  -- computed, stored
    content_preview text,  -- computed, stored
    cover_image bytea,
    icon text,
    is_archived boolean,
    last_edited_by bigint,  -- computed, stored
    name text,
    parent_id bigint,
    parent_path text,
    sequence bigint,
    space_id bigint,  -- computed, stored
    template_id bigint,
    workspace_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_page_write_date
    ON odoo_shadow_ipai_workos_page (_odoo_write_date DESC);

-- Model: ipai.workos.property
-- Module: ipai_workos_db
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_property (
    id bigint PRIMARY KEY,
    database_id bigint,
    is_title boolean,
    is_visible boolean,
    name text,
    options_json text,
    property_type text,
    related_database_id bigint,
    sequence bigint,
    width bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_property_write_date
    ON odoo_shadow_ipai_workos_property (_odoo_write_date DESC);

-- Model: ipai.workos.row
-- Module: ipai_workos_db
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_row (
    id bigint PRIMARY KEY,
    active boolean,
    database_id bigint,
    name text,  -- computed, stored
    sequence bigint,
    values_json text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_row_write_date
    ON odoo_shadow_ipai_workos_row (_odoo_write_date DESC);

-- Model: ipai.workos.search
-- Module: ipai_workos_search
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_search (
    id bigint PRIMARY KEY,
    block_results text,
    database_results text,
    page_results text,
    query text,
    scope text,
    scope_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_search_write_date
    ON odoo_shadow_ipai_workos_search (_odoo_write_date DESC);

-- Model: ipai.workos.search.history
-- Module: ipai_workos_search
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_search_history (
    id bigint PRIMARY KEY,
    query text,
    result_count bigint,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_search_history_write_date
    ON odoo_shadow_ipai_workos_search_history (_odoo_write_date DESC);

-- Model: ipai.workos.space
-- Module: ipai_workos_core
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_space (
    id bigint PRIMARY KEY,
    active boolean,
    color bigint,
    description text,
    icon text,
    name text,
    page_count bigint,  -- computed, stored
    sequence bigint,
    visibility text,
    workspace_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_space_write_date
    ON odoo_shadow_ipai_workos_space (_odoo_write_date DESC);

-- Model: ipai.workos.template
-- Module: ipai_workos_templates
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_template (
    id bigint PRIMARY KEY,
    blocks_json text,
    category text,
    description text,
    icon text,
    is_published boolean,
    is_system boolean,
    name text,
    properties_json text,
    sequence bigint,
    views_json text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_template_write_date
    ON odoo_shadow_ipai_workos_template (_odoo_write_date DESC);

-- Model: ipai.workos.template.tag
-- Module: ipai_workos_templates
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_template_tag (
    id bigint PRIMARY KEY,
    color bigint,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_template_tag_write_date
    ON odoo_shadow_ipai_workos_template_tag (_odoo_write_date DESC);

-- Model: ipai.workos.view
-- Module: ipai_workos_views
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_view (
    id bigint PRIMARY KEY,
    config_json text,
    database_id bigint,
    date_property_id bigint,
    filter_json text,
    group_by_property_id bigint,
    is_default boolean,
    is_shared boolean,
    name text,
    sequence bigint,
    sort_json text,
    user_id bigint,
    view_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_view_write_date
    ON odoo_shadow_ipai_workos_view (_odoo_write_date DESC);

-- Model: ipai.workos.workspace
-- Module: ipai_workos_core
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workos_workspace (
    id bigint PRIMARY KEY,
    active boolean,
    color bigint,
    description text,
    icon text,
    name text,
    owner_id bigint,
    space_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workos_workspace_write_date
    ON odoo_shadow_ipai_workos_workspace (_odoo_write_date DESC);

-- Model: ipai.workspace
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workspace (
    id bigint PRIMARY KEY,
    account_manager_id bigint,
    active boolean,
    brand_name text,
    campaign_type text,
    channel_mix text,
    client_id bigint,
    closing_stage text,
    code text,
    color bigint,
    company_id bigint,
    date_end timestamptz,
    date_start timestamptz,
    engagement_count bigint,  -- computed, stored
    entity_code text,
    fiscal_period text,
    industry text,
    invoice_count bigint,  -- computed, stored
    is_critical boolean,
    name text,
    parent_id bigint,
    planned_hours double precision,
    progress double precision,
    project_count bigint,  -- computed, stored
    remaining_hours double precision,
    sequence bigint,
    stage text,
    workspace_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workspace_write_date
    ON odoo_shadow_ipai_workspace (_odoo_write_date DESC);

-- Model: ipai.workspace.link
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ipai_workspace_link (
    id bigint PRIMARY KEY,
    display_name text,  -- computed, stored
    link_type text,
    res_id bigint,
    res_model text,
    workspace_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ipai_workspace_link_write_date
    ON odoo_shadow_ipai_workspace_link (_odoo_write_date DESC);

-- Model: ir.actions.act_multi
-- Module: web_ir_actions_act_multi
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_actions (
    id bigint PRIMARY KEY,
    type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_actions_write_date
    ON odoo_shadow_ir_actions (_odoo_write_date DESC);

-- Model: ir.actions.act_window.message
-- Module: web_ir_actions_act_window_message
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_actions (
    id bigint PRIMARY KEY,
    type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_actions_write_date
    ON odoo_shadow_ir_actions (_odoo_write_date DESC);

-- Model: ir.actions.act_window.view
-- Module: web_timeline
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_actions_act_window_view (
    id bigint PRIMARY KEY,
    view_mode text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_actions_act_window_view_write_date
    ON odoo_shadow_ir_actions_act_window_view (_odoo_write_date DESC);

-- Model: ir.actions.actions
-- Module: base_temporary_action
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_actions_actions (
    id bigint PRIMARY KEY,
    is_temporary boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_actions_actions_write_date
    ON odoo_shadow_ir_actions_actions (_odoo_write_date DESC);

-- Model: ir.actions.report
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_actions_report (
    id bigint PRIMARY KEY,
    report_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_actions_report_write_date
    ON odoo_shadow_ir_actions_report (_odoo_write_date DESC);

-- Model: ir.cron
-- Module: base_cron_exclusion
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_cron (
    id bigint PRIMARY KEY,
    email_template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_cron_write_date
    ON odoo_shadow_ir_cron (_odoo_write_date DESC);

-- Model: ir.exports
-- Module: jsonifier
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_exports (
    id bigint PRIMARY KEY,
    global_resolver_id bigint,
    language_agnostic boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_exports_write_date
    ON odoo_shadow_ir_exports (_odoo_write_date DESC);

-- Model: ir.exports.line
-- Module: jsonifier
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_exports_line (
    id bigint PRIMARY KEY,
    active boolean,
    instance_method_name text,
    lang_id bigint,
    resolver_id bigint,
    target text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_exports_line_write_date
    ON odoo_shadow_ir_exports_line (_odoo_write_date DESC);

-- Model: ir.exports.resolver
-- Module: jsonifier
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_exports_resolver (
    id bigint PRIMARY KEY,
    name text,
    python_code text,
    type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_exports_resolver_write_date
    ON odoo_shadow_ir_exports_resolver (_odoo_write_date DESC);

-- Model: ir.model
-- Module: base_force_record_noupdate
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_model (
    id bigint PRIMARY KEY,
    active_custom_tracking boolean,
    add_open_tab_field boolean,
    add_smart_search boolean,
    automatic_custom_tracking boolean,  -- computed, stored
    automatic_custom_tracking_domain text,  -- computed, stored
    force_noupdate boolean,
    name_search_domain text,
    restrict_update boolean,
    rpc_config_edit text,
    smart_search_warning text,  -- computed, stored
    tracked_field_count bigint,  -- computed, stored
    use_smart_name_search boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_model_write_date
    ON odoo_shadow_ir_model (_odoo_write_date DESC);

-- Model: ir.model.fields
-- Module: database_cleanup
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_model_fields (
    id bigint PRIMARY KEY,
    can_have_options boolean,  -- computed, stored
    comodel_id bigint,  -- computed, stored
    custom_tracking boolean,  -- computed, stored
    native_tracking boolean,  -- computed, stored
    trackable boolean,  -- computed, stored
    tracking_domain text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_model_fields_write_date
    ON odoo_shadow_ir_model_fields (_odoo_write_date DESC);

-- Model: ir.model.index.size
-- Module: database_size
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_model_index_size (
    id bigint PRIMARY KEY,
    ir_model_size_id bigint,
    name text,
    size bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_model_index_size_write_date
    ON odoo_shadow_ir_model_index_size (_odoo_write_date DESC);

-- Model: ir.model.relation.size
-- Module: database_size
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_model_relation_size (
    id bigint PRIMARY KEY,
    ir_model_size_id bigint,
    name text,
    size bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_model_relation_size_write_date
    ON odoo_shadow_ir_model_relation_size (_odoo_write_date DESC);

-- Model: ir.model.size
-- Module: database_size
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_model_size (
    id bigint PRIMARY KEY,
    attachment_size bigint,
    indexes_size bigint,  -- computed, stored
    measurement_date date,
    model text,
    model_name text,  -- computed, stored
    relations_size bigint,  -- computed, stored
    table_size bigint,
    total_database_size bigint,  -- computed, stored
    total_model_size bigint,  -- computed, stored
    total_table_size bigint,
    tuples bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_model_size_write_date
    ON odoo_shadow_ir_model_size (_odoo_write_date DESC);

-- Model: ir.module.author
-- Module: module_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_module_author (
    id bigint PRIMARY KEY,
    installed_module_qty bigint,  -- computed, stored
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_module_author_write_date
    ON odoo_shadow_ir_module_author (_odoo_write_date DESC);

-- Model: ir.module.module
-- Module: module_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_module_module (
    id bigint PRIMARY KEY,
    css_code_qty bigint,
    is_oca_module boolean,  -- computed, stored
    is_odoo_module boolean,  -- computed, stored
    js_code_qty bigint,
    module_type_id bigint,
    python_code_qty bigint,
    scss_code_qty bigint,
    xml_code_qty bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_module_module_write_date
    ON odoo_shadow_ir_module_module (_odoo_write_date DESC);

-- Model: ir.module.type
-- Module: module_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_module_type (
    id bigint PRIMARY KEY,
    installed_module_qty bigint,  -- computed, stored
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_module_type_write_date
    ON odoo_shadow_ir_module_type (_odoo_write_date DESC);

-- Model: ir.module.type.rule
-- Module: module_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_module_type_rule (
    id bigint PRIMARY KEY,
    module_domain text,
    module_type_id bigint,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_module_type_rule_write_date
    ON odoo_shadow_ir_module_type_rule (_odoo_write_date DESC);

-- Model: ir.sequence.option
-- Module: base_sequence_option
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_sequence_option (
    id bigint PRIMARY KEY,
    company_id bigint,
    model text,
    name text,
    use_sequence_option boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_sequence_option_write_date
    ON odoo_shadow_ir_sequence_option (_odoo_write_date DESC);

-- Model: ir.sequence.option.line
-- Module: base_sequence_option
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_sequence_option_line (
    id bigint PRIMARY KEY,
    base_id bigint,
    company_id bigint,
    filter_domain text,
    implementation text,
    model text,
    name text,
    prefix text,
    sequence_id bigint,
    suffix text,
    use_sequence_option boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_sequence_option_line_write_date
    ON odoo_shadow_ir_sequence_option_line (_odoo_write_date DESC);

-- Model: ir.ui.view
-- Module: base_view_inheritance_extension
CREATE TABLE IF NOT EXISTS odoo_shadow_ir_ui_view (
    id bigint PRIMARY KEY,
    type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ir_ui_view_write_date
    ON odoo_shadow_ir_ui_view (_odoo_write_date DESC);

-- Model: journal.ledger.report.wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_journal_ledger_report_wizard (
    id bigint PRIMARY KEY,
    date_from date,
    date_range_id bigint,
    date_to date,
    foreign_currency boolean,
    group_option text,
    move_target text,
    sort_option text,
    with_account_name boolean,
    with_auto_sequence boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_journal_ledger_report_wizard_write_date
    ON odoo_shadow_journal_ledger_report_wizard (_odoo_write_date DESC);

-- Model: m2x.create.edit.option
-- Module: web_m2x_options_manager
CREATE TABLE IF NOT EXISTS odoo_shadow_m2x_create_edit_option (
    id bigint PRIMARY KEY,
    comodel_id bigint,
    comodel_name text,
    field_id bigint,
    field_name text,
    model_id bigint,
    model_name text,
    name text,  -- computed, stored
    option_create text,
    option_create_edit text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_m2x_create_edit_option_write_date
    ON odoo_shadow_m2x_create_edit_option (_odoo_write_date DESC);

-- Model: mis.cash_flow.forecast_line
-- Module: mis_builder_cash_flow
CREATE TABLE IF NOT EXISTS odoo_shadow_mis_cash_flow_forecast_line (
    id bigint PRIMARY KEY,
    account_id bigint,
    balance double precision,
    company_id bigint,
    date date,
    name text,
    partner_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_mis_cash_flow_forecast_line_write_date
    ON odoo_shadow_mis_cash_flow_forecast_line (_odoo_write_date DESC);

-- Model: mis.report.instance
-- Module: mis_template_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_mis_report_instance (
    id bigint PRIMARY KEY,
    allow_horizontal boolean,  -- computed, stored
    horizontal boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_mis_report_instance_write_date
    ON odoo_shadow_mis_report_instance (_odoo_write_date DESC);

-- Model: mis.report.kpi
-- Module: mis_template_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_mis_report_kpi (
    id bigint PRIMARY KEY,
    split_after boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_mis_report_kpi_write_date
    ON odoo_shadow_mis_report_kpi (_odoo_write_date DESC);

-- Model: open.items.report.wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_open_items_report_wizard (
    id bigint PRIMARY KEY,
    account_code_from bigint,
    account_code_to bigint,
    date_at date,
    date_from date,
    foreign_currency boolean,
    grouped_by text,
    hide_account_at_0 boolean,
    payable_accounts_only boolean,
    receivable_accounts_only boolean,
    show_partner_details boolean,
    target_move text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_open_items_report_wizard_write_date
    ON odoo_shadow_open_items_report_wizard (_odoo_write_date DESC);

-- Model: ph.holiday
-- Module: ipai_tbwa_finance
CREATE TABLE IF NOT EXISTS odoo_shadow_ph_holiday (
    id bigint PRIMARY KEY,
    company_id bigint,
    date date,
    holiday_type text,
    name text,
    year bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ph_holiday_write_date
    ON odoo_shadow_ph_holiday (_odoo_write_date DESC);

-- Model: ppm.close.task
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_close_task (
    id bigint PRIMARY KEY,
    agency_code text,
    approval_completed_by text,
    approval_completed_date date,
    approval_days double precision,
    approval_due date,
    approver_code text,
    completion_notes text,
    detailed_task text,
    monthly_close_id bigint,
    name text,
    notes text,
    owner_code text,
    prep_completed_by text,
    prep_completed_date date,
    prep_days double precision,
    prep_start date,
    review_completed_by text,
    review_completed_date date,
    review_days double precision,
    review_due date,
    reviewer_code text,
    sequence bigint,
    state text,
    template_id bigint,
    total_days double precision,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_close_task_write_date
    ON odoo_shadow_ppm_close_task (_odoo_write_date DESC);

-- Model: ppm.close.template
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_close_template (
    id bigint PRIMARY KEY,
    active boolean,
    agency_code text,
    approval_days double precision,
    approver_code text,
    detailed_task text,
    name text,  -- computed, stored
    notes text,
    owner_code text,
    prep_days double precision,
    review_days double precision,
    reviewer_code text,
    sequence bigint,
    task_category text,
    total_days double precision,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_close_template_write_date
    ON odoo_shadow_ppm_close_template (_odoo_write_date DESC);

-- Model: ppm.kpi.snapshot
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_kpi_snapshot (
    id bigint PRIMARY KEY,
    as_of timestamptz,
    kpi_category text,
    kpi_key text,
    kpi_label text,
    name text,  -- computed, stored
    portfolio_id bigint,
    program_id bigint,
    project_id bigint,
    scope text,
    source text,
    source_ref text,
    status text,  -- computed, stored
    target_value double precision,
    threshold_green double precision,
    threshold_yellow double precision,
    unit text,
    value double precision,
    value_text text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_kpi_snapshot_write_date
    ON odoo_shadow_ppm_kpi_snapshot (_odoo_write_date DESC);

-- Model: ppm.monthly.close
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_monthly_close (
    id bigint PRIMARY KEY,
    approval_due_date date,  -- computed, stored
    close_month date,
    created_by_cron boolean,
    month_end_date date,  -- computed, stored
    name text,  -- computed, stored
    notes text,
    prep_start_date date,  -- computed, stored
    progress_percentage double precision,  -- computed, stored
    review_due_date date,  -- computed, stored
    state text,
    task_completed bigint,  -- computed, stored
    task_count bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_monthly_close_write_date
    ON odoo_shadow_ppm_monthly_close (_odoo_write_date DESC);

-- Model: ppm.portfolio
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_portfolio (
    id bigint PRIMARY KEY,
    active boolean,
    budget_variance_pct double precision,  -- computed, stored
    code text,
    currency_id bigint,
    date_end date,
    date_start date,
    description text,
    health_score bigint,  -- computed, stored
    health_status text,  -- computed, stored
    name text,
    objective text,
    owner_id bigint,
    program_count bigint,  -- computed, stored
    sequence bigint,
    sponsor_id bigint,
    total_actual numeric(16, 2),  -- computed, stored
    total_budget numeric(16, 2),  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_portfolio_write_date
    ON odoo_shadow_ppm_portfolio (_odoo_write_date DESC);

-- Model: ppm.program
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_program (
    id bigint PRIMARY KEY,
    active boolean,
    actual_cost numeric(16, 2),  -- computed, stored
    budget numeric(16, 2),
    code text,
    currency_id bigint,
    date_end date,
    date_start date,
    description text,
    health_notes text,
    health_score bigint,
    health_status text,
    name text,
    objectives text,
    open_high_risks bigint,  -- computed, stored
    portfolio_id bigint,
    program_manager_id bigint,
    project_count bigint,  -- computed, stored
    risk_count bigint,  -- computed, stored
    sequence bigint,
    sponsor_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_program_write_date
    ON odoo_shadow_ppm_program (_odoo_write_date DESC);

-- Model: ppm.resource.allocation
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_resource_allocation (
    id bigint PRIMARY KEY,
    allocation_pct double precision,
    date_end date,
    date_start date,
    employee_id bigint,
    is_overloaded boolean,  -- computed, stored
    name text,  -- computed, stored
    notes text,
    planned_hours double precision,
    program_id bigint,
    project_id bigint,
    role text,
    status text,
    task_id bigint,
    total_allocation double precision,  -- computed, stored
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_resource_allocation_write_date
    ON odoo_shadow_ppm_resource_allocation (_odoo_write_date DESC);

-- Model: ppm.risk
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_ppm_risk (
    id bigint PRIMARY KEY,
    assigned_to_id bigint,
    category text,
    code text,
    contingency_plan text,
    currency_id bigint,
    date_closed date,
    date_identified date,
    date_target date,
    description text,
    impact text,
    mitigation_plan text,
    mitigation_strategy text,
    name text,
    owner_id bigint,
    portfolio_id bigint,
    potential_cost numeric(16, 2),
    probability text,
    program_id bigint,
    project_id bigint,
    risk_score bigint,  -- computed, stored
    scope text,
    severity text,  -- computed, stored
    status text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_ppm_risk_write_date
    ON odoo_shadow_ppm_risk (_odoo_write_date DESC);

-- Model: product.template
-- Module: sale_project_copy_tasks
CREATE TABLE IF NOT EXISTS odoo_shadow_product_template (
    id bigint PRIMARY KEY,
    recurring_task boolean,
    service_tracking text,
    task_force_month text,
    task_force_month_quarter text,
    task_force_month_semester text,
    task_repeat_interval bigint,
    task_repeat_number bigint,
    task_repeat_type text,
    task_repeat_unit text,
    task_repeat_until date,
    task_start_date_method text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_product_template_write_date
    ON odoo_shadow_product_template (_odoo_write_date DESC);

-- Model: project.assignment
-- Module: project_role
CREATE TABLE IF NOT EXISTS odoo_shadow_project_assignment (
    id bigint PRIMARY KEY,
    active boolean,
    company_id bigint,
    name text,  -- computed, stored
    project_id bigint,
    role_id bigint,
    user_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_assignment_write_date
    ON odoo_shadow_project_assignment (_odoo_write_date DESC);

-- Model: project.milestone
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_project_milestone (
    id bigint PRIMARY KEY,
    alert_days_before bigint,
    approval_date date,
    approval_required boolean,
    approver_id bigint,
    baseline_deadline date,
    completed_task_count bigint,  -- computed, stored
    completion_criteria text,
    dedication bigint,  -- computed, stored
    deliverables text,
    execution bigint,  -- computed, stored
    gate_status text,
    last_alert_sent date,
    milestone_type text,
    risk_level text,
    risk_notes text,
    task_count bigint,  -- computed, stored
    variance_days bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_milestone_write_date
    ON odoo_shadow_project_milestone (_odoo_write_date DESC);

-- Model: project.project
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_project_project (
    id bigint PRIMARY KEY,
    actual_finish date,
    actual_start date,
    baseline_finish date,
    baseline_start date,
    child_ids_count bigint,  -- computed, stored
    clarity_id text,
    critical_milestone_count bigint,  -- computed, stored
    department_id bigint,
    health_status text,
    im_code text,
    inherit_assignments boolean,
    ipai_finance_enabled boolean,
    ipai_im_code text,
    ipai_is_im_project boolean,
    ipai_root_project_id bigint,
    is_program boolean,
    is_template boolean,
    key text,
    limit_role_to_assignments boolean,
    location_dest_id bigint,
    location_id bigint,
    milestone_count bigint,  -- computed, stored
    name text,
    overall_progress double precision,  -- computed, stored
    overall_status text,  -- computed, stored
    parent_id bigint,
    parent_path text,
    phase_count bigint,  -- computed, stored
    picking_type_id bigint,
    portfolio_id bigint,
    program_code text,
    program_type text,
    purchase_count bigint,  -- computed, stored
    purchase_invoice_count bigint,  -- computed, stored
    purchase_invoice_line_total double precision,  -- computed, stored
    purchase_line_total bigint,  -- computed, stored
    sequence_code text,
    stage_last_update_date timestamptz,
    stock_analytic_date date,
    task_key_sequence_id bigint,
    type_id bigint,
    variance_finish bigint,  -- computed, stored
    variance_start bigint,  -- computed, stored
    x_cycle_code text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_project_write_date
    ON odoo_shadow_project_project (_odoo_write_date DESC);

-- Model: project.role
-- Module: project_role
CREATE TABLE IF NOT EXISTS odoo_shadow_project_role (
    id bigint PRIMARY KEY,
    active boolean,
    company_id bigint,
    complete_name text,  -- computed, stored
    description text,
    name text,
    parent_id bigint,
    parent_path text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_role_write_date
    ON odoo_shadow_project_role (_odoo_write_date DESC);

-- Model: project.stakeholder
-- Module: project_stakeholder
CREATE TABLE IF NOT EXISTS odoo_shadow_project_stakeholder (
    id bigint PRIMARY KEY,
    note text,
    partner_id bigint,
    project_id bigint,
    role_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_stakeholder_write_date
    ON odoo_shadow_project_stakeholder (_odoo_write_date DESC);

-- Model: project.stakeholder.role
-- Module: project_stakeholder
CREATE TABLE IF NOT EXISTS odoo_shadow_project_stakeholder_role (
    id bigint PRIMARY KEY,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_stakeholder_role_write_date
    ON odoo_shadow_project_stakeholder_role (_odoo_write_date DESC);

-- Model: project.tags
-- Module: project_tag_hierarchy
CREATE TABLE IF NOT EXISTS odoo_shadow_project_tags (
    id bigint PRIMARY KEY,
    company_id bigint,
    parent_id bigint,
    parent_path text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_tags_write_date
    ON odoo_shadow_project_tags (_odoo_write_date DESC);

-- Model: project.task
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_project_task (
    id bigint PRIMARY KEY,
    activity_type text,
    actual_cost double precision,
    actual_hours double precision,  -- computed, stored
    allow_moves_action_assign boolean,  -- computed, stored
    allow_moves_action_confirm boolean,  -- computed, stored
    ancestor_id bigint,  -- computed, stored
    approval_duration double precision,
    approver_id bigint,
    auto_sync boolean,
    bir_approval_due_date date,
    bir_deadline date,
    bir_form text,
    bir_payment_due_date date,
    bir_period_label text,
    bir_prep_due_date date,
    bir_related boolean,
    bir_schedule_id bigint,
    child_task_count bigint,  -- computed, stored
    closing_due_date date,
    cluster text,
    code text,
    cost_variance double precision,  -- computed, stored
    critical_path boolean,  -- computed, stored
    domain_hr_category_ids bytea,  -- computed, stored
    domain_user_ids bytea,  -- computed, stored
    done_stock_moves boolean,
    earned_value double precision,  -- computed, stored
    erp_ref text,
    fd_id bigint,
    finance_category text,
    finance_code text,
    finance_deadline_type text,
    finance_logframe_id bigint,
    finance_person_id bigint,
    finance_supervisor_id bigint,
    free_float bigint,  -- computed, stored
    gate_approver_id bigint,
    gate_decision text,
    gate_milestone_id bigint,
    group_id bigint,
    has_gate boolean,
    ipai_compliance_step text,
    ipai_days_to_deadline bigint,  -- computed, stored
    ipai_deadline_offset_workdays bigint,
    ipai_owner_code text,
    ipai_owner_role text,
    ipai_status_bucket text,  -- computed, stored
    ipai_task_category text,
    ipai_template_id bigint,
    is_finance_ppm boolean,  -- computed, stored
    is_phase boolean,
    key text,
    lag_days bigint,
    lead_days bigint,
    location_dest_id bigint,
    location_id bigint,
    milestone_count bigint,  -- computed, stored
    notes text,
    owner_code text,
    period_covered text,
    phase_baseline_finish date,
    phase_baseline_start date,
    phase_progress double precision,  -- computed, stored
    phase_status text,
    phase_type text,
    phase_variance_days bigint,  -- computed, stored
    picking_type_id bigint,
    planned_date_end timestamptz,  -- computed, stored
    planned_date_start timestamptz,  -- computed, stored
    planned_hours double precision,
    planned_value double precision,
    portal_url text,  -- computed, stored
    portal_url_visible boolean,  -- computed, stored
    pr_uri text,
    prep_duration double precision,
    priority text,
    project_department_id bigint,
    relative_due text,
    remaining_hours double precision,
    resource_allocation double precision,
    review_duration double precision,
    reviewer_id bigint,
    role_code text,
    schedule_variance double precision,  -- computed, stored
    scrap_count bigint,  -- computed, stored
    sfm_id bigint,
    stage_id bigint,
    stock_analytic_account_id bigint,
    stock_analytic_date date,
    stock_analytic_distribution jsonb,
    stock_moves_is_locked boolean,
    stock_state text,  -- computed, stored
    target_date date,
    total_float bigint,  -- computed, stored
    type_id bigint,
    unreserve_visible boolean,  -- computed, stored
    url text,  -- computed, stored
    use_stock_moves boolean,
    version_id bigint,
    wbs_code text,  -- computed, stored
    x_cycle_key text,
    x_external_key text,
    x_obsolete boolean,
    x_seed_hash text,
    x_step_code text,
    x_task_template_code text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_task_write_date
    ON odoo_shadow_project_task (_odoo_write_date DESC);

-- Model: project.task.checklist.item
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_project_task_checklist_item (
    id bigint PRIMARY KEY,
    actual_hours double precision,
    assigned_user_id bigint,
    blocker_description text,
    completed_date date,
    due_date date,
    estimated_hours double precision,
    notes text,
    priority text,
    status text,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_task_checklist_item_write_date
    ON odoo_shadow_project_task_checklist_item (_odoo_write_date DESC);

-- Model: project.task.description.template
-- Module: project_task_description_template
CREATE TABLE IF NOT EXISTS odoo_shadow_project_task_description_template (
    id bigint PRIMARY KEY,
    active boolean,
    company_id bigint,
    description text,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_task_description_template_write_date
    ON odoo_shadow_project_task_description_template (_odoo_write_date DESC);

-- Model: project.task.merge
-- Module: project_merge
CREATE TABLE IF NOT EXISTS odoo_shadow_project_task_merge (
    id bigint PRIMARY KEY,
    create_new_task boolean,
    dst_project_id bigint,
    dst_task_id bigint,
    dst_task_name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_task_merge_write_date
    ON odoo_shadow_project_task_merge (_odoo_write_date DESC);

-- Model: project.task.stock.product.set.wizard
-- Module: project_task_stock_product_set
CREATE TABLE IF NOT EXISTS odoo_shadow_project_task_stock_product_set_wizard (
    id bigint PRIMARY KEY,
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_task_stock_product_set_wizard_write_date
    ON odoo_shadow_project_task_stock_product_set_wizard (_odoo_write_date DESC);

-- Model: project.task.type
-- Module: project_task_default_stage
CREATE TABLE IF NOT EXISTS odoo_shadow_project_task_type (
    id bigint PRIMARY KEY,
    case_default boolean,
    done_stock_moves boolean,
    task_state text,
    use_stock_moves boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_task_type_write_date
    ON odoo_shadow_project_task_type (_odoo_write_date DESC);

-- Model: project.type
-- Module: project_type
CREATE TABLE IF NOT EXISTS odoo_shadow_project_type (
    id bigint PRIMARY KEY,
    code text,
    complete_name text,  -- computed, stored
    description text,
    name text,
    parent_id bigint,
    project_ok boolean,
    task_ok boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_type_write_date
    ON odoo_shadow_project_type (_odoo_write_date DESC);

-- Model: project.version
-- Module: project_version
CREATE TABLE IF NOT EXISTS odoo_shadow_project_version (
    id bigint PRIMARY KEY,
    name text,
    project_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_project_version_write_date
    ON odoo_shadow_project_version (_odoo_write_date DESC);

-- Model: purchase.order
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_purchase_order (
    id bigint PRIMARY KEY,
    x_master_control_submitted boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_purchase_order_write_date
    ON odoo_shadow_purchase_order (_odoo_write_date DESC);

-- Model: quick.start.screen
-- Module: web_quick_start_screen
CREATE TABLE IF NOT EXISTS odoo_shadow_quick_start_screen (
    id bigint PRIMARY KEY,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_quick_start_screen_write_date
    ON odoo_shadow_quick_start_screen (_odoo_write_date DESC);

-- Model: quick.start.screen.action
-- Module: web_quick_start_screen
CREATE TABLE IF NOT EXISTS odoo_shadow_quick_start_screen_action (
    id bigint PRIMARY KEY,
    action_ref_id jsonb,
    active boolean,
    color bigint,
    context text,
    description text,
    domain text,
    icon_name text,
    image jsonb,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_quick_start_screen_action_write_date
    ON odoo_shadow_quick_start_screen_action (_odoo_write_date DESC);

-- Model: report.project.task.user
-- Module: project_task_ancestor
CREATE TABLE IF NOT EXISTS odoo_shadow_report_project_task_user (
    id bigint PRIMARY KEY,
    ancestor_id bigint,
    planned_date_end timestamptz,
    planned_date_start timestamptz,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_report_project_task_user_write_date
    ON odoo_shadow_report_project_task_user (_odoo_write_date DESC);

-- Model: report.xlsx.wizard
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_report_xlsx_wizard (
    id bigint PRIMARY KEY,
    domain text,
    res_model text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_report_xlsx_wizard_write_date
    ON odoo_shadow_report_xlsx_wizard (_odoo_write_date DESC);

-- Model: res.company
-- Module: account_reconcile_oca
CREATE TABLE IF NOT EXISTS odoo_shadow_res_company (
    id bigint PRIMARY KEY,
    account_auto_reconcile_queue boolean,
    color_button_bg text,
    color_button_bg_hover text,
    color_button_text text,
    color_link_text text,
    color_link_text_hover text,
    color_navbar_bg text,
    color_navbar_bg_hover text,
    color_navbar_text text,
    color_submenu_text text,
    company_colors jsonb,
    favicon bytea,
    project_inherit_assignments boolean,
    project_limit_role_to_assignments boolean,
    reconcile_aggregate text,
    scss_modif_timestamp text,
    user_tech_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_res_company_write_date
    ON odoo_shadow_res_company (_odoo_write_date DESC);

-- Model: res.config.settings
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_res_config_settings (
    id bigint PRIMARY KEY,
    account_auto_reconcile_queue boolean,
    age_partner_config_id bigint,
    database_size_purge boolean,
    database_size_retention_daily bigint,
    database_size_retention_monthly bigint,
    default_aging_type text,
    default_filter_negative_balances boolean,
    default_filter_partners_non_due boolean,
    default_show_aging_buckets boolean,
    excluded_models_from_readonly text,
    group_activity_statement boolean,
    group_outstanding_statement boolean,
    ipai_copilot_api_key text,
    ipai_copilot_api_url text,
    ipai_enable_finance_project_analytics boolean,
    project_display_name_pattern text,
    project_inherit_assignments boolean,
    project_limit_role_to_assignments boolean,
    pwa_background_color text,
    pwa_icon bytea,
    pwa_short_name text,
    pwa_theme_color text,
    reconcile_aggregate text,
    session_auto_close_timeout bigint,
    superset_auto_sync boolean,
    superset_connection_id bigint,
    superset_create_analytics_views boolean,
    superset_enable_rls boolean,
    superset_sync_interval text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_res_config_settings_write_date
    ON odoo_shadow_res_config_settings (_odoo_write_date DESC);

-- Model: res.partner
-- Module: account_move_base_import
CREATE TABLE IF NOT EXISTS odoo_shadow_res_partner (
    id bigint PRIMARY KEY,
    bank_statement_label text,
    bir_registered boolean,
    bir_registration_date date,
    srm_overall_score double precision,
    srm_supplier_id bigint,
    srm_tier text,
    tax_type text,
    tin text,
    tin_branch_code text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_res_partner_write_date
    ON odoo_shadow_res_partner (_odoo_write_date DESC);

-- Model: res.remote
-- Module: base_remote
CREATE TABLE IF NOT EXISTS odoo_shadow_res_remote (
    id bigint PRIMARY KEY,
    in_network boolean,
    ip text,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_res_remote_write_date
    ON odoo_shadow_res_remote (_odoo_write_date DESC);

-- Model: res.users
-- Module: base_model_restrict_update
CREATE TABLE IF NOT EXISTS odoo_shadow_res_users (
    id bigint PRIMARY KEY,
    apps_menu_search_type text,
    apps_menu_theme text,
    chatter_position text,
    is_readonly_user boolean,
    is_redirect_home boolean,  -- computed, stored
    notify_danger_channel_name text,  -- computed, stored
    notify_default_channel_name text,  -- computed, stored
    notify_info_channel_name text,  -- computed, stored
    notify_success_channel_name text,  -- computed, stored
    notify_warning_channel_name text,  -- computed, stored
    quick_start_screen_id bigint,
    x_employee_code text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_res_users_write_date
    ON odoo_shadow_res_users (_odoo_write_date DESC);

-- Model: sale.order
-- Module: base_transaction_id
CREATE TABLE IF NOT EXISTS odoo_shadow_sale_order (
    id bigint PRIMARY KEY,
    has_project_service_tracking_lines boolean,  -- computed, stored
    transaction_id text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_sale_order_write_date
    ON odoo_shadow_sale_order (_odoo_write_date DESC);

-- Model: sale.order.line
-- Module: sale_project_copy_tasks
CREATE TABLE IF NOT EXISTS odoo_shadow_sale_order_line (
    id bigint PRIMARY KEY,
    is_project_service_tracking_line boolean,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_sale_order_line_write_date
    ON odoo_shadow_sale_order_line (_odoo_write_date DESC);

-- Model: srm.kpi.category
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_srm_kpi_category (
    id bigint PRIMARY KEY,
    active boolean,
    code text,
    compute_source text,
    description text,
    eval_method text,
    name text,
    sequence bigint,
    weight double precision,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_srm_kpi_category_write_date
    ON odoo_shadow_srm_kpi_category (_odoo_write_date DESC);

-- Model: srm.qualification
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_srm_qualification (
    id bigint PRIMARY KEY,
    approval_date timestamptz,
    approver_id bigint,
    checklist_complete boolean,  -- computed, stored
    completion_date date,
    expiry_date date,
    name text,  -- computed, stored
    notes text,
    qualification_type text,
    rejection_reason text,
    reviewer_id bigint,
    risk_notes text,
    risk_score double precision,
    start_date date,
    state text,
    supplier_id bigint,
    target_completion date,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_srm_qualification_write_date
    ON odoo_shadow_srm_qualification (_odoo_write_date DESC);

-- Model: srm.qualification.checklist
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_srm_qualification_checklist (
    id bigint PRIMARY KEY,
    completed_by bigint,
    completed_date date,
    description text,
    is_complete boolean,
    is_required boolean,
    name text,
    notes text,
    qualification_id bigint,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_srm_qualification_checklist_write_date
    ON odoo_shadow_srm_qualification_checklist (_odoo_write_date DESC);

-- Model: srm.scorecard
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_srm_scorecard (
    id bigint PRIMARY KEY,
    action_items text,
    as_of date,
    comments text,
    evaluator_id bigint,
    grade text,  -- computed, stored
    name text,  -- computed, stored
    overall_score double precision,  -- computed, stored
    period text,
    state text,
    supplier_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_srm_scorecard_write_date
    ON odoo_shadow_srm_scorecard (_odoo_write_date DESC);

-- Model: srm.scorecard.line
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_srm_scorecard_line (
    id bigint PRIMARY KEY,
    evidence text,
    kpi_category_id bigint,
    notes text,
    score double precision,
    scorecard_id bigint,
    sequence bigint,
    weight double precision,
    weighted_score double precision,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_srm_scorecard_line_write_date
    ON odoo_shadow_srm_scorecard_line (_odoo_write_date DESC);

-- Model: srm.supplier
-- Module: ipai
CREATE TABLE IF NOT EXISTS odoo_shadow_srm_supplier (
    id bigint PRIMARY KEY,
    code text,
    compliance_docs_complete boolean,
    currency_id bigint,
    is_qualified boolean,  -- computed, stored
    last_audit_date date,
    latest_scorecard_id bigint,  -- computed, stored
    name text,
    next_audit_date date,
    open_po_count bigint,  -- computed, stored
    overall_score double precision,  -- computed, stored
    partner_id bigint,
    primary_contact_id bigint,
    qualification_expiry date,
    risk_level text,
    risk_notes text,
    sales_contact_id bigint,
    state text,
    tier text,
    total_po_count bigint,  -- computed, stored
    ytd_spend numeric(16, 2),  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_srm_supplier_write_date
    ON odoo_shadow_srm_supplier (_odoo_write_date DESC);

-- Model: statement.common.wizard
-- Module: partner_statement
CREATE TABLE IF NOT EXISTS odoo_shadow_statement_common_wizard (
    id bigint PRIMARY KEY,
    account_type text,
    aging_type text,
    company_id bigint,
    date_end date,
    excluded_accounts_selector text,
    filter_negative_balances boolean,
    filter_partners_non_due boolean,
    name text,
    number_partner_ids bigint,
    show_aging_buckets boolean,
    show_only_overdue boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_statement_common_wizard_write_date
    ON odoo_shadow_statement_common_wizard (_odoo_write_date DESC);

-- Model: stock.move
-- Module: project_task_stock
CREATE TABLE IF NOT EXISTS odoo_shadow_stock_move (
    id bigint PRIMARY KEY,
    raw_material_task_id bigint,
    show_cancel_button_in_task boolean,  -- computed, stored
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_stock_move_write_date
    ON odoo_shadow_stock_move (_odoo_write_date DESC);

-- Model: stock.move.line
-- Module: project_task_stock
CREATE TABLE IF NOT EXISTS odoo_shadow_stock_move_line (
    id bigint PRIMARY KEY,
    task_id bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_stock_move_line_write_date
    ON odoo_shadow_stock_move_line (_odoo_write_date DESC);

-- Model: stock.scrap
-- Module: project_task_stock
CREATE TABLE IF NOT EXISTS odoo_shadow_stock_scrap (
    id bigint PRIMARY KEY,
    task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_stock_scrap_write_date
    ON odoo_shadow_stock_scrap (_odoo_write_date DESC);

-- Model: superset.analytics.view
-- Module: ipai_superset_connector
CREATE TABLE IF NOT EXISTS odoo_shadow_superset_analytics_view (
    id bigint PRIMARY KEY,
    active boolean,
    category text,
    description text,
    is_created boolean,
    last_refresh timestamptz,
    name text,
    required_modules text,
    sequence bigint,
    sql_definition text,
    technical_name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_superset_analytics_view_write_date
    ON odoo_shadow_superset_analytics_view (_odoo_write_date DESC);

-- Model: superset.bulk.dataset.wizard
-- Module: ipai_superset_connector
CREATE TABLE IF NOT EXISTS odoo_shadow_superset_bulk_dataset_wizard (
    id bigint PRIMARY KEY,
    connection_id bigint,
    create_analytics_views boolean,
    preset text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_superset_bulk_dataset_wizard_write_date
    ON odoo_shadow_superset_bulk_dataset_wizard (_odoo_write_date DESC);

-- Model: superset.connection
-- Module: ipai_superset_connector
CREATE TABLE IF NOT EXISTS odoo_shadow_superset_connection (
    id bigint PRIMARY KEY,
    access_token text,
    active boolean,
    api_key text,
    auth_method text,
    base_url text,
    csrf_token text,
    dataset_count bigint,  -- computed, stored
    db_connection_id bigint,
    db_connection_name text,
    last_error text,
    last_sync timestamptz,
    name text,
    password text,
    pg_database text,
    pg_host text,
    pg_password text,
    pg_port bigint,
    pg_schema text,
    pg_username text,
    refresh_token text,
    state text,
    token_expiry timestamptz,
    use_ssl boolean,
    username text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_superset_connection_write_date
    ON odoo_shadow_superset_connection (_odoo_write_date DESC);

-- Model: superset.dataset
-- Module: ipai_superset_connector
CREATE TABLE IF NOT EXISTS odoo_shadow_superset_dataset (
    id bigint PRIMARY KEY,
    active boolean,
    category text,
    column_count bigint,  -- computed, stored
    connection_id bigint,
    custom_sql text,
    description text,
    enable_rls boolean,
    include_all_fields boolean,
    last_sync timestamptz,
    model_id bigint,
    model_name text,
    name text,
    rls_filter_column text,
    sequence bigint,
    source_type text,
    superset_dataset_id bigint,
    sync_error text,
    sync_status text,
    technical_name text,
    view_created boolean,
    view_name text,  -- computed, stored
    view_sql text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_superset_dataset_write_date
    ON odoo_shadow_superset_dataset (_odoo_write_date DESC);

-- Model: superset.dataset.column
-- Module: ipai_superset_connector
CREATE TABLE IF NOT EXISTS odoo_shadow_superset_dataset_column (
    id bigint PRIMARY KEY,
    aggregation text,
    column_type text,
    data_type text,
    dataset_id bigint,
    description text,
    filterable boolean,
    format_string text,
    groupable boolean,
    label text,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_superset_dataset_column_write_date
    ON odoo_shadow_superset_dataset_column (_odoo_write_date DESC);

-- Model: superset.dataset.wizard
-- Module: ipai_superset_connector
CREATE TABLE IF NOT EXISTS odoo_shadow_superset_dataset_wizard (
    id bigint PRIMARY KEY,
    category text,
    connection_id bigint,
    create_view boolean,
    enable_rls boolean,
    include_all_fields boolean,
    model_id bigint,
    name text,
    sync_to_superset boolean,
    technical_name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_superset_dataset_wizard_write_date
    ON odoo_shadow_superset_dataset_wizard (_odoo_write_date DESC);

-- Model: test.partner.time.window
-- Module: test_base_time_window
CREATE TABLE IF NOT EXISTS odoo_shadow_test_partner_time_window (
    id bigint PRIMARY KEY,
    partner_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_test_partner_time_window_write_date
    ON odoo_shadow_test_partner_time_window (_odoo_write_date DESC);

-- Model: test.time.window.model
-- Module: base_time_window
CREATE TABLE IF NOT EXISTS odoo_shadow_test_time_window_model (
    id bigint PRIMARY KEY,
    partner_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_test_time_window_model_write_date
    ON odoo_shadow_test_time_window_model (_odoo_write_date DESC);

-- Model: time.weekday
-- Module: base_time_window
CREATE TABLE IF NOT EXISTS odoo_shadow_time_weekday (
    id bigint PRIMARY KEY,
    name text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_time_weekday_write_date
    ON odoo_shadow_time_weekday (_odoo_write_date DESC);

-- Model: time.window.mixin
-- Module: base_time_window
CREATE TABLE IF NOT EXISTS odoo_shadow_time_window_mixin (
    id bigint PRIMARY KEY,
    time_window_end double precision,
    time_window_start double precision,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_time_window_mixin_write_date
    ON odoo_shadow_time_window_mixin (_odoo_write_date DESC);

-- Model: timesheets.analysis.report
-- Module: project_task_ancestor
CREATE TABLE IF NOT EXISTS odoo_shadow_timesheets_analysis_report (
    id bigint PRIMARY KEY,
    ancestor_task_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_timesheets_analysis_report_write_date
    ON odoo_shadow_timesheets_analysis_report (_odoo_write_date DESC);

-- Model: trgm.index
-- Module: base_search_fuzzy
CREATE TABLE IF NOT EXISTS odoo_shadow_trgm_index (
    id bigint PRIMARY KEY,
    field_id bigint,
    index_name text,
    index_type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_trgm_index_write_date
    ON odoo_shadow_trgm_index (_odoo_write_date DESC);

-- Model: trial.balance.report.wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_trial_balance_report_wizard (
    id bigint PRIMARY KEY,
    account_code_from bigint,
    account_code_to bigint,
    date_from date,
    date_range_id bigint,
    date_to date,
    foreign_currency boolean,
    fy_start_date date,  -- computed, stored
    grouped_by text,
    hide_account_at_0 boolean,
    hide_parent_hierarchy_level boolean,
    limit_hierarchy_level boolean,
    only_one_unaffected_earnings_account boolean,
    payable_accounts_only boolean,
    receivable_accounts_only boolean,
    show_hierarchy boolean,
    show_hierarchy_level bigint,
    show_partner_details boolean,
    target_move text,
    unaffected_earnings_account bigint,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_trial_balance_report_wizard_write_date
    ON odoo_shadow_trial_balance_report_wizard (_odoo_write_date DESC);

-- Model: upgrade.analysis
-- Module: upgrade_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_upgrade_analysis (
    id bigint PRIMARY KEY,
    analysis_date timestamptz,
    config_id bigint,
    log text,
    state text,
    upgrade_path text,  -- computed, stored
    write_files boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_upgrade_analysis_write_date
    ON odoo_shadow_upgrade_analysis (_odoo_write_date DESC);

-- Model: upgrade.attribute
-- Module: upgrade_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_upgrade_attribute (
    id bigint PRIMARY KEY,
    name text,
    record_id bigint,
    value text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_upgrade_attribute_write_date
    ON odoo_shadow_upgrade_attribute (_odoo_write_date DESC);

-- Model: upgrade.comparison.config
-- Module: upgrade_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_upgrade_comparison_config (
    id bigint PRIMARY KEY,
    analysis_qty bigint,  -- computed, stored
    database text,
    name text,
    password text,
    port bigint,
    server text,
    username text,
    version text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_upgrade_comparison_config_write_date
    ON odoo_shadow_upgrade_comparison_config (_odoo_write_date DESC);

-- Model: upgrade.generate.record.wizard
-- Module: upgrade_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_upgrade_generate_record_wizard (
    id bigint PRIMARY KEY,
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_upgrade_generate_record_wizard_write_date
    ON odoo_shadow_upgrade_generate_record_wizard (_odoo_write_date DESC);

-- Model: upgrade.install.wizard
-- Module: upgrade_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_upgrade_install_wizard (
    id bigint PRIMARY KEY,
    module_qty bigint,  -- computed, stored
    state text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_upgrade_install_wizard_write_date
    ON odoo_shadow_upgrade_install_wizard (_odoo_write_date DESC);

-- Model: upgrade.record
-- Module: upgrade_analysis
CREATE TABLE IF NOT EXISTS odoo_shadow_upgrade_record (
    id bigint PRIMARY KEY,
    definition text,
    domain text,
    field text,
    mode text,
    model text,
    model_original_module text,  -- computed, stored
    model_type text,  -- computed, stored
    module text,
    name text,
    noupdate boolean,
    prefix text,  -- computed, stored
    suffix text,  -- computed, stored
    type text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_upgrade_record_write_date
    ON odoo_shadow_upgrade_record (_odoo_write_date DESC);

-- Model: vacuum.rule
-- Module: autovacuum_message_attachment
CREATE TABLE IF NOT EXISTS odoo_shadow_vacuum_rule (
    id bigint PRIMARY KEY,
    active boolean,
    company_id bigint,
    description text,
    empty_model boolean,
    empty_subtype boolean,
    filename_pattern text,
    inheriting_model text,
    message_type text,
    model text,  -- computed, stored
    model_filter_domain text,
    model_id bigint,  -- computed, stored
    name text,
    retention_time bigint,
    ttype text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_vacuum_rule_write_date
    ON odoo_shadow_vacuum_rule (_odoo_write_date DESC);

-- Model: vat.report.wizard
-- Module: account_financial_report
CREATE TABLE IF NOT EXISTS odoo_shadow_vat_report_wizard (
    id bigint PRIMARY KEY,
    based_on text,
    date_from date,
    date_range_id bigint,
    date_to date,
    target_move text,
    tax_detail boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_vat_report_wizard_write_date
    ON odoo_shadow_vat_report_wizard (_odoo_write_date DESC);

-- Model: web.editor.class
-- Module: web_editor_class_selector
CREATE TABLE IF NOT EXISTS odoo_shadow_web_editor_class (
    id bigint PRIMARY KEY,
    active boolean,
    class_name text,
    name text,
    sequence bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_web_editor_class_write_date
    ON odoo_shadow_web_editor_class (_odoo_write_date DESC);

-- Model: web.form.banner.rule
-- Module: web_form_banner
CREATE TABLE IF NOT EXISTS odoo_shadow_web_form_banner_rule (
    id bigint PRIMARY KEY,
    active boolean,
    message text,
    message_is_html boolean,
    message_value_code text,
    model_id bigint,
    model_name text,
    name text,
    position text,
    sequence bigint,
    severity text,
    target_xpath text,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_web_form_banner_rule_write_date
    ON odoo_shadow_web_form_banner_rule (_odoo_write_date DESC);

-- Model: wizard.open.tax.balances
-- Module: account_tax_balance
CREATE TABLE IF NOT EXISTS odoo_shadow_wizard_open_tax_balances (
    id bigint PRIMARY KEY,
    date_range_id bigint,
    from_date date,  -- computed, stored
    target_move text,
    to_date date,  -- computed, stored
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_wizard_open_tax_balances_write_date
    ON odoo_shadow_wizard_open_tax_balances (_odoo_write_date DESC);

-- Model: xlsx.report
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_xlsx_report (
    id bigint PRIMARY KEY,
    choose_template boolean,
    data bytea,
    name text,
    state text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_xlsx_report_write_date
    ON odoo_shadow_xlsx_report (_odoo_write_date DESC);

-- Model: xlsx.template
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_xlsx_template (
    id bigint PRIMARY KEY,
    csv_delimiter text,
    csv_extension text,
    csv_quote boolean,
    datas bytea,
    description text,
    export_action_id bigint,
    fname text,
    gname text,
    import_action_id bigint,
    input_instruction text,
    instruction text,  -- computed, stored
    name text,
    post_import_hook text,
    redirect_action bigint,
    report_action_id bigint,
    report_menu_id bigint,
    res_model text,
    result_field text,  -- computed, stored
    result_model_id bigint,
    show_instruction boolean,
    to_csv boolean,
    use_report_wizard boolean,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_xlsx_template_write_date
    ON odoo_shadow_xlsx_template (_odoo_write_date DESC);

-- Model: xlsx.template.export
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_xlsx_template_export (
    id bigint PRIMARY KEY,
    excel_cell text,
    field_cond text,
    field_name text,
    is_cont boolean,
    is_extend boolean,
    is_sum boolean,
    row_field text,
    section_type text,
    sequence bigint,
    sheet text,
    style text,
    style_cond text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_xlsx_template_export_write_date
    ON odoo_shadow_xlsx_template_export (_odoo_write_date DESC);

-- Model: xlsx.template.import
-- Module: excel_import_export
CREATE TABLE IF NOT EXISTS odoo_shadow_xlsx_template_import (
    id bigint PRIMARY KEY,
    excel_cell text,
    field_cond text,
    field_name text,
    no_delete boolean,
    row_field text,
    section_type text,
    sequence bigint,
    sheet text,
    template_id bigint,
    -- Shadow tracking columns
    _odoo_write_date timestamptz,
    _synced_at timestamptz DEFAULT now(),
    _sync_hash text
);
CREATE INDEX IF NOT EXISTS idx_odoo_shadow_xlsx_template_import_write_date
    ON odoo_shadow_xlsx_template_import (_odoo_write_date DESC);

-- =============================================================================
-- Populate Shadow Metadata
-- =============================================================================

INSERT INTO odoo_shadow_meta (table_name, odoo_model, odoo_module, field_count)
VALUES
    ('odoo_shadow_a1_check', 'a1.check', 'ipai', 11),
    ('odoo_shadow_a1_check_result', 'a1.check.result', 'ipai', 7),
    ('odoo_shadow_a1_export_run', 'a1.export.run', 'ipai', 11),
    ('odoo_shadow_a1_role', 'a1.role', 'ipai', 8),
    ('odoo_shadow_a1_task', 'a1.task', 'ipai', 26),
    ('odoo_shadow_a1_task_checklist', 'a1.task.checklist', 'ipai', 12),
    ('odoo_shadow_a1_tasklist', 'a1.tasklist', 'ipai', 12),
    ('odoo_shadow_a1_template', 'a1.template', 'ipai', 16),
    ('odoo_shadow_a1_template_checklist', 'a1.template.checklist', 'ipai', 7),
    ('odoo_shadow_a1_template_step', 'a1.template.step', 'ipai', 7),
    ('odoo_shadow_a1_workstream', 'a1.workstream', 'ipai', 11),
    ('odoo_shadow_account_account', 'account.account', 'account_financial_report', 2),
    ('odoo_shadow_account_account_reconcile_data', 'account.account.reconcile.data', 'account_reconcile_oca', 3),
    ('odoo_shadow_account_age_report_configuration', 'account.age.report.configuration', 'account_financial_report', 2),
    ('odoo_shadow_account_age_report_configuration_line', 'account.age.report.configuration.line', 'account_financial_report', 3),
    ('odoo_shadow_account_analytic_line', 'account.analytic.line', 'project_task_ancestor', 6),
    ('odoo_shadow_account_bank_statement_line', 'account.bank.statement.line', 'account_reconcile_analytic_tag', 7),
    ('odoo_shadow_account_group', 'account.group', 'account_financial_report', 3),
    ('odoo_shadow_account_journal', 'account.journal', 'account_move_base_import', 15),
    ('odoo_shadow_account_move', 'account.move', 'account_in_payment', 8),
    ('odoo_shadow_account_move_completion_rule', 'account.move.completion.rule', 'account_move_base_import', 3),
    ('odoo_shadow_account_move_line', 'account.move.line', 'account_financial_report', 1),
    ('odoo_shadow_account_reconcile_abstract', 'account.reconcile.abstract', 'account_reconcile_analytic_tag', 5),
    ('odoo_shadow_account_reconcile_model', 'account.reconcile.model', 'account_reconcile_model_oca', 1),
    ('odoo_shadow_account_tax', 'account.tax', 'account_tax_balance', 7),
    ('odoo_shadow_account_financial_report_abstract_wizard', 'account_financial_report_abstract_wizard', 'account_financial_report', 2),
    ('odoo_shadow_activity_statement_wizard', 'activity.statement.wizard', 'partner_statement', 1),
    ('odoo_shadow_advisor_category', 'advisor.category', 'ipai', 11),
    ('odoo_shadow_advisor_playbook', 'advisor.playbook', 'ipai', 9),
    ('odoo_shadow_advisor_recommendation', 'advisor.recommendation', 'ipai', 22),
    ('odoo_shadow_advisor_score', 'advisor.score', 'ipai', 9),
    ('odoo_shadow_advisor_tag', 'advisor.tag', 'ipai', 2),
    ('odoo_shadow_aged_partner_balance_report_wizard', 'aged.partner.balance.report.wizard', 'account_financial_report', 9),
    ('odoo_shadow_attachment_queue', 'attachment.queue', 'attachment_queue', 9),
    ('odoo_shadow_attachment_synchronize_task', 'attachment.synchronize.task', 'attachment_synchronize', 15),
    ('odoo_shadow_auditlog_http_request', 'auditlog.http.request', 'auditlog', 6),
    ('odoo_shadow_auditlog_http_session', 'auditlog.http.session', 'auditlog', 3),
    ('odoo_shadow_auditlog_log', 'auditlog.log', 'auditlog', 11),
    ('odoo_shadow_auditlog_log_line', 'auditlog.log.line', 'auditlog', 8),
    ('odoo_shadow_auditlog_rule', 'auditlog.rule', 'auditlog', 13),
    ('odoo_shadow_base', 'base', 'autovacuum_message_attachment', 1),
    ('odoo_shadow_base_exception', 'base.exception', 'base_exception', 3),
    ('odoo_shadow_base_exception_test_purchase', 'base.exception.test.purchase', 'base_exception', 6),
    ('odoo_shadow_base_exception_test_purchase_line', 'base.exception.test.purchase.line', 'base_exception', 4),
    ('odoo_shadow_base_sequence_tester', 'base.sequence.tester', 'base_sequence_option', 2),
    ('odoo_shadow_bir_alphalist', 'bir.alphalist', 'ipai_bir_tax_compliance', 8),
    ('odoo_shadow_bir_alphalist_line', 'bir.alphalist.line', 'ipai_bir_tax_compliance', 7),
    ('odoo_shadow_bir_filing_deadline', 'bir.filing.deadline', 'ipai_bir_tax_compliance', 9),
    ('odoo_shadow_bir_return', 'bir.return', 'ipai_tbwa_finance', 28),
    ('odoo_shadow_bir_return_line', 'bir.return.line', 'ipai_tbwa_finance', 9),
    ('odoo_shadow_bir_tax_return', 'bir.tax.return', 'ipai_bir_tax_compliance', 25),
    ('odoo_shadow_bir_tax_return_line', 'bir.tax.return.line', 'ipai_bir_tax_compliance', 10),
    ('odoo_shadow_bir_vat_line', 'bir.vat.line', 'ipai_bir_tax_compliance', 10),
    ('odoo_shadow_bir_vat_return', 'bir.vat.return', 'ipai_bir_tax_compliance', 12),
    ('odoo_shadow_bir_withholding_line', 'bir.withholding.line', 'ipai_bir_tax_compliance', 10),
    ('odoo_shadow_bir_withholding_return', 'bir.withholding.return', 'ipai_bir_tax_compliance', 8),
    ('odoo_shadow_cleanup_create_indexes_line', 'cleanup.create_indexes.line', 'database_cleanup', 3),
    ('odoo_shadow_cleanup_purge_line', 'cleanup.purge.line', 'database_cleanup', 3),
    ('odoo_shadow_cleanup_purge_line_column', 'cleanup.purge.line.column', 'database_cleanup', 2),
    ('odoo_shadow_cleanup_purge_line_data', 'cleanup.purge.line.data', 'database_cleanup', 2),
    ('odoo_shadow_cleanup_purge_line_field', 'cleanup.purge.line.field', 'database_cleanup', 4),
    ('odoo_shadow_cleanup_purge_line_menu', 'cleanup.purge.line.menu', 'database_cleanup', 2),
    ('odoo_shadow_cleanup_purge_line_model', 'cleanup.purge.line.model', 'database_cleanup', 1),
    ('odoo_shadow_cleanup_purge_line_module', 'cleanup.purge.line.module', 'database_cleanup', 1),
    ('odoo_shadow_cleanup_purge_line_table', 'cleanup.purge.line.table', 'database_cleanup', 2),
    ('odoo_shadow_close_approval_gate', 'close.approval.gate', 'ipai', 14),
    ('odoo_shadow_close_approval_gate_template', 'close.approval.gate.template', 'ipai', 9),
    ('odoo_shadow_close_cycle', 'close.cycle', 'ipai', 15),
    ('odoo_shadow_close_exception', 'close.exception', 'ipai', 17),
    ('odoo_shadow_close_task', 'close.task', 'ipai', 24),
    ('odoo_shadow_close_task_category', 'close.task.category', 'ipai', 8),
    ('odoo_shadow_close_task_checklist', 'close.task.checklist', 'ipai', 9),
    ('odoo_shadow_close_task_template', 'close.task.template', 'ipai', 20),
    ('odoo_shadow_close_task_template_checklist', 'close.task.template.checklist', 'ipai', 6),
    ('odoo_shadow_closing_period', 'closing.period', 'ipai_tbwa_finance', 14),
    ('odoo_shadow_compliance_check', 'compliance.check', 'ipai_tbwa_finance', 12),
    ('odoo_shadow_credit_statement_import', 'credit.statement.import', 'account_move_base_import', 6),
    ('odoo_shadow_crm_lead', 'crm.lead', 'ipai_crm_pipeline', 6),
    ('odoo_shadow_crm_stage', 'crm.stage', 'ipai_crm_pipeline', 5),
    ('odoo_shadow_db_backup', 'db.backup', 'auto_backup', 10),
    ('odoo_shadow_detailed_activity_statement_wizard', 'detailed.activity.statement.wizard', 'partner_statement', 2),
    ('odoo_shadow_discuss_channel', 'discuss.channel', 'ipai_ask_ai', 1),
    ('odoo_shadow_exception_rule', 'exception.rule', 'base_exception', 10),
    ('odoo_shadow_exception_rule_confirm', 'exception.rule.confirm', 'base_exception', 2),
    ('odoo_shadow_exception_rule_confirm_test_purchase', 'exception.rule.confirm.test.purchase', 'base_exception', 1),
    ('odoo_shadow_export_xlsx_wizard', 'export.xlsx.wizard', 'excel_import_export', 6),
    ('odoo_shadow_fetchmail_attach_mail_manually', 'fetchmail.attach.mail.manually', 'fetchmail_attach_from_folder', 2),
    ('odoo_shadow_fetchmail_attach_mail_manually_mail', 'fetchmail.attach.mail.manually.mail', 'fetchmail_attach_from_folder', 7),
    ('odoo_shadow_fetchmail_server', 'fetchmail.server', 'fetchmail_attach_from_folder', 8),
    ('odoo_shadow_fetchmail_server_folder', 'fetchmail.server.folder', 'fetchmail_attach_from_folder', 18),
    ('odoo_shadow_finance_bir_deadline', 'finance.bir.deadline', 'ipai', 14),
    ('odoo_shadow_finance_ppm_bir_calendar', 'finance.ppm.bir.calendar', 'ipai', 6),
    ('odoo_shadow_finance_ppm_dashboard', 'finance.ppm.dashboard', 'ipai', 10),
    ('odoo_shadow_finance_ppm_import_wizard', 'finance.ppm.import.wizard', 'ipai', 13),
    ('odoo_shadow_finance_ppm_logframe', 'finance.ppm.logframe', 'ipai', 11),
    ('odoo_shadow_finance_ppm_ph_holiday', 'finance.ppm.ph.holiday', 'ipai', 5),
    ('odoo_shadow_finance_ppm_tdi_audit', 'finance.ppm.tdi.audit', 'ipai', 15),
    ('odoo_shadow_finance_task', 'finance.task', 'ipai_tbwa_finance', 31),
    ('odoo_shadow_finance_task_template', 'finance.task.template', 'ipai_tbwa_finance', 18),
    ('odoo_shadow_fs_storage', 'fs.storage', 'attachment_synchronize', 2),
    ('odoo_shadow_general_ledger_report_wizard', 'general.ledger.report.wizard', 'account_financial_report', 17),
    ('odoo_shadow_hr_employee', 'hr.employee', 'ipai', 2),
    ('odoo_shadow_hr_expense', 'hr.expense', 'ipai', 4),
    ('odoo_shadow_hr_timesheet_switch', 'hr.timesheet.switch', 'project_timesheet_time_control', 10),
    ('odoo_shadow_hr_timesheet_time_control_mixin', 'hr.timesheet.time_control.mixin', 'project_timesheet_time_control', 1),
    ('odoo_shadow_iap_account', 'iap.account', 'iap_alternative_provider', 1),
    ('odoo_shadow_import_xlsx_wizard', 'import.xlsx.wizard', 'excel_import_export', 8),
    ('odoo_shadow_ipai_agent_knowledge_source', 'ipai.agent.knowledge_source', 'ipai', 9),
    ('odoo_shadow_ipai_agent_run', 'ipai.agent.run', 'ipai', 14),
    ('odoo_shadow_ipai_agent_skill', 'ipai.agent.skill', 'ipai', 9),
    ('odoo_shadow_ipai_agent_tool', 'ipai.agent.tool', 'ipai', 9),
    ('odoo_shadow_ipai_ai_studio_run', 'ipai.ai_studio.run', 'ipai', 9),
    ('odoo_shadow_ipai_approval_mixin', 'ipai.approval.mixin', 'ipai_platform_approvals', 5),
    ('odoo_shadow_ipai_ask_ai_chatter_request', 'ipai.ask_ai_chatter.request', 'ipai_ask_ai_chatter', 11),
    ('odoo_shadow_ipai_asset', 'ipai.asset', 'ipai', 14),
    ('odoo_shadow_ipai_asset_category', 'ipai.asset.category', 'ipai', 8),
    ('odoo_shadow_ipai_asset_checkout', 'ipai.asset.checkout', 'ipai', 12),
    ('odoo_shadow_ipai_asset_reservation', 'ipai.asset.reservation', 'ipai', 7),
    ('odoo_shadow_ipai_audit_log', 'ipai.audit.log', 'ipai_platform_audit', 9),
    ('odoo_shadow_ipai_audit_mixin', 'ipai.audit.mixin', 'ipai_platform_audit', 1),
    ('odoo_shadow_ipai_bir_dat_wizard', 'ipai.bir.dat.wizard', 'ipai', 10),
    ('odoo_shadow_ipai_bir_form_schedule', 'ipai.bir.form.schedule', 'ipai', 13),
    ('odoo_shadow_ipai_bir_process_step', 'ipai.bir.process.step', 'ipai', 7),
    ('odoo_shadow_ipai_bir_schedule_item', 'ipai.bir.schedule.item', 'ipai', 5),
    ('odoo_shadow_ipai_bir_schedule_line', 'ipai.bir.schedule.line', 'ipai', 10),
    ('odoo_shadow_ipai_bir_schedule_step', 'ipai.bir.schedule.step', 'ipai', 6),
    ('odoo_shadow_ipai_close_generated_map', 'ipai.close.generated.map', 'ipai', 8),
    ('odoo_shadow_ipai_close_generation_run', 'ipai.close.generation.run', 'ipai', 28),
    ('odoo_shadow_ipai_close_generator', 'ipai.close.generator', 'ipai', 1),
    ('odoo_shadow_ipai_close_task_step', 'ipai.close.task.step', 'ipai', 7),
    ('odoo_shadow_ipai_close_task_template', 'ipai.close.task.template', 'ipai', 28),
    ('odoo_shadow_ipai_convert_phases_wizard', 'ipai.convert.phases.wizard', 'ipai', 6),
    ('odoo_shadow_ipai_directory_person', 'ipai.directory.person', 'ipai', 5),
    ('odoo_shadow_ipai_equipment_asset', 'ipai.equipment.asset', 'ipai', 11),
    ('odoo_shadow_ipai_equipment_booking', 'ipai.equipment.booking', 'ipai', 8),
    ('odoo_shadow_ipai_equipment_incident', 'ipai.equipment.incident', 'ipai', 7),
    ('odoo_shadow_ipai_finance_bir_schedule', 'ipai.finance.bir_schedule', 'ipai', 15),
    ('odoo_shadow_ipai_finance_close_generate_wizard', 'ipai.finance.close.generate.wizard', 'ipai', 3),
    ('odoo_shadow_ipai_finance_directory', 'ipai.finance.directory', 'ipai', 5),
    ('odoo_shadow_ipai_finance_logframe', 'ipai.finance.logframe', 'ipai', 8),
    ('odoo_shadow_ipai_finance_person', 'ipai.finance.person', 'ipai', 5),
    ('odoo_shadow_ipai_finance_ppm_golive_checklist', 'ipai.finance.ppm.golive.checklist', 'ipai_finance_ppm_golive', 19),
    ('odoo_shadow_ipai_finance_ppm_golive_item', 'ipai.finance.ppm.golive.item', 'ipai_finance_ppm_golive', 10),
    ('odoo_shadow_ipai_finance_ppm_golive_section', 'ipai.finance.ppm.golive.section', 'ipai_finance_ppm_golive', 7),
    ('odoo_shadow_ipai_finance_seed_wizard', 'ipai.finance.seed.wizard', 'ipai', 1),
    ('odoo_shadow_ipai_finance_task_template', 'ipai.finance.task.template', 'ipai', 21),
    ('odoo_shadow_ipai_generate_bir_tasks_wizard', 'ipai.generate.bir.tasks.wizard', 'ipai', 4),
    ('odoo_shadow_ipai_generate_im_projects_wizard', 'ipai.generate.im.projects.wizard', 'ipai', 4),
    ('odoo_shadow_ipai_generate_month_end_wizard', 'ipai.generate.month.end.wizard', 'ipai', 3),
    ('odoo_shadow_ipai_grid_column', 'ipai.grid.column', 'ipai_grid_view', 30),
    ('odoo_shadow_ipai_grid_filter', 'ipai.grid.filter', 'ipai_grid_view', 12),
    ('odoo_shadow_ipai_grid_filter_condition', 'ipai.grid.filter.condition', 'ipai_grid_view', 13),
    ('odoo_shadow_ipai_grid_view', 'ipai.grid.view', 'ipai_grid_view', 19),
    ('odoo_shadow_ipai_month_end_closing', 'ipai.month.end.closing', 'ipai_month_end', 9),
    ('odoo_shadow_ipai_month_end_task', 'ipai.month.end.task', 'ipai_month_end', 24),
    ('odoo_shadow_ipai_month_end_task_template', 'ipai.month.end.task.template', 'ipai_month_end', 14),
    ('odoo_shadow_ipai_month_end_template', 'ipai.month.end.template', 'ipai', 4),
    ('odoo_shadow_ipai_month_end_template_step', 'ipai.month.end.template.step', 'ipai', 6),
    ('odoo_shadow_ipai_ocr_job', 'ipai.ocr.job', 'ipai_ocr_gateway', 17),
    ('odoo_shadow_ipai_ocr_provider', 'ipai.ocr.provider', 'ipai_ocr_gateway', 12),
    ('odoo_shadow_ipai_permission', 'ipai.permission', 'ipai_platform_permissions', 8),
    ('odoo_shadow_ipai_ph_holiday', 'ipai.ph.holiday', 'ipai_month_end', 4),
    ('odoo_shadow_ipai_share_token', 'ipai.share.token', 'ipai_platform_permissions', 8),
    ('odoo_shadow_ipai_sms_message', 'ipai.sms.message', 'ipai_sms_gateway', 18),
    ('odoo_shadow_ipai_sms_provider', 'ipai.sms.provider', 'ipai_sms_gateway', 13),
    ('odoo_shadow_ipai_studio_ai_history', 'ipai.studio.ai.history', 'ipai', 13),
    ('odoo_shadow_ipai_studio_ai_wizard', 'ipai.studio.ai.wizard', 'ipai', 18),
    ('odoo_shadow_ipai_travel_request', 'ipai.travel.request', 'ipai', 11),
    ('odoo_shadow_ipai_workflow_mixin', 'ipai.workflow.mixin', 'ipai_platform_workflow', 3),
    ('odoo_shadow_ipai_workos_block', 'ipai.workos.block', 'ipai_workos_blocks', 13),
    ('odoo_shadow_ipai_workos_canvas', 'ipai.workos.canvas', 'ipai_workos_canvas', 5),
    ('odoo_shadow_ipai_workos_comment', 'ipai.workos.comment', 'ipai_workos_collab', 12),
    ('odoo_shadow_ipai_workos_database', 'ipai.workos.database', 'ipai_workos_db', 7),
    ('odoo_shadow_ipai_workos_page', 'ipai.workos.page', 'ipai_workos_core', 14),
    ('odoo_shadow_ipai_workos_property', 'ipai.workos.property', 'ipai_workos_db', 9),
    ('odoo_shadow_ipai_workos_row', 'ipai.workos.row', 'ipai_workos_db', 5),
    ('odoo_shadow_ipai_workos_search', 'ipai.workos.search', 'ipai_workos_search', 6),
    ('odoo_shadow_ipai_workos_search_history', 'ipai.workos.search.history', 'ipai_workos_search', 3),
    ('odoo_shadow_ipai_workos_space', 'ipai.workos.space', 'ipai_workos_core', 9),
    ('odoo_shadow_ipai_workos_template', 'ipai.workos.template', 'ipai_workos_templates', 10),
    ('odoo_shadow_ipai_workos_template_tag', 'ipai.workos.template.tag', 'ipai_workos_templates', 2),
    ('odoo_shadow_ipai_workos_view', 'ipai.workos.view', 'ipai_workos_views', 12),
    ('odoo_shadow_ipai_workos_workspace', 'ipai.workos.workspace', 'ipai_workos_core', 7),
    ('odoo_shadow_ipai_workspace', 'ipai.workspace', 'ipai', 27),
    ('odoo_shadow_ipai_workspace_link', 'ipai.workspace.link', 'ipai', 5),
    ('odoo_shadow_ir_actions', 'ir.actions.act_multi', 'web_ir_actions_act_multi', 1),
    ('odoo_shadow_ir_actions', 'ir.actions.act_window.message', 'web_ir_actions_act_window_message', 1),
    ('odoo_shadow_ir_actions_act_window_view', 'ir.actions.act_window.view', 'web_timeline', 1),
    ('odoo_shadow_ir_actions_actions', 'ir.actions.actions', 'base_temporary_action', 1),
    ('odoo_shadow_ir_actions_report', 'ir.actions.report', 'account_financial_report', 1),
    ('odoo_shadow_ir_cron', 'ir.cron', 'base_cron_exclusion', 1),
    ('odoo_shadow_ir_exports', 'ir.exports', 'jsonifier', 2),
    ('odoo_shadow_ir_exports_line', 'ir.exports.line', 'jsonifier', 5),
    ('odoo_shadow_ir_exports_resolver', 'ir.exports.resolver', 'jsonifier', 3),
    ('odoo_shadow_ir_model', 'ir.model', 'base_force_record_noupdate', 12),
    ('odoo_shadow_ir_model_fields', 'ir.model.fields', 'database_cleanup', 6),
    ('odoo_shadow_ir_model_index_size', 'ir.model.index.size', 'database_size', 3),
    ('odoo_shadow_ir_model_relation_size', 'ir.model.relation.size', 'database_size', 3),
    ('odoo_shadow_ir_model_size', 'ir.model.size', 'database_size', 11),
    ('odoo_shadow_ir_module_author', 'ir.module.author', 'module_analysis', 2),
    ('odoo_shadow_ir_module_module', 'ir.module.module', 'module_analysis', 8),
    ('odoo_shadow_ir_module_type', 'ir.module.type', 'module_analysis', 3),
    ('odoo_shadow_ir_module_type_rule', 'ir.module.type.rule', 'module_analysis', 3),
    ('odoo_shadow_ir_sequence_option', 'ir.sequence.option', 'base_sequence_option', 4),
    ('odoo_shadow_ir_sequence_option_line', 'ir.sequence.option.line', 'base_sequence_option', 10),
    ('odoo_shadow_ir_ui_view', 'ir.ui.view', 'base_view_inheritance_extension', 1),
    ('odoo_shadow_journal_ledger_report_wizard', 'journal.ledger.report.wizard', 'account_financial_report', 9),
    ('odoo_shadow_m2x_create_edit_option', 'm2x.create.edit.option', 'web_m2x_options_manager', 9),
    ('odoo_shadow_mis_cash_flow_forecast_line', 'mis.cash_flow.forecast_line', 'mis_builder_cash_flow', 6),
    ('odoo_shadow_mis_report_instance', 'mis.report.instance', 'mis_template_financial_report', 2),
    ('odoo_shadow_mis_report_kpi', 'mis.report.kpi', 'mis_template_financial_report', 1),
    ('odoo_shadow_open_items_report_wizard', 'open.items.report.wizard', 'account_financial_report', 11),
    ('odoo_shadow_ph_holiday', 'ph.holiday', 'ipai_tbwa_finance', 5),
    ('odoo_shadow_ppm_close_task', 'ppm.close.task', 'ipai', 25),
    ('odoo_shadow_ppm_close_template', 'ppm.close.template', 'ipai', 14),
    ('odoo_shadow_ppm_kpi_snapshot', 'ppm.kpi.snapshot', 'ipai', 18),
    ('odoo_shadow_ppm_monthly_close', 'ppm.monthly.close', 'ipai', 12),
    ('odoo_shadow_ppm_portfolio', 'ppm.portfolio', 'ipai', 17),
    ('odoo_shadow_ppm_program', 'ppm.program', 'ipai', 20),
    ('odoo_shadow_ppm_resource_allocation', 'ppm.resource.allocation', 'ipai', 15),
    ('odoo_shadow_ppm_risk', 'ppm.risk', 'ipai', 23),
    ('odoo_shadow_product_template', 'product.template', 'sale_project_copy_tasks', 11),
    ('odoo_shadow_project_assignment', 'project.assignment', 'project_role', 6),
    ('odoo_shadow_project_milestone', 'project.milestone', 'ipai', 17),
    ('odoo_shadow_project_project', 'project.project', 'ipai', 44),
    ('odoo_shadow_project_role', 'project.role', 'project_role', 7),
    ('odoo_shadow_project_stakeholder', 'project.stakeholder', 'project_stakeholder', 4),
    ('odoo_shadow_project_stakeholder_role', 'project.stakeholder.role', 'project_stakeholder', 1),
    ('odoo_shadow_project_tags', 'project.tags', 'project_tag_hierarchy', 3),
    ('odoo_shadow_project_task', 'project.task', 'ipai', 106),
    ('odoo_shadow_project_task_checklist_item', 'project.task.checklist.item', 'ipai', 9),
    ('odoo_shadow_project_task_description_template', 'project.task.description.template', 'project_task_description_template', 4),
    ('odoo_shadow_project_task_merge', 'project.task.merge', 'project_merge', 4),
    ('odoo_shadow_project_task_stock_product_set_wizard', 'project.task.stock.product.set.wizard', 'project_task_stock_product_set', 1),
    ('odoo_shadow_project_task_type', 'project.task.type', 'project_task_default_stage', 4),
    ('odoo_shadow_project_type', 'project.type', 'project_type', 7),
    ('odoo_shadow_project_version', 'project.version', 'project_version', 2),
    ('odoo_shadow_purchase_order', 'purchase.order', 'ipai', 1),
    ('odoo_shadow_quick_start_screen', 'quick.start.screen', 'web_quick_start_screen', 1),
    ('odoo_shadow_quick_start_screen_action', 'quick.start.screen.action', 'web_quick_start_screen', 10),
    ('odoo_shadow_report_project_task_user', 'report.project.task.user', 'project_task_ancestor', 3),
    ('odoo_shadow_report_xlsx_wizard', 'report.xlsx.wizard', 'excel_import_export', 2),
    ('odoo_shadow_res_company', 'res.company', 'account_reconcile_oca', 17),
    ('odoo_shadow_res_config_settings', 'res.config.settings', 'account_financial_report', 29),
    ('odoo_shadow_res_partner', 'res.partner', 'account_move_base_import', 9),
    ('odoo_shadow_res_remote', 'res.remote', 'base_remote', 3),
    ('odoo_shadow_res_users', 'res.users', 'base_model_restrict_update', 12),
    ('odoo_shadow_sale_order', 'sale.order', 'base_transaction_id', 2),
    ('odoo_shadow_sale_order_line', 'sale.order.line', 'sale_project_copy_tasks', 1),
    ('odoo_shadow_srm_kpi_category', 'srm.kpi.category', 'ipai', 8),
    ('odoo_shadow_srm_qualification', 'srm.qualification', 'ipai', 16),
    ('odoo_shadow_srm_qualification_checklist', 'srm.qualification.checklist', 'ipai', 9),
    ('odoo_shadow_srm_scorecard', 'srm.scorecard', 'ipai', 10),
    ('odoo_shadow_srm_scorecard_line', 'srm.scorecard.line', 'ipai', 8),
    ('odoo_shadow_srm_supplier', 'srm.supplier', 'ipai', 20),
    ('odoo_shadow_statement_common_wizard', 'statement.common.wizard', 'partner_statement', 11),
    ('odoo_shadow_stock_move', 'stock.move', 'project_task_stock', 3),
    ('odoo_shadow_stock_move_line', 'stock.move.line', 'project_task_stock', 1),
    ('odoo_shadow_stock_scrap', 'stock.scrap', 'project_task_stock', 1),
    ('odoo_shadow_superset_analytics_view', 'superset.analytics.view', 'ipai_superset_connector', 10),
    ('odoo_shadow_superset_bulk_dataset_wizard', 'superset.bulk.dataset.wizard', 'ipai_superset_connector', 3),
    ('odoo_shadow_superset_connection', 'superset.connection', 'ipai_superset_connector', 24),
    ('odoo_shadow_superset_dataset', 'superset.dataset', 'ipai_superset_connector', 22),
    ('odoo_shadow_superset_dataset_column', 'superset.dataset.column', 'ipai_superset_connector', 11),
    ('odoo_shadow_superset_dataset_wizard', 'superset.dataset.wizard', 'ipai_superset_connector', 9),
    ('odoo_shadow_test_partner_time_window', 'test.partner.time.window', 'test_base_time_window', 1),
    ('odoo_shadow_test_time_window_model', 'test.time.window.model', 'base_time_window', 1),
    ('odoo_shadow_time_weekday', 'time.weekday', 'base_time_window', 1),
    ('odoo_shadow_time_window_mixin', 'time.window.mixin', 'base_time_window', 2),
    ('odoo_shadow_timesheets_analysis_report', 'timesheets.analysis.report', 'project_task_ancestor', 1),
    ('odoo_shadow_trgm_index', 'trgm.index', 'base_search_fuzzy', 3),
    ('odoo_shadow_trial_balance_report_wizard', 'trial.balance.report.wizard', 'account_financial_report', 19),
    ('odoo_shadow_upgrade_analysis', 'upgrade.analysis', 'upgrade_analysis', 6),
    ('odoo_shadow_upgrade_attribute', 'upgrade.attribute', 'upgrade_analysis', 3),
    ('odoo_shadow_upgrade_comparison_config', 'upgrade.comparison.config', 'upgrade_analysis', 8),
    ('odoo_shadow_upgrade_generate_record_wizard', 'upgrade.generate.record.wizard', 'upgrade_analysis', 1),
    ('odoo_shadow_upgrade_install_wizard', 'upgrade.install.wizard', 'upgrade_analysis', 2),
    ('odoo_shadow_upgrade_record', 'upgrade.record', 'upgrade_analysis', 13),
    ('odoo_shadow_vacuum_rule', 'vacuum.rule', 'autovacuum_message_attachment', 14),
    ('odoo_shadow_vat_report_wizard', 'vat.report.wizard', 'account_financial_report', 6),
    ('odoo_shadow_web_editor_class', 'web.editor.class', 'web_editor_class_selector', 4),
    ('odoo_shadow_web_form_banner_rule', 'web.form.banner.rule', 'web_form_banner', 11),
    ('odoo_shadow_wizard_open_tax_balances', 'wizard.open.tax.balances', 'account_tax_balance', 4),
    ('odoo_shadow_xlsx_report', 'xlsx.report', 'excel_import_export', 5),
    ('odoo_shadow_xlsx_template', 'xlsx.template', 'excel_import_export', 22),
    ('odoo_shadow_xlsx_template_export', 'xlsx.template.export', 'excel_import_export', 13),
    ('odoo_shadow_xlsx_template_import', 'xlsx.template.import', 'excel_import_export', 9)
ON CONFLICT (table_name) DO UPDATE SET
    odoo_model = EXCLUDED.odoo_model,
    odoo_module = EXCLUDED.odoo_module,
    field_count = EXCLUDED.field_count,
    updated_at = now();
