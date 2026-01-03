# Odoo Module Deltas

## ipai

- New tables:
  - `a1_check`
  - `a1_check_result`
  - `a1_export_run`
  - `a1_role`
  - `a1_task`
  - `a1_task_checklist`
  - `a1_tasklist`
  - `a1_template`
  - `a1_template_checklist`
  - `a1_template_step`
  - `a1_workstream`
  - `account_move`
  - `advisor_category`
  - `advisor_playbook`
  - `advisor_recommendation`
  - `advisor_score`
  - `advisor_tag`
  - `close_approval_gate`
  - `close_approval_gate_template`
  - `close_cycle`
  - `close_exception`
  - `close_task`
  - `close_task_category`
  - `close_task_checklist`
  - `close_task_template`
  - `close_task_template_checklist`
  - `finance_bir_deadline`
  - `finance_ppm_bir_calendar`
  - `finance_ppm_dashboard`
  - `finance_ppm_import_wizard`
  - `finance_ppm_logframe`
  - `finance_ppm_ph_holiday`
  - `finance_ppm_tdi_audit`
  - `hr_employee`
  - `hr_expense`
  - `ipai_asset`
  - `ipai_asset_category`
  - `ipai_asset_checkout`
  - `ipai_asset_reservation`
  - `ipai_bir_dat_wizard`
  - `ipai_bir_form_schedule`
  - `ipai_bir_process_step`
  - `ipai_bir_schedule_item`
  - `ipai_bir_schedule_line`
  - `ipai_bir_schedule_step`
  - `ipai_close_generated_map`
  - `ipai_close_generation_run`
  - `ipai_close_generator`
  - `ipai_close_task_step`
  - `ipai_close_task_template`
  - `ipai_convert_phases_wizard`
  - `ipai_directory_person`
  - `ipai_equipment_asset`
  - `ipai_equipment_booking`
  - `ipai_equipment_incident`
  - `ipai_finance_bir_schedule`
  - `ipai_finance_directory`
  - `ipai_finance_logframe`
  - `ipai_finance_person`
  - `ipai_finance_seed_service`
  - `ipai_finance_seed_wizard`
  - `ipai_finance_task_template`
  - `ipai_generate_bir_tasks_wizard`
  - `ipai_generate_im_projects_wizard`
  - `ipai_generate_month_end_wizard`
  - `ipai_month_end_template`
  - `ipai_month_end_template_step`
  - `ipai_studio_ai_history`
  - `ipai_studio_ai_wizard`
  - `ipai_travel_request`
  - `ipai_workspace`
  - `ipai_workspace_link`
  - `ppm_close_task`
  - `ppm_close_template`
  - `ppm_kpi_snapshot`
  - `ppm_monthly_close`
  - `ppm_portfolio`
  - `ppm_program`
  - `ppm_resource_allocation`
  - `ppm_risk`
  - `project_milestone`
  - `project_project`
  - `project_task`
  - `project_task_checklist_item`
  - `purchase_order`
  - `res_config_settings`
  - `res_partner`
  - `res_users`
  - `srm_kpi_category`
  - `srm_qualification`
  - `srm_qualification_checklist`
  - `srm_scorecard`
  - `srm_scorecard_line`
  - `srm_supplier`
