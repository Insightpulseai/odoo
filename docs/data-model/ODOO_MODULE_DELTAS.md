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
  - `ipai_agent_knowledge_source`
  - `ipai_agent_run`
  - `ipai_agent_skill`
  - `ipai_agent_tool`
  - `ipai_ai_studio_run`
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
  - `ipai_finance_close_generate_wizard`
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
  - `srm_kpi_category`
  - `srm_qualification`
  - `srm_qualification_checklist`
  - `srm_scorecard`
  - `srm_scorecard_line`
  - `srm_supplier`
- Extended tables:
  - `hr_employee`: x_master_control_offboarded, x_master_control_onboarded
  - `hr_expense`: project_id, requires_project, travel_request_id, x_master_control_submitted
  - `ipai_bir_form_schedule`: approval_date, bir_deadline, filing_date, form_code, last_reminder_sent, period, prep_date, reminder_count, responsible_approval_id, responsible_prep_id, responsible_review_id, review_date, status, step_ids
  - `ipai_workspace`: account_manager_id, active, brand_name, campaign_type, channel_mix, child_ids, client_id, closing_stage, code, color, company_id, date_end, date_start, engagement_count, entity_code, fiscal_period, industry, invoice_count, is_critical, link_ids, name, parent_id, planned_hours, progress, project_count, remaining_hours, sequence, stage, workspace_type
  - `project_milestone`: alert_days_before, approval_date, approval_required, approver_id, baseline_deadline, completed_task_count, completion_criteria, dedication, deliverables, execution, gate_status, last_alert_sent, milestone_type, risk_level, risk_notes, task_count, task_ids, variance_days
  - `project_project`: actual_finish, actual_start, assignment_ids, baseline_finish, baseline_start, child_ids, child_ids_count, clarity_id, critical_milestone_count, department_id, group_ids, health_status, hr_category_ids, im_code, im_count, im_task_count, inherit_assignments, ipai_finance_enabled, ipai_im_code, ipai_is_im_project, ipai_root_project_id, is_program, is_template, key, limit_role_to_assignments, location_dest_id, location_id, milestone_count, name, overall_progress, overall_status, parent_id, parent_path, phase_count, picking_type_id, portfolio_id, ppm_program_ids, pr_required_states, program_code, program_type, purchase_count, purchase_invoice_count, purchase_invoice_line_total, purchase_line_total, sequence_code, show_key_warning, stage_last_update_date, stakeholder_ids, stock_analytic_date, tag_ids, task_key_sequence_id, type_id, type_ids, variance_finish, variance_start, version_ids, x_cycle_code
  - `project_task`: activity_type, actual_cost, actual_hours, allow_moves_action_assign, allow_moves_action_confirm, ancestor_id, approval_duration, approver_id, auto_sync, bir_approval_due_date, bir_deadline, bir_form, bir_payment_due_date, bir_period_label, bir_prep_due_date, bir_related, bir_schedule_id, child_task_count, closing_due_date, cluster, code, cost_variance, critical_path, description_template_id, domain_hr_category_ids, domain_user_ids, done_stock_moves, earned_value, employee_ids, erp_ref, fd_id, finance_category, finance_code, finance_deadline_type, finance_logframe_id, finance_person_id, finance_supervisor_id, free_float, gate_approver_id, gate_decision, gate_milestone_id, group_id, has_gate, hr_category_ids, ipai_compliance_step, ipai_days_to_deadline, ipai_deadline_offset_workdays, ipai_owner_code, ipai_owner_role, ipai_status_bucket, ipai_task_category, ipai_template_id, is_finance_ppm, is_phase, key, lag_days, lead_days, location_dest_id, location_id, milestone_count, move_ids, notes, owner_code, period_covered, phase_baseline_finish, phase_baseline_start, phase_progress, phase_status, phase_type, phase_variance_days, picking_type_id, planned_date_end, planned_date_start, planned_hours, planned_value, portal_url, portal_url_visible, pr_required_states, pr_uri, prep_duration, priority, project_department_id, relative_due, remaining_hours, resource_allocation, review_duration, reviewer_id, role_code, schedule_variance, scrap_count, scrap_ids, sfm_id, stage_id, stock_analytic_account_id, stock_analytic_date, stock_analytic_distribution, stock_analytic_line_ids, stock_moves_is_locked, stock_state, tag_ids, target_date, total_float, type_id, unreserve_visible, url, use_stock_moves, user_ids, version_id, wbs_code, x_cycle_key, x_external_key, x_obsolete, x_seed_hash, x_step_code, x_task_template_code
  - `project_task_checklist_item`: actual_hours, assigned_user_id, blocker_description, completed_date, due_date, estimated_hours, notes, priority, status
  - `purchase_order`: x_master_control_submitted
- Relation tables:
  - `a1_check_result_attachment_ids_rel`
  - `a1_role_group_ids_rel`
  - `a1_template_check_rel`
  - `advisor_playbook_category_ids_rel`
  - `advisor_recommendation_tag_ids_rel`
  - `ipai_skill_knowledge_rel`
  - `ipai_skill_tool_rel`
  - `ppm_program_project_rel`
  - `project_pr_required`
  - `project_project_group_ids_rel`
  - `project_project_hr_category_ids_rel`
  - `project_project_tag_ids_rel`
  - `project_project_type_ids_rel`
  - `project_task_employee_ids_rel`
  - `project_task_hr_category_ids_rel`
  - `project_task_pr_required_states_rel`
  - `project_task_tag_ids_rel`
  - `project_task_user_ids_rel`
  - `srm_qualification_document_ids_rel`
  - `srm_supplier_category_ids_rel`

## ipai_ask_ai

- New tables:
  - `discuss_channel`
  - `ipai_ask_ai_service`
- Extended tables:
  - `discuss_channel`: is_ai_channel

## ipai_ask_ai_chatter

- New tables:
  - `ipai_ask_ai_chatter_request`

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

## ipai_ocr_gateway

- New tables:
  - `ipai_ocr_job`
  - `ipai_ocr_provider`

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

## ipai_sms_gateway

- New tables:
  - `ipai_sms_message`
  - `ipai_sms_provider`

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