- Extended tables:
  - `account_move`: bir_2307_date, bir_2307_generated, ewt_amount
  - `close_task`: a1_task_id, approval_deadline, approval_done_by, approval_done_date, approve_done_date, approve_due_date, approve_notes, approve_user_id, approver_id, attachment_ids, category_id, checklist_done_pct, checklist_ids, checklist_progress, company_id, cycle_id, days_overdue, description, exception_ids, external_key, gl_entry_count, gl_entry_ids, has_exceptions, has_open_exceptions, is_overdue, name, notes, prep_deadline, prep_done_by, prep_done_date, prep_due_date, prep_notes, prep_user_id, preparer_id, review_deadline, review_done_by, review_done_date, review_due_date, review_notes, review_result, review_user_id, reviewer_id, sequence, state, template_id
  - `hr_employee`: x_master_control_offboarded, x_master_control_onboarded
  - `hr_expense`: project_id, requires_project, travel_request_id, x_master_control_submitted
  - `ipai_workspace`: account_manager_id, active, brand_name, campaign_type, channel_mix, child_ids, client_id, closing_stage, code, color, company_id, date_end, date_start, engagement_count, entity_code, fiscal_period, industry, invoice_count, is_critical, link_ids, name, parent_id, planned_hours, progress, project_count, remaining_hours, sequence, stage, workspace_type
  - `project_milestone`: alert_days_before, approval_date, approval_required, approver_id, baseline_deadline, completed_task_count, completion_criteria, deliverables, gate_status, last_alert_sent, milestone_type, risk_level, risk_notes, task_count, task_ids, variance_days
  - `project_project`: actual_finish, actual_start, baseline_finish, baseline_start, child_ids, clarity_id, critical_milestone_count, health_status, im_code, im_count, im_task_count, ipai_finance_enabled, ipai_im_code, ipai_is_im_project, ipai_root_project_id, is_program, milestone_count, overall_progress, overall_status, parent_id, phase_count, portfolio_id, ppm_program_ids, program_code, program_type, variance_finish, variance_start, x_cycle_code
  - `project_task`: activity_type, actual_cost, actual_hours, approval_duration, approver_id, auto_sync, bir_approval_due_date, bir_deadline, bir_form, bir_payment_due_date, bir_period_label, bir_prep_due_date, bir_related, bir_schedule_id, child_task_count, closing_due_date, cluster, cost_variance, critical_path, earned_value, erp_ref, fd_id, finance_category, finance_code, finance_deadline_type, finance_logframe_id, finance_person_id, finance_supervisor_id, free_float, gate_approver_id, gate_decision, gate_milestone_id, has_gate, ipai_compliance_step, ipai_days_to_deadline, ipai_owner_code, ipai_owner_role, ipai_status_bucket, ipai_task_category, ipai_template_id, is_finance_ppm, is_phase, lag_days, lead_days, milestone_count, owner_code, period_covered, phase_baseline_finish, phase_baseline_start, phase_progress, phase_status, phase_type, phase_variance_days, planned_hours, planned_value, prep_duration, relative_due, remaining_hours, resource_allocation, review_duration, reviewer_id, role_code, schedule_variance, sfm_id, target_date, total_float, wbs_code, x_cycle_key, x_external_key, x_obsolete, x_seed_hash, x_step_code, x_task_template_code
  - `project_task_checklist_item`: actual_hours, assigned_user_id, blocker_description, completed_date, due_date, estimated_hours, notes, priority, status
  - `purchase_order`: x_master_control_submitted
  - `res_config_settings`: ipai_enable_finance_project_analytics, superset_auto_sync, superset_connection_id, superset_create_analytics_views, superset_enable_rls, superset_sync_interval
  - `res_partner`: bir_registered, bir_registration_date, srm_overall_score, srm_supplier_id, srm_tier, tax_type, tin, tin_branch_code
  - `res_users`: x_employee_code
- Relation tables:
  - `a1_check_result_attachment_ids_rel`
  - `a1_role_group_ids_rel`
  - `a1_template_check_rel`
  - `advisor_playbook_category_ids_rel`
  - `advisor_recommendation_tag_ids_rel`
  - `close_approval_gate_blocking_exceptions_rel`
  - `close_approval_gate_blocking_tasks_rel`
  - `close_task_attachment_ids_rel`
  - `close_task_category_gl_account_ids_rel`
  - `close_task_gl_entry_ids_rel`
  - `close_task_template_gl_account_ids_rel`
  - `ppm_program_project_rel`
  - `srm_qualification_document_ids_rel`
  - `srm_supplier_category_ids_rel`

## ipai_ask_ai

- New tables:
  - `discuss_channel`
  - `ipai_ask_ai_service`
- Extended tables:
  - `discuss_channel`: is_ai_channel

## ipai_bir_tax_compliance

- New tables:
  - `bir_alphalist`
  - `bir_alphalist_line`
  - `bir_filing_deadline`
  - `bir_tax_return`
  - `bir_tax_return_line`
  - `bir_vat_line`
  - `bir_vat_return`
  - `bir_withholding_line`
  - `bir_withholding_return`

## ipai_crm_pipeline

- New tables:
  - `crm_lead`
  - `crm_stage`
- Extended tables:
  - `crm_lead`: days_in_stage, last_call_date, last_meeting_date, stage_entry_date, stage_missing_fields, stage_rule_validated
  - `crm_stage`: ipai_automation_notes, ipai_enforce_rules, ipai_required_field_ids, ipai_sla_days, ipai_stage_color, ipai_stage_icon
- Relation tables:
  - `crm_stage_required_fields_rel`

## ipai_finance_ppm_golive

- New tables:
  - `ipai_finance_ppm_golive_checklist`
  - `ipai_finance_ppm_golive_item`
  - `ipai_finance_ppm_golive_section`
- Relation tables:
  - `ipai_finance_ppm_golive_checklist_section_ids_rel`

## ipai_grid_view

- New tables:
  - `ipai_grid_column`
  - `ipai_grid_filter`
  - `ipai_grid_filter_condition`
  - `ipai_grid_view`
- Relation tables:
  - `ipai_grid_view_visible_columns_rel`

## ipai_month_end

- New tables:
  - `ipai_month_end_closing`
  - `ipai_month_end_task`
  - `ipai_month_end_task_template`
  - `ipai_ph_holiday`
- Relation tables:
  - `ipai_task_template_dependency_rel`

## ipai_platform_approvals

- _No model changes detected._

## ipai_platform_audit

- New tables:
  - `ipai_audit_log`

## ipai_platform_permissions

- New tables:
  - `ipai_permission`
  - `ipai_share_token`

## ipai_platform_workflow

- _No model changes detected._

## ipai_ppm_a1

- New tables:
  - `ipai_export_seed_wizard`
  - `ipai_import_seed_wizard`
  - `ipai_localization_overlay`
  - `ipai_ppm_task`
  - `ipai_ppm_task_checklist`
  - `ipai_ppm_tasklist`
  - `ipai_ppm_taskrun`
  - `ipai_ppm_template`
  - `ipai_repo_export_run`
  - `ipai_stc_check`
  - `ipai_stc_scenario`
  - `ipai_stc_worklist_type`
  - `ipai_workstream`
- Relation tables:
  - `ipai_stc_scenario_check_ids_rel`

## ipai_superset_connector

- New tables:
  - `superset_analytics_view`
  - `superset_bulk_dataset_wizard`
  - `superset_connection`
  - `superset_dataset`
  - `superset_dataset_column`
  - `superset_dataset_wizard`
- Relation tables:
  - `superset_dataset_field_ids_rel`
  - `superset_dataset_wizard_field_ids_rel`

## ipai_tbwa_finance

- New tables:
  - `bir_return`
  - `bir_return_line`
  - `closing_period`
  - `compliance_check`
  - `finance_task`
  - `finance_task_template`
  - `ph_holiday`
- Relation tables:
  - `finance_task_template_dependency_rel`

## ipai_workos_blocks

- New tables:
  - `ipai_workos_block`

## ipai_workos_canvas

- New tables:
  - `ipai_workos_canvas`

## ipai_workos_collab

- New tables:
  - `ipai_workos_comment`
- Relation tables:
  - `workos_comment_mention_rel`

## ipai_workos_core

- New tables:
  - `ipai_workos_page`
  - `ipai_workos_space`
  - `ipai_workos_workspace`
- Relation tables:
  - `workspace_member_rel`

## ipai_workos_db

- New tables:
  - `ipai_workos_database`
  - `ipai_workos_property`
  - `ipai_workos_row`

## ipai_workos_search

- New tables:
  - `ipai_workos_search`
  - `ipai_workos_search_history`

## ipai_workos_templates

- New tables:
  - `ipai_workos_template`
  - `ipai_workos_template_tag`
- Relation tables:
  - `ipai_workos_template_tag_ids_rel`

## ipai_workos_views

- New tables:
  - `ipai_workos_view`
- Relation tables:
  - `ipai_workos_view_visible_property_ids_rel`
