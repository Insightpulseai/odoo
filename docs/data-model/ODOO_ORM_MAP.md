# Odoo ORM Map

## a1.check

- Module: `ipai`
- Model type: `Model`
- Table: `a1_check`
- SQL constraints:
  - `code_uniq`: `unique(code, company_id)` (Check code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Check code must be unique per company.)

### Persisted fields
- `active`: `Boolean`
- `check_type`: `Selection` (required)
- `close_gate_template_id`: `Many2one` (relation=close.approval.gate.template)
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `description`: `Html`
- `fail_action`: `Text`
- `name`: `Char` (required)
- `pass_criteria`: `Text`
- `sequence`: `Integer`
- `severity`: `Selection` (required)
- `template_ids`: `Many2many` (relation=a1.template)

### Non-persisted fields
- _none_

## a1.check.result

- Module: `ipai`
- Model type: `Model`
- Table: `a1_check_result`

### Persisted fields
- `attachment_ids`: `Many2many` (relation=ir.attachment)
- `check_id`: `Many2one` (relation=a1.check, required, ondelete=cascade)
- `evidence`: `Html`
- `executed_by`: `Many2one` (relation=res.users)
- `executed_date`: `Datetime`
- `result`: `Selection` (required)
- `result_notes`: `Text`
- `task_id`: `Many2one` (relation=a1.task, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## a1.export.run

- Module: `ipai`
- Model type: `Model`
- Table: `a1_export_run`

### Persisted fields
- `company_id`: `Many2one` (relation=res.company, required)
- `created_count`: `Integer`
- `error_count`: `Integer`
- `log`: `Text`
- `run_type`: `Selection` (required)
- `seed_hash`: `Char` (index)
- `seed_json`: `Text`
- `status`: `Selection` (required)
- `unchanged_count`: `Integer`
- `updated_count`: `Integer`
- `webhook_url`: `Char`

### Non-persisted fields
- _none_

## a1.role

- Module: `ipai`
- Model type: `Model`
- Table: `a1_role`
- SQL constraints:
  - `code_uniq`: `unique(code, company_id)` (Role code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Role code must be unique per company.)

### Persisted fields
- `active`: `Boolean`
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `default_user_id`: `Many2one` (relation=res.users)
- `description`: `Text`
- `fallback_user_id`: `Many2one` (relation=res.users)
- `group_ids`: `Many2many` (relation=res.groups)
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## a1.task

- Module: `ipai`
- Model type: `Model`
- Table: `a1_task`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `approval_deadline`: `Date`
- `approval_done_by`: `Many2one` (relation=res.users)
- `approval_done_date`: `Datetime`
- `approver_id`: `Many2one` (relation=res.users)
- `approver_role`: `Char`
- `checklist_progress`: `Float` (compute=_compute_checklist_progress)
- `close_task_id`: `Many2one` (relation=close.task)
- `company_id`: `Many2one` (relation=res.company, related=tasklist_id.company_id)
- `external_key`: `Char` (index)
- `name`: `Char` (required)
- `notes`: `Html`
- `owner_id`: `Many2one` (relation=res.users)
- `owner_role`: `Char`
- `prep_deadline`: `Date`
- `prep_done_by`: `Many2one` (relation=res.users)
- `prep_done_date`: `Datetime`
- `review_deadline`: `Date`
- `review_done_by`: `Many2one` (relation=res.users)
- `review_done_date`: `Datetime`
- `reviewer_id`: `Many2one` (relation=res.users)
- `reviewer_role`: `Char`
- `sequence`: `Integer`
- `state`: `Selection` (required)
- `tasklist_id`: `Many2one` (relation=a1.tasklist, required, index, ondelete=cascade)
- `template_id`: `Many2one` (relation=a1.template)
- `workstream_id`: `Many2one` (relation=a1.workstream, related=template_id.workstream_id)

### Non-persisted fields
- `checklist_ids`: `One2many` (relation=a1.task.checklist)

## a1.task.checklist

- Module: `ipai`
- Model type: `Model`
- Table: `a1_task_checklist`

### Persisted fields
- `code`: `Char` (required)
- `done_by`: `Many2one` (relation=res.users)
- `done_date`: `Datetime`
- `is_done`: `Boolean`
- `is_required`: `Boolean`
- `item_type`: `Selection` (required)
- `name`: `Char` (required)
- `sequence`: `Integer`
- `task_id`: `Many2one` (relation=a1.task, required, index, ondelete=cascade)
- `template_item_id`: `Many2one` (relation=a1.template.checklist)
- `value_attachment_id`: `Many2one` (relation=ir.attachment)
- `value_text`: `Text`

### Non-persisted fields
- _none_

## a1.tasklist

- Module: `ipai`
- Model type: `Model`
- Table: `a1_tasklist`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `period_uniq`: `unique(period_start, period_end, company_id)` (A tasklist for this period already exists.)
  - `period_uniq`: `unique(period_start, period_end, company_id)` (A tasklist for this period already exists.)

### Persisted fields
- `close_cycle_id`: `Many2one` (relation=close.cycle)
- `company_id`: `Many2one` (relation=res.company, required)
- `name`: `Char` (required)
- `notes`: `Html`
- `period_end`: `Date` (required)
- `period_label`: `Char` (compute=_compute_period_label)
- `period_start`: `Date` (required)
- `progress`: `Float` (compute=_compute_task_stats)
- `state`: `Selection` (required)
- `task_count`: `Integer` (compute=_compute_task_stats)
- `task_done_count`: `Integer` (compute=_compute_task_stats)
- `webhook_url`: `Char`

### Non-persisted fields
- `task_ids`: `One2many` (relation=a1.task)

## a1.template

- Module: `ipai`
- Model type: `Model`
- Table: `a1_template`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `code_uniq`: `unique(code, company_id)` (Template code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Template code must be unique per company.)

### Persisted fields
- `active`: `Boolean`
- `approval_days`: `Float`
- `approver_role`: `Char`
- `close_template_id`: `Many2one` (relation=close.task.template)
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `description`: `Html`
- `name`: `Char` (required)
- `owner_role`: `Char` (required)
- `phase_code`: `Char` (related=workstream_id.phase_code)
- `prep_days`: `Float`
- `review_days`: `Float`
- `reviewer_role`: `Char`
- `sequence`: `Integer`
- `total_days`: `Float` (compute=_compute_total_days)
- `workstream_id`: `Many2one` (relation=a1.workstream, required, index, ondelete=cascade)

### Non-persisted fields
- `checklist_ids`: `One2many` (relation=a1.template.checklist)
- `step_ids`: `One2many` (relation=a1.template.step)

## a1.template.checklist

- Module: `ipai`
- Model type: `Model`
- Table: `a1_template_checklist`

### Persisted fields
- `code`: `Char` (required)
- `instructions`: `Text`
- `is_required`: `Boolean`
- `item_type`: `Selection` (required)
- `name`: `Char` (required)
- `sequence`: `Integer`
- `template_id`: `Many2one` (relation=a1.template, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## a1.template.step

- Module: `ipai`
- Model type: `Model`
- Table: `a1_template_step`

### Persisted fields
- `assignee_role`: `Char`
- `code`: `Char` (required)
- `deadline_offset_days`: `Integer`
- `effort_days`: `Float`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `template_id`: `Many2one` (relation=a1.template, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## a1.workstream

- Module: `ipai`
- Model type: `Model`
- Table: `a1_workstream`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `code_uniq`: `unique(code, company_id)` (Workstream code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Workstream code must be unique per company.)

### Persisted fields
- `active`: `Boolean`
- `close_category_id`: `Many2one` (relation=close.task.category)
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `description`: `Html`
- `name`: `Char` (required)
- `owner_role_id`: `Many2one` (relation=a1.role)
- `owner_user_id`: `Many2one` (relation=res.users, compute=_compute_owner_user)
- `phase_code`: `Char`
- `sequence`: `Integer`
- `template_count`: `Integer` (compute=_compute_template_count)

### Non-persisted fields
- `template_ids`: `One2many` (relation=a1.template)

## abstract.mpld3.parser

- Module: `web_widget_mpld3_chart`
- Model type: `AbstractModel`
- Table: `abstract_mpld3_parser`

### Persisted fields

### Non-persisted fields
- _none_

## account.account

- Module: `account_financial_report`
- Model type: `Model`
- Table: `account_account`
- _inherit: `account.account`

### Persisted fields
- `centralized`: `Boolean`
- `hide_in_cash_flow`: `Boolean`

### Non-persisted fields
- _none_

## account.account.reconcile

- Module: `account_reconcile_oca`
- Model type: `Model`
- Table: `N/A`
- _inherit: `account.reconcile.abstract`

### Persisted fields
- `account_id`: `Many2one` (relation=account.account)
- `active`: `Boolean`
- `is_reconciled`: `Boolean`
- `name`: `Char`
- `partner_id`: `Many2one` (relation=res.partner)
- `reconcile_data_info`: `Serialized`

### Non-persisted fields
- _none_

## account.account.reconcile.data

- Module: `account_reconcile_oca`
- Model type: `TransientModel`
- Table: `account_account_reconcile_data`

### Persisted fields
- `data`: `Serialized`
- `reconcile_id`: `Integer` (required)
- `user_id`: `Many2one` (relation=res.users, required)

### Non-persisted fields
- _none_

## account.age.report.configuration

- Module: `account_financial_report`
- Model type: `Model`
- Table: `account_age_report_configuration`
- Python constraints:
  - `_check_line_ids`

### Persisted fields
- `company_id`: `Many2one` (relation=res.company)
- `name`: `Char` (required)

### Non-persisted fields
- `line_ids`: `One2many` (relation=account.age.report.configuration.line)

## account.age.report.configuration.line

- Module: `account_financial_report`
- Model type: `Model`
- Table: `account_age_report_configuration_line`
- SQL constraints:
  - `unique_name_config_combination`: `UNIQUE(name,account_age_report_config_id)` (Name must be unique per report configuration)
- Python constraints:
  - `_check_inferior_limit`

### Persisted fields
- `account_age_report_config_id`: `Many2one` (relation=account.age.report.configuration)
- `inferior_limit`: `Integer`
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## account.analytic.line

- Module: `project_task_ancestor`
- Model type: `Model`
- Table: `account_analytic_line`
- _inherit: `account.analytic.line`

### Persisted fields
- `ancestor_task_id`: `Many2one` (related=task_id.ancestor_id)
- `date_time`: `Datetime`
- `date_time_end`: `Datetime` (compute=_compute_date_time_end)
- `show_time_control`: `Selection` (compute=_compute_show_time_control)
- `stock_move_id`: `Many2one` (ondelete=cascade)
- `stock_task_id`: `Many2one` (ondelete=cascade)

### Non-persisted fields
- _none_

## account.bank.statement

- Module: `account_reconcile_oca`
- Model type: `Model`
- Table: `account_bank_statement`
- _inherit: `account.bank.statement`

### Persisted fields

### Non-persisted fields
- _none_

## account.bank.statement.line

- Module: `account_reconcile_analytic_tag`
- Model type: `Model`
- Table: `account_bank_statement_line`
- _inherit: `account.bank.statement.line, account.reconcile.abstract`

### Persisted fields
- `aggregate_id`: `Integer` (compute=_compute_reconcile_aggregate)
- `aggregate_name`: `Char` (compute=_compute_reconcile_aggregate)
- `analytic_distribution`: `Json`
- `analytic_precision`: `Integer`
- `can_reconcile`: `Boolean`
- `manual_account_id`: `Many2one` (relation=account.account)
- `manual_amount`: `Monetary`
- `manual_amount_in_currency`: `Monetary`
- `manual_analytic_tag_ids`: `Many2many`
- `manual_currency_id`: `Many2one` (relation=res.currency)
- `manual_exchange_counterpart`: `Boolean`
- `manual_in_currency`: `Boolean`
- `manual_in_currency_id`: `Many2one` (relation=res.currency)
- `manual_kind`: `Char`
- `manual_line_id`: `Many2one` (relation=account.move.line)
- `manual_model_id`: `Many2one` (relation=account.reconcile.model)
- `manual_move_id`: `Many2one` (relation=account.move)
- `manual_move_type`: `Selection`
- `manual_name`: `Char`
- `manual_original_amount`: `Monetary`
- `manual_partner_id`: `Many2one` (relation=res.partner)
- `previous_manual_amount_in_currency`: `Monetary`
- `reconcile_aggregate`: `Char` (compute=_compute_reconcile_aggregate)
- `reconcile_data`: `Serialized`
- `reconcile_data_info`: `Serialized`
- `reconcile_mode`: `Selection`

### Non-persisted fields
- _none_

## account.group

- Module: `account_financial_report`
- Model type: `Model`
- Table: `account_group`
- _inherit: `account.group`

### Persisted fields
- `complete_code`: `Char` (relation=Full Code, compute=_compute_complete_code)
- `complete_name`: `Char` (relation=Full Name, compute=_compute_complete_name)
- `compute_account_ids`: `Many2many` (relation=account.account, compute=_compute_group_accounts)
- `level`: `Integer` (compute=_compute_level)

### Non-persisted fields
- `account_ids`: `One2many` (compute=_compute_account_ids)
- `group_child_ids`: `One2many`

## account.journal

- Module: `account_move_base_import`
- Model type: `Model`
- Table: `account_journal`
- _inherit: `account.journal, mail.thread`

### Persisted fields
- `autovalidate_completed_move`: `Boolean`
- `commission_account_id`: `Many2one`
- `commission_analytic_account_id`: `Many2one`
- `company_currency_id`: `Many2one` (related=company_id.currency_id)
- `create_counterpart`: `Boolean`
- `import_type`: `Selection`
- `last_import_date`: `Datetime`
- `launch_import_completion`: `Boolean`
- `partner_id`: `Many2one`
- `receivable_account_id`: `Many2one`
- `reconcile_aggregate`: `Selection`
- `reconcile_mode`: `Selection` (required)
- `rule_ids`: `Many2many`
- `split_counterpart`: `Boolean`
- `used_for_completion`: `Boolean`
- `used_for_import`: `Boolean`

### Non-persisted fields
- _none_

## account.move

- Module: `account_in_payment`
- Model type: `Model`
- Table: `account_move`
- _inherit: `account.move, mail.thread`

### Persisted fields
- `bir_2307_date`: `Date`
- `bir_2307_generated`: `Boolean`
- `completion_logs`: `Text`
- `ewt_amount`: `Monetary` (compute=_compute_ewt_amount)
- `financial_type`: `Selection` (compute=_compute_financial_type)
- `import_partner_id`: `Many2one` (relation=res.partner)
- `transaction_id`: `Char` (index)
- `used_for_completion`: `Boolean` (related=journal_id.used_for_completion)

### Non-persisted fields
- _none_

## account.move.completion.rule

- Module: `account_move_base_import`
- Model type: `Model`
- Table: `account_move_completion_rule`

### Persisted fields
- `function_to_call`: `Selection`
- `journal_ids`: `Many2many`
- `name`: `Char`
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## account.move.line

- Module: `account_financial_report`
- Model type: `Model`
- Table: `account_move_line`
- _inherit: `account.move.line`

### Persisted fields
- `already_completed`: `Boolean`
- `analytic_account_ids`: `Many2many` (relation=account.analytic.account, compute=_compute_analytic_account_ids)

### Non-persisted fields
- _none_

## account.reconcile.abstract

- Module: `account_reconcile_analytic_tag`
- Model type: `AbstractModel`
- Table: `account_reconcile_abstract`
- _inherit: `account.reconcile.abstract`

### Persisted fields
- `add_account_move_line_id`: `Many2one` (relation=account.move.line)
- `company_currency_id`: `Many2one` (related=company_id.currency_id)
- `company_id`: `Many2one` (relation=res.company)
- `currency_id`: `Many2one` (relation=res.currency)
- `foreign_currency_id`: `Many2one` (relation=res.currency)
- `manual_delete`: `Boolean`
- `manual_reference`: `Char`
- `reconcile_data_info`: `Serialized` (compute=_compute_reconcile_data_info)

### Non-persisted fields
- _none_

## account.reconcile.model

- Module: `account_reconcile_model_oca`
- Model type: `Model`
- Table: `account_reconcile_model`
- _inherit: `account.reconcile.model`

### Persisted fields
- `unique_matching`: `Boolean`

### Non-persisted fields
- _none_

## account.reconcile.model.line

- Module: `account_reconcile_analytic_tag`
- Model type: `Model`
- Table: `account_reconcile_model_line`
- _inherit: `account.reconcile.model.line`

### Persisted fields
- `analytic_tag_ids`: `Many2many`

### Non-persisted fields
- _none_

## account.tax

- Module: `account_tax_balance`
- Model type: `Model`
- Table: `account_tax`
- _inherit: `account.tax`

### Persisted fields
- `balance`: `Float` (compute=_compute_balance)
- `balance_refund`: `Float` (compute=_compute_balance)
- `balance_regular`: `Float` (compute=_compute_balance)
- `base_balance`: `Float` (compute=_compute_balance)
- `base_balance_refund`: `Float` (compute=_compute_balance)
- `base_balance_regular`: `Float` (compute=_compute_balance)
- `has_moves`: `Boolean` (compute=_compute_has_moves)

### Non-persisted fields
- _none_

## account_financial_report_abstract_wizard

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `account_financial_report_abstract_wizard`

### Persisted fields
- `company_id`: `Many2one`
- `label_text_limit`: `Integer`

### Non-persisted fields
- _none_

## activity.statement.wizard

- Module: `partner_statement`
- Model type: `TransientModel`
- Table: `activity_statement_wizard`
- _inherit: `statement.common.wizard`

### Persisted fields
- `date_start`: `Date` (required)

### Non-persisted fields
- _none_

## advisor.category

- Module: `ipai`
- Model type: `Model`
- Table: `advisor_category`
- SQL constraints:
  - `code_unique`: `UNIQUE(code)` (Category code must be unique!)
  - `code_unique`: `UNIQUE(code)` (Category code must be unique!)

### Persisted fields
- `active`: `Boolean`
- `code`: `Char` (required)
- `color`: `Integer`
- `description`: `Text`
- `high_count`: `Integer` (compute=_compute_recommendation_count)
- `icon`: `Char`
- `latest_score`: `Integer` (compute=_compute_latest_score)
- `name`: `Char` (required)
- `open_count`: `Integer` (compute=_compute_recommendation_count)
- `recommendation_count`: `Integer` (compute=_compute_recommendation_count)
- `sequence`: `Integer`

### Non-persisted fields
- `recommendation_ids`: `One2many` (relation=advisor.recommendation)

## advisor.playbook

- Module: `ipai`
- Model type: `Model`
- Table: `advisor_playbook`

### Persisted fields
- `active`: `Boolean`
- `automation_kind`: `Selection`
- `automation_params`: `Text`
- `automation_ref`: `Char`
- `category_ids`: `Many2many` (relation=advisor.category)
- `code`: `Char`
- `description`: `Text`
- `name`: `Char` (required)
- `recommendation_count`: `Integer` (compute=_compute_recommendation_count)
- `steps_md`: `Text`

### Non-persisted fields
- `recommendation_ids`: `One2many` (relation=advisor.recommendation)

## advisor.recommendation

- Module: `ipai`
- Model type: `Model`
- Table: `advisor_recommendation`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `category_code`: `Char` (related=category_id.code)
- `category_id`: `Many2one` (relation=advisor.category, required, index)
- `confidence`: `Float`
- `currency_id`: `Many2one` (relation=res.currency)
- `date_due`: `Date`
- `date_resolved`: `Date`
- `description`: `Text`
- `estimated_savings`: `Monetary`
- `evidence`: `Text`
- `external_link`: `Char`
- `impact_score`: `Integer`
- `name`: `Char` (required)
- `owner_id`: `Many2one` (relation=res.users)
- `playbook_id`: `Many2one` (relation=advisor.playbook)
- `remediation_steps`: `Text`
- `resource_ref`: `Char`
- `resource_type`: `Char`
- `severity`: `Selection` (required)
- `severity_order`: `Integer` (compute=_compute_severity_order)
- `snooze_until`: `Date`
- `source`: `Selection`
- `status`: `Selection`
- `tag_ids`: `Many2many` (relation=advisor.tag)

### Non-persisted fields
- _none_

## advisor.score

- Module: `ipai`
- Model type: `Model`
- Table: `advisor_score`

### Persisted fields
- `as_of`: `Datetime` (required, index)
- `category_code`: `Char` (related=category_id.code)
- `category_id`: `Many2one` (relation=advisor.category, required, index, ondelete=cascade)
- `critical_count`: `Integer`
- `high_count`: `Integer`
- `inputs_json`: `Text`
- `open_count`: `Integer`
- `resolved_count`: `Integer`
- `score`: `Integer` (required)

### Non-persisted fields
- _none_

## advisor.tag

- Module: `ipai`
- Model type: `Model`
- Table: `advisor_tag`
- SQL constraints:
  - `name_unique`: `UNIQUE(name)` (Tag name must be unique!)
  - `name_unique`: `UNIQUE(name)` (Tag name must be unique!)

### Persisted fields
- `color`: `Integer`
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## afc.rag.service

- Module: `ipai_ask_ai`
- Model type: `AbstractModel`
- Table: `afc_rag_service`

### Persisted fields

### Non-persisted fields
- _none_

## aged.partner.balance.report.wizard

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `aged_partner_balance_report_wizard`
- _inherit: `account_financial_report_abstract_wizard`

### Persisted fields
- `account_code_from`: `Many2one`
- `account_code_to`: `Many2one`
- `account_ids`: `Many2many` (required)
- `age_partner_config_id`: `Many2one` (relation=account.age.report.configuration)
- `date_at`: `Date` (required)
- `date_from`: `Date`
- `partner_ids`: `Many2many`
- `payable_accounts_only`: `Boolean`
- `receivable_accounts_only`: `Boolean`
- `show_move_line_details`: `Boolean`
- `target_move`: `Selection` (required)

### Non-persisted fields
- _none_

## attachment.queue

- Module: `attachment_queue`
- Model type: `Model`
- Table: `attachment_queue`
- _inherit: `attachment.queue, mail.activity.mixin, mail.thread`
- _inherits: `ir.attachment via attachment_id`

### Persisted fields
- `attachment_id`: `Many2one` (relation=ir.attachment, required, ondelete=cascade)
- `date_done`: `Datetime`
- `failure_emails`: `Char` (compute=_compute_failure_emails)
- `file_type`: `Selection`
- `fs_storage_id`: `Many2one` (relation=fs.storage, related=task_id.backend_id)
- `method_type`: `Selection` (related=task_id.method_type)
- `state`: `Selection` (required)
- `state_message`: `Text`
- `task_id`: `Many2one` (relation=attachment.synchronize.task)

### Non-persisted fields
- _none_

## attachment.queue.reschedule

- Module: `attachment_queue`
- Model type: `TransientModel`
- Table: `attachment_queue_reschedule`

### Persisted fields
- `attachment_ids`: `Many2many`

### Non-persisted fields
- _none_

## attachment.synchronize.task

- Module: `attachment_synchronize`
- Model type: `Model`
- Table: `attachment_synchronize_task`

### Persisted fields
- `active`: `Boolean` (relation=Enabled)
- `after_import`: `Selection`
- `avoid_duplicated_files`: `Boolean`
- `backend_id`: `Many2one` (relation=fs.storage)
- `count_attachment_done`: `Integer` (compute=_compute_count_state)
- `count_attachment_failed`: `Integer` (compute=_compute_count_state)
- `count_attachment_pending`: `Integer` (compute=_compute_count_state)
- `failure_emails`: `Char`
- `file_type`: `Selection`
- `filepath`: `Char`
- `method_type`: `Selection` (required)
- `move_path`: `Char`
- `name`: `Char` (required)
- `new_name`: `Char`
- `pattern`: `Char`

### Non-persisted fields
- `attachment_ids`: `One2many` (relation=attachment.queue)

## auditlog.autovacuum

- Module: `auditlog`
- Model type: `TransientModel`
- Table: `auditlog_autovacuum`

### Persisted fields

### Non-persisted fields
- _none_

## auditlog.http.request

- Module: `auditlog`
- Model type: `Model`
- Table: `auditlog_http_request`

### Persisted fields
- `display_name`: `Char` (relation=Name, compute=_compute_display_name)
- `http_session_id`: `Many2one` (relation=auditlog.http.session, index)
- `name`: `Char` (relation=Path)
- `root_url`: `Char` (relation=Root URL)
- `user_context`: `Char` (relation=Context)
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- `log_ids`: `One2many` (relation=auditlog.log)

## auditlog.http.session

- Module: `auditlog`
- Model type: `Model`
- Table: `auditlog_http_session`

### Persisted fields
- `display_name`: `Char` (relation=Name, compute=_compute_display_name)
- `name`: `Char` (relation=Session ID, index)
- `user_id`: `Many2one` (relation=res.users, index)

### Non-persisted fields
- `http_request_ids`: `One2many` (relation=auditlog.http.request)

## auditlog.log

- Module: `auditlog`
- Model type: `Model`
- Table: `auditlog_log`

### Persisted fields
- `http_request_id`: `Many2one` (relation=auditlog.http.request, index)
- `http_session_id`: `Many2one` (relation=auditlog.http.session, index)
- `log_type`: `Selection`
- `method`: `Char`
- `model_id`: `Many2one` (relation=ir.model, index, ondelete=set null)
- `model_model`: `Char`
- `model_name`: `Char`
- `name`: `Char` (relation=Resource Name)
- `res_id`: `Integer` (relation=Resource ID)
- `res_ids`: `Char` (relation=Resource IDs)
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- `line_ids`: `One2many` (relation=auditlog.log.line)

## auditlog.log.line

- Module: `auditlog`
- Model type: `Model`
- Table: `auditlog_log_line`

### Persisted fields
- `field_description`: `Char` (relation=Description)
- `field_id`: `Many2one` (relation=ir.model.fields, index, ondelete=set null)
- `field_name`: `Char` (relation=Technical name)
- `log_id`: `Many2one` (relation=auditlog.log, index, ondelete=cascade)
- `new_value`: `Text`
- `new_value_text`: `Text` (relation=New value Text)
- `old_value`: `Text`
- `old_value_text`: `Text` (relation=Old value Text)

### Non-persisted fields
- _none_

## auditlog.log.line.view

- Module: `auditlog`
- Model type: `Model`
- Table: `N/A`
- _inherit: `auditlog.log.line`

### Persisted fields
- `http_request_id`: `Many2one` (relation=auditlog.http.request, index)
- `http_session_id`: `Many2one` (relation=auditlog.http.session, index)
- `log_type`: `Selection`
- `method`: `Char`
- `model_id`: `Many2one` (relation=ir.model)
- `model_model`: `Char`
- `model_name`: `Char`
- `name`: `Char`
- `res_id`: `Integer`
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- _none_

## auditlog.rule

- Module: `auditlog`
- Model type: `Model`
- Table: `auditlog_rule`
- SQL constraints:
  - `model_uniq`: `unique(model_id)` (There is already a rule defined on this model
You cannot define another: please edit the existing one.)

### Persisted fields
- `action_id`: `Many2one` (relation=ir.actions.act_window)
- `capture_record`: `Boolean`
- `fields_to_exclude_ids`: `Many2many` (relation=ir.model.fields)
- `log_create`: `Boolean` (relation=Log Creates)
- `log_export_data`: `Boolean` (relation=Log Exports)
- `log_read`: `Boolean` (relation=Log Reads)
- `log_type`: `Selection` (required)
- `log_unlink`: `Boolean` (relation=Log Deletes)
- `log_write`: `Boolean` (relation=Log Writes)
- `model_id`: `Many2one` (relation=ir.model, index, ondelete=set null)
- `model_model`: `Char`
- `model_name`: `Char`
- `name`: `Char` (required)
- `state`: `Selection` (required)
- `user_ids`: `Many2many` (relation=res.users)
- `users_to_exclude_ids`: `Many2many` (relation=res.users)

### Non-persisted fields
- _none_

## autovacuum.mixin

- Module: `autovacuum_message_attachment`
- Model type: `AbstractModel`
- Table: `autovacuum_mixin`

### Persisted fields

### Non-persisted fields
- _none_

## base

- Module: `autovacuum_message_attachment`
- Model type: `AbstractModel`
- Table: `base`
- _inherit: `base`

### Persisted fields
- `smart_search`: `Char` (compute=_compute_smart_search)

### Non-persisted fields
- `assigned_attachment_ids`: `One2many` (relation=ir.attachment)

## base.exception

- Module: `base_exception`
- Model type: `AbstractModel`
- Table: `base_exception`
- _inherit: `base.exception.method`

### Persisted fields
- `exception_ids`: `Many2many` (relation=exception.rule)
- `exceptions_summary`: `Html` (compute=_compute_exceptions_summary)
- `ignore_exception`: `Boolean` (relation=Ignore Exceptions)
- `main_exception_id`: `Many2one` (relation=exception.rule, compute=_compute_main_error)

### Non-persisted fields
- _none_

## base.exception.method

- Module: `base_exception`
- Model type: `AbstractModel`
- Table: `base_exception_method`

### Persisted fields

### Non-persisted fields
- _none_

## base.exception.test.purchase

- Module: `base_exception`
- Model type: `Model`
- Table: `base_exception_test_purchase`
- _inherit: `base.exception`
- Python constraints:
  - `test_purchase_check_exception`

### Persisted fields
- `active`: `Boolean`
- `amount_total`: `Float` (compute=_compute_amount_total)
- `name`: `Char` (required)
- `partner_id`: `Many2one` (relation=res.partner)
- `state`: `Selection`
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- `line_ids`: `One2many` (relation=base.exception.test.purchase.line)

## base.exception.test.purchase.line

- Module: `base_exception`
- Model type: `Model`
- Table: `base_exception_test_purchase_line`

### Persisted fields
- `amount`: `Float`
- `lead_id`: `Many2one` (relation=base.exception.test.purchase, ondelete=cascade)
- `name`: `Char`
- `qty`: `Float`

### Non-persisted fields
- _none_

## base.sequence.tester

- Module: `base_sequence_option`
- Model type: `Model`
- Table: `base_sequence_tester`

### Persisted fields
- `name`: `Char`
- `test_type`: `Selection`

### Non-persisted fields
- _none_

## bir.alphalist

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_alphalist`
- _inherit: `mail.thread`

### Persisted fields
- `company_id`: `Many2one` (relation=res.company, required)
- `currency_id`: `Many2one` (relation=res.currency)
- `fiscal_year`: `Integer` (required)
- `form_type`: `Selection` (required)
- `name`: `Char` (required)
- `state`: `Selection`
- `total_gross`: `Monetary` (compute=_compute_totals)
- `total_wht`: `Monetary` (compute=_compute_totals)

### Non-persisted fields
- `line_ids`: `One2many` (relation=bir.alphalist.line)

## bir.alphalist.line

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_alphalist_line`

### Persisted fields
- `alphalist_id`: `Many2one` (relation=bir.alphalist, required, ondelete=cascade)
- `currency_id`: `Many2one` (relation=res.currency, related=alphalist_id.currency_id)
- `gross_income`: `Monetary`
- `income_type`: `Selection`
- `partner_id`: `Many2one` (relation=res.partner, required)
- `tin`: `Char` (related=partner_id.tin)
- `wht_amount`: `Monetary`

### Non-persisted fields
- _none_

## bir.filing.deadline

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_filing_deadline`

### Persisted fields
- `company_id`: `Many2one` (relation=res.company, required)
- `deadline_date`: `Date` (required)
- `form_type`: `Selection` (required)
- `name`: `Char` (required)
- `period_month`: `Integer`
- `period_year`: `Integer`
- `reminder_date`: `Date` (compute=_compute_reminder_date)
- `return_id`: `Many2one` (relation=bir.tax.return)
- `state`: `Selection` (compute=_compute_state)

### Non-persisted fields
- _none_

## bir.return

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `bir_return`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `bir_reference`: `Char`
- `company_id`: `Many2one` (relation=res.company, required)
- `currency_id`: `Many2one` (relation=res.currency)
- `exempt_sales`: `Monetary`
- `filed_by`: `Many2one` (relation=res.users)
- `filed_date`: `Datetime`
- `form_type`: `Selection` (required)
- `input_vat`: `Monetary`
- `interest`: `Monetary`
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `output_vat`: `Monetary`
- `payment_date`: `Date`
- `payment_reference`: `Char`
- `penalty`: `Monetary`
- `period_end`: `Date` (required)
- `period_start`: `Date` (required)
- `state`: `Selection`
- `task_id`: `Many2one` (relation=finance.task)
- `tax_base`: `Monetary`
- `tax_credits`: `Monetary`
- `tax_due`: `Monetary`
- `tax_payable`: `Monetary` (compute=_compute_tax_payable)
- `total_due`: `Monetary` (compute=_compute_total_due)
- `total_payments`: `Monetary`
- `total_wht`: `Monetary`
- `vatable_sales`: `Monetary`
- `zero_rated_sales`: `Monetary`

### Non-persisted fields
- `line_ids`: `One2many` (relation=bir.return.line)

## bir.return.line

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `bir_return_line`

### Persisted fields
- `amount`: `Monetary`
- `currency_id`: `Many2one` (related=return_id.currency_id)
- `description`: `Char`
- `move_id`: `Many2one` (relation=account.move)
- `partner_id`: `Many2one` (relation=res.partner)
- `return_id`: `Many2one` (relation=bir.return, required, ondelete=cascade)
- `sequence`: `Integer`
- `tax_amount`: `Monetary`
- `tin`: `Char` (related=partner_id.tin)

### Non-persisted fields
- _none_

## bir.tax.return

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_tax_return`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `bir_reference`: `Char`
- `company_id`: `Many2one` (relation=res.company, required)
- `currency_id`: `Many2one` (relation=res.currency)
- `days_until_due`: `Integer` (compute=_compute_days_until_due)
- `due_date`: `Date` (compute=_compute_due_date)
- `filed_by`: `Many2one` (relation=res.users)
- `filed_date`: `Datetime`
- `form_type`: `Selection` (required)
- `frequency`: `Selection` (compute=_compute_frequency)
- `interest`: `Monetary`
- `is_overdue`: `Boolean` (compute=_compute_days_until_due)
- `name`: `Char` (required)
- `notes`: `Text`
- `payment_date`: `Date`
- `payment_reference`: `Char`
- `penalty`: `Monetary`
- `period_end`: `Date` (required)
- `period_start`: `Date` (required)
- `state`: `Selection`
- `tax_base`: `Monetary`
- `tax_category`: `Selection` (compute=_compute_tax_category)
- `tax_credits`: `Monetary`
- `tax_due`: `Monetary`
- `tax_payable`: `Monetary` (compute=_compute_tax_payable)
- `total_amount_due`: `Monetary` (compute=_compute_total_amount_due)

### Non-persisted fields
- `line_ids`: `One2many` (relation=bir.tax.return.line)

## bir.tax.return.line

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_tax_return_line`

### Persisted fields
- `currency_id`: `Many2one` (relation=res.currency, related=return_id.currency_id)
- `description`: `Char` (required)
- `move_id`: `Many2one` (relation=account.move)
- `partner_id`: `Many2one` (relation=res.partner)
- `return_id`: `Many2one` (relation=bir.tax.return, required, ondelete=cascade)
- `sequence`: `Integer`
- `tax_amount`: `Monetary`
- `tax_base`: `Monetary`
- `tax_rate`: `Float`
- `tin`: `Char` (related=partner_id.tin)

### Non-persisted fields
- _none_

## bir.vat.line

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_vat_line`

### Persisted fields
- `amount_untaxed`: `Monetary`
- `currency_id`: `Many2one` (relation=res.currency, related=return_id.currency_id)
- `invoice_date`: `Date` (related=invoice_id.invoice_date)
- `invoice_id`: `Many2one` (relation=account.move)
- `line_type`: `Selection` (required)
- `partner_id`: `Many2one` (relation=res.partner)
- `return_id`: `Many2one` (relation=bir.vat.return, required, ondelete=cascade)
- `tin`: `Char` (related=partner_id.tin)
- `vat_amount`: `Monetary`
- `vat_category`: `Selection`

### Non-persisted fields
- _none_

## bir.vat.return

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_vat_return`
- _inherit: `bir.tax.return`

### Persisted fields
- `excess_input_vat`: `Monetary` (compute=_compute_net_vat)
- `excess_input_vat_previous`: `Monetary`
- `exempt_sales`: `Monetary`
- `importations`: `Monetary`
- `net_vat_payable`: `Monetary` (compute=_compute_net_vat)
- `output_vat`: `Monetary` (compute=_compute_output_vat)
- `purchase_of_services`: `Monetary`
- `total_input_vat`: `Monetary` (compute=_compute_total_input_vat)
- `total_sales`: `Monetary` (compute=_compute_total_sales)
- `vatable_purchases`: `Monetary`
- `vatable_sales`: `Monetary`
- `zero_rated_sales`: `Monetary`

### Non-persisted fields
- _none_

## bir.withholding.line

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_withholding_line`

### Persisted fields
- `currency_id`: `Many2one` (relation=res.currency, related=return_id.currency_id)
- `gross_income`: `Monetary`
- `income_type`: `Selection`
- `move_id`: `Many2one` (relation=account.move)
- `partner_id`: `Many2one` (relation=res.partner)
- `payslip_id`: `Many2one` (relation=hr.payslip)
- `return_id`: `Many2one` (relation=bir.withholding.return, required, ondelete=cascade)
- `tin`: `Char` (related=partner_id.tin)
- `wht_amount`: `Monetary`
- `wht_rate`: `Float`

### Non-persisted fields
- _none_

## bir.withholding.return

- Module: `ipai_bir_tax_compliance`
- Model type: `Model`
- Table: `bir_withholding_return`
- _inherit: `bir.tax.return`

### Persisted fields
- `compensation_tax_withheld`: `Monetary`
- `employee_count`: `Integer`
- `expanded_wht_amount`: `Monetary`
- `final_wht_amount`: `Monetary`
- `taxable_compensation`: `Monetary`
- `total_compensation`: `Monetary`
- `total_payments`: `Monetary`
- `withholding_type`: `Selection` (required)

### Non-persisted fields
- `line_ids`: `One2many` (relation=bir.withholding.line)

## cleanup.create_indexes.line

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_create_indexes_line`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `field_id`: `Many2one` (relation=ir.model.fields, required)
- `purged`: `Boolean` (relation=Created)
- `wizard_id`: `Many2one` (relation=cleanup.create_indexes.wizard)

### Non-persisted fields
- _none_

## cleanup.create_indexes.wizard

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_create_indexes_wizard`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.create_indexes.line)

## cleanup.purge.line

- Module: `database_cleanup`
- Model type: `AbstractModel`
- Table: `cleanup_purge_line`

### Persisted fields
- `name`: `Char`
- `purged`: `Boolean`
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard)

### Non-persisted fields
- _none_

## cleanup.purge.line.column

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_column`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `model_id`: `Many2one` (relation=ir.model, required, ondelete=CASCADE)
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.column)

### Non-persisted fields
- _none_

## cleanup.purge.line.data

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_data`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `data_id`: `Many2one` (relation=ir.model.data)
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.data)

### Non-persisted fields
- _none_

## cleanup.purge.line.field

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_field`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `field_id`: `Many2one`
- `model_id`: `Many2one` (related=field_id.model_id)
- `model_name`: `Char` (related=model_id.model)
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.field)

### Non-persisted fields
- _none_

## cleanup.purge.line.menu

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_menu`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `menu_id`: `Many2one` (relation=ir.ui.menu)
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.menu)

### Non-persisted fields
- _none_

## cleanup.purge.line.model

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_model`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.model)

### Non-persisted fields
- _none_

## cleanup.purge.line.module

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_module`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.module)

### Non-persisted fields
- _none_

## cleanup.purge.line.table

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_line_table`
- _inherit: `cleanup.purge.line`

### Persisted fields
- `table_type`: `Selection`
- `wizard_id`: `Many2one` (relation=cleanup.purge.wizard.table)

### Non-persisted fields
- _none_

## cleanup.purge.wizard

- Module: `database_cleanup`
- Model type: `AbstractModel`
- Table: `cleanup_purge_wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line)

## cleanup.purge.wizard.column

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_column`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.column)

## cleanup.purge.wizard.data

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_data`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.data)

## cleanup.purge.wizard.field

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_field`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.field)

## cleanup.purge.wizard.menu

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_menu`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.menu)

## cleanup.purge.wizard.model

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_model`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.model)

## cleanup.purge.wizard.module

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_module`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.module)

## cleanup.purge.wizard.table

- Module: `database_cleanup`
- Model type: `TransientModel`
- Table: `cleanup_purge_wizard_table`
- _inherit: `cleanup.purge.wizard`

### Persisted fields

### Non-persisted fields
- `purge_line_ids`: `One2many` (relation=cleanup.purge.line.table)

## close.approval.gate

- Module: `ipai`
- Model type: `Model`
- Table: `close_approval_gate`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `actual_value`: `Float`
- `approved_by`: `Many2one` (relation=res.users)
- `approved_date`: `Datetime`
- `approver_id`: `Many2one` (relation=res.users)
- `block_reason`: `Text`
- `company_id`: `Many2one` (relation=res.company, related=cycle_id.company_id)
- `cycle_id`: `Many2one` (relation=close.cycle, required, index, ondelete=cascade)
- `gate_type`: `Selection` (required)
- `name`: `Char` (required)
- `notes`: `Html`
- `sequence`: `Integer`
- `state`: `Selection` (required)
- `template_id`: `Many2one` (relation=close.approval.gate.template)
- `threshold_value`: `Float`

### Non-persisted fields
- _none_

## close.approval.gate.template

- Module: `ipai`
- Model type: `Model`
- Table: `close_approval_gate_template`

### Persisted fields
- `a1_check_id`: `Many2one` (relation=a1.check)
- `active`: `Boolean`
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `description`: `Html`
- `gate_type`: `Selection` (required)
- `name`: `Char` (required)
- `pass_criteria`: `Text`
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## close.cycle

- Module: `ipai`
- Model type: `Model`
- Table: `close_cycle`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `period_uniq`: `unique(period_start, period_end, company_id)` (A cycle for this period already exists.)
  - `period_uniq`: `unique(period_start, period_end, company_id)` (A cycle for this period already exists.)

### Persisted fields
- `a1_tasklist_id`: `Many2one` (relation=a1.tasklist)
- `company_id`: `Many2one` (relation=res.company, required)
- `exception_count`: `Integer` (compute=_compute_exception_count)
- `gates_ready`: `Boolean` (compute=_compute_gates_ready)
- `name`: `Char` (required)
- `notes`: `Html`
- `open_exception_count`: `Integer` (compute=_compute_exception_count)
- `period_end`: `Date` (required)
- `period_label`: `Char` (compute=_compute_period_label)
- `period_start`: `Date` (required)
- `progress`: `Float` (compute=_compute_task_stats)
- `state`: `Selection` (required)
- `task_count`: `Integer` (compute=_compute_task_stats)
- `task_done_count`: `Integer` (compute=_compute_task_stats)
- `webhook_url`: `Char`

### Non-persisted fields
- `exception_ids`: `One2many` (relation=close.exception)
- `gate_ids`: `One2many` (relation=close.approval.gate)
- `task_ids`: `One2many` (relation=close.task)

## close.exception

- Module: `ipai`
- Model type: `Model`
- Table: `close_exception`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `assigned_to`: `Many2one` (relation=res.users)
- `company_id`: `Many2one` (relation=res.company, related=cycle_id.company_id)
- `cycle_id`: `Many2one` (relation=close.cycle, required, index, ondelete=cascade)
- `description`: `Html`
- `escalated_to`: `Many2one` (relation=res.users)
- `escalation_count`: `Integer`
- `escalation_deadline`: `Datetime`
- `exception_type`: `Selection` (required)
- `last_escalated`: `Datetime`
- `name`: `Char` (required)
- `reported_by`: `Many2one` (relation=res.users)
- `resolution`: `Html`
- `resolved_by`: `Many2one` (relation=res.users)
- `resolved_date`: `Datetime`
- `severity`: `Selection` (required)
- `state`: `Selection` (required)
- `task_id`: `Many2one` (relation=close.task, index, ondelete=set null)

### Non-persisted fields
- _none_

## close.task

- Module: `ipai`
- Model type: `Model`
- Table: `close_task`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `a1_task_id`: `Many2one` (relation=a1.task)
- `approval_deadline`: `Date`
- `approval_done_by`: `Many2one` (relation=res.users)
- `approval_done_date`: `Datetime`
- `approver_id`: `Many2one` (relation=res.users)
- `category_id`: `Many2one` (relation=close.task.category)
- `checklist_progress`: `Float` (compute=_compute_checklist_progress)
- `company_id`: `Many2one` (relation=res.company, related=cycle_id.company_id)
- `cycle_id`: `Many2one` (relation=close.cycle, required, index, ondelete=cascade)
- `external_key`: `Char` (index)
- `has_open_exceptions`: `Boolean` (compute=_compute_has_open_exceptions)
- `name`: `Char` (required)
- `notes`: `Html`
- `prep_deadline`: `Date`
- `prep_done_by`: `Many2one` (relation=res.users)
- `prep_done_date`: `Datetime`
- `preparer_id`: `Many2one` (relation=res.users)
- `review_deadline`: `Date`
- `review_done_by`: `Many2one` (relation=res.users)
- `review_done_date`: `Datetime`
- `reviewer_id`: `Many2one` (relation=res.users)
- `sequence`: `Integer`
- `state`: `Selection` (required)
- `template_id`: `Many2one` (relation=close.task.template)

### Non-persisted fields
- `checklist_ids`: `One2many` (relation=close.task.checklist)
- `exception_ids`: `One2many` (relation=close.exception)

## close.task.category

- Module: `ipai`
- Model type: `Model`
- Table: `close_task_category`
- SQL constraints:
  - `code_uniq`: `unique(code, company_id)` (Category code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Category code must be unique per company.)

### Persisted fields
- `a1_workstream_id`: `Many2one` (relation=a1.workstream)
- `active`: `Boolean`
- `code`: `Char` (required, index)
- `color`: `Integer`
- `company_id`: `Many2one` (relation=res.company, required)
- `description`: `Text`
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- `template_ids`: `One2many` (relation=close.task.template)

## close.task.checklist

- Module: `ipai`
- Model type: `Model`
- Table: `close_task_checklist`

### Persisted fields
- `code`: `Char` (required)
- `done_by`: `Many2one` (relation=res.users)
- `done_date`: `Datetime`
- `instructions`: `Text`
- `is_done`: `Boolean`
- `is_required`: `Boolean`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `task_id`: `Many2one` (relation=close.task, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## close.task.template

- Module: `ipai`
- Model type: `Model`
- Table: `close_task_template`
- SQL constraints:
  - `code_uniq`: `unique(code, company_id)` (Template code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Template code must be unique per company.)

### Persisted fields
- `a1_template_id`: `Many2one` (relation=a1.template)
- `active`: `Boolean`
- `approval_days`: `Float`
- `approval_offset`: `Integer`
- `approver_id`: `Many2one` (relation=res.users)
- `approver_role`: `Selection`
- `category_id`: `Many2one` (relation=close.task.category, index, ondelete=cascade)
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `description`: `Html`
- `name`: `Char` (required)
- `prep_days`: `Float`
- `prep_offset`: `Integer`
- `preparer_id`: `Many2one` (relation=res.users)
- `preparer_role`: `Selection`
- `review_days`: `Float`
- `review_offset`: `Integer`
- `reviewer_id`: `Many2one` (relation=res.users)
- `reviewer_role`: `Selection`
- `sequence`: `Integer`

### Non-persisted fields
- `checklist_ids`: `One2many` (relation=close.task.template.checklist)

## close.task.template.checklist

- Module: `ipai`
- Model type: `Model`
- Table: `close_task_template_checklist`

### Persisted fields
- `code`: `Char` (required)
- `instructions`: `Text`
- `is_required`: `Boolean`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `template_id`: `Many2one` (relation=close.task.template, required, ondelete=cascade)

### Non-persisted fields
- _none_

## closing.period

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `closing_period`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `bir_tasks`: `Integer` (compute=_compute_task_stats)
- `company_id`: `Many2one` (relation=res.company, required)
- `completed_tasks`: `Integer` (compute=_compute_task_stats)
- `last_workday`: `Date` (compute=_compute_last_workday)
- `month_end_tasks`: `Integer` (compute=_compute_task_stats)
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `overdue_tasks`: `Integer` (compute=_compute_task_stats)
- `period_date`: `Date` (required)
- `period_month`: `Integer` (compute=_compute_period_parts)
- `period_year`: `Integer` (compute=_compute_period_parts)
- `progress`: `Float` (compute=_compute_task_stats)
- `state`: `Selection`
- `total_tasks`: `Integer` (compute=_compute_task_stats)

### Non-persisted fields
- `task_ids`: `One2many` (relation=finance.task)

## compliance.check

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `compliance_check`

### Persisted fields
- `actual_value`: `Float`
- `check_type`: `Selection` (required)
- `checked_by`: `Many2one` (relation=res.users)
- `checked_date`: `Datetime`
- `closing_id`: `Many2one` (relation=closing.period, required, ondelete=cascade)
- `expected_value`: `Float`
- `name`: `Char` (required)
- `result_text`: `Text`
- `sequence`: `Integer`
- `status`: `Selection`
- `tolerance`: `Float`
- `variance`: `Float` (compute=_compute_variance)

### Non-persisted fields
- _none_

## credit.statement.import

- Module: `account_move_base_import`
- Model type: `TransientModel`
- Table: `credit_statement_import`

### Persisted fields
- `commission_account_id`: `Many2one` (related=journal_id.commission_account_id)
- `file_name`: `Char`
- `input_statement`: `Binary` (required)
- `journal_id`: `Many2one` (required)
- `partner_id`: `Many2one` (related=journal_id.partner_id)
- `receivable_account_id`: `Many2one` (related=journal_id.receivable_account_id)

### Non-persisted fields
- _none_

## crm.lead

- Module: `ipai_crm_pipeline`
- Model type: `Model`
- Table: `crm_lead`
- _inherit: `crm.lead`

### Persisted fields
- `days_in_stage`: `Integer` (compute=_compute_days_in_stage)
- `last_call_date`: `Datetime`
- `last_meeting_date`: `Datetime`
- `stage_entry_date`: `Datetime`
- `stage_missing_fields`: `Char` (compute=_compute_stage_rule_validated)
- `stage_rule_validated`: `Boolean` (compute=_compute_stage_rule_validated)

### Non-persisted fields
- _none_

## crm.stage

- Module: `ipai_crm_pipeline`
- Model type: `Model`
- Table: `crm_stage`
- _inherit: `crm.stage`

### Persisted fields
- `ipai_automation_notes`: `Text`
- `ipai_enforce_rules`: `Boolean`
- `ipai_required_field_ids`: `Many2many` (relation=ir.model.fields)
- `ipai_sla_days`: `Integer`
- `ipai_stage_color`: `Char`
- `ipai_stage_icon`: `Char`

### Non-persisted fields
- _none_

## db.backup

- Module: `auto_backup`
- Model type: `Model`
- Table: `db_backup`
- _inherit: `mail.thread`
- SQL constraints:
  - `days_to_keep_positive`: `CHECK(days_to_keep >= 0)` (I cannot remove backups from the future. Ask Doc for that.)
  - `name_unique`: `UNIQUE(name)` (Cannot duplicate a configuration.)
- Python constraints:
  - `_check_folder`

### Persisted fields
- `backup_format`: `Selection`
- `days_to_keep`: `Integer` (required)
- `folder`: `Char` (required)
- `method`: `Selection`
- `name`: `Char` (compute=_compute_name)
- `sftp_host`: `Char` (relation=SFTP Server)
- `sftp_password`: `Char` (relation=SFTP Password)
- `sftp_port`: `Integer` (relation=SFTP Port)
- `sftp_private_key`: `Char` (relation=Private key location)
- `sftp_user`: `Char` (relation=Username in the SFTP Server)

### Non-persisted fields
- _none_

## detailed.activity.statement.wizard

- Module: `partner_statement`
- Model type: `TransientModel`
- Table: `detailed_activity_statement_wizard`
- _inherit: `activity.statement.wizard`

### Persisted fields
- `show_aging_buckets`: `Boolean`
- `show_balance`: `Boolean`

### Non-persisted fields
- _none_

## discuss.channel

- Module: `ipai_ask_ai`
- Model type: `Model`
- Table: `discuss_channel`
- _inherit: `discuss.channel`

### Persisted fields
- `is_ai_channel`: `Boolean`

### Non-persisted fields
- _none_

## exception.rule

- Module: `base_exception`
- Model type: `Model`
- Table: `exception_rule`
- _inherit: `exception.rule`
- Python constraints:
  - `check_exception_type_consistency`

### Persisted fields
- `active`: `Boolean`
- `code`: `Text` (relation=Python Code)
- `description`: `Text`
- `domain`: `Char`
- `exception_type`: `Selection` (required)
- `is_blocking`: `Boolean`
- `method`: `Selection`
- `model`: `Selection` (required)
- `name`: `Char` (relation=Exception Name, required)
- `sequence`: `Integer`
- `test_purchase_ids`: `Many2many` (relation=base.exception.test.purchase)

### Non-persisted fields
- _none_

## exception.rule.confirm

- Module: `base_exception`
- Model type: `AbstractModel`
- Table: `exception_rule_confirm`

### Persisted fields
- `exception_ids`: `Many2many` (relation=exception.rule)
- `ignore`: `Boolean` (relation=Ignore Exceptions)
- `related_model_id`: `Many2one` (relation=base.exception)

### Non-persisted fields
- _none_

## exception.rule.confirm.test.purchase

- Module: `base_exception`
- Model type: `TransientModel`
- Table: `exception_rule_confirm_test_purchase`
- _inherit: `exception.rule.confirm`

### Persisted fields
- `related_model_id`: `Many2one` (relation=base.exception.test.purchase)

### Non-persisted fields
- _none_

## export.xlsx.wizard

- Module: `excel_import_export`
- Model type: `TransientModel`
- Table: `export_xlsx_wizard`

### Persisted fields
- `data`: `Binary`
- `name`: `Char`
- `res_ids`: `Char` (required)
- `res_model`: `Char` (required)
- `state`: `Selection`
- `template_id`: `Many2one` (relation=xlsx.template, required, ondelete=cascade)

### Non-persisted fields
- _none_

## fetchmail.attach.mail.manually

- Module: `fetchmail_attach_from_folder`
- Model type: `TransientModel`
- Table: `fetchmail_attach_mail_manually`

### Persisted fields
- `folder_id`: `Many2one`
- `name`: `Char`

### Non-persisted fields
- `mail_ids`: `One2many` (relation=fetchmail.attach.mail.manually.mail)

## fetchmail.attach.mail.manually.mail

- Module: `fetchmail_attach_from_folder`
- Model type: `TransientModel`
- Table: `fetchmail_attach_mail_manually_mail`

### Persisted fields
- `body`: `Html`
- `date`: `Datetime`
- `email_from`: `Char` (relation=From)
- `msgid`: `Char` (relation=Message id)
- `object_id`: `Reference`
- `subject`: `Char`
- `wizard_id`: `Many2one` (relation=fetchmail.attach.mail.manually)

### Non-persisted fields
- _none_

## fetchmail.server

- Module: `fetchmail_attach_from_folder`
- Model type: `Model`
- Table: `fetchmail_server`
- _inherit: `fetchmail.server`

### Persisted fields
- `cleanup_days`: `Integer`
- `cleanup_folder`: `Char`
- `error_notice_template_id`: `Many2one` (relation=mail.template)
- `folders_available`: `Text` (compute=_compute_folders_available)
- `folders_only`: `Boolean`
- `object_id`: `Many2one`
- `purge_days`: `Integer`
- `server_type`: `Selection`

### Non-persisted fields
- `folder_ids`: `One2many`

## fetchmail.server.folder

- Module: `fetchmail_attach_from_folder`
- Model type: `Model`
- Table: `fetchmail_server_folder`

### Persisted fields
- `action_id`: `Many2one`
- `active`: `Boolean`
- `archive_path`: `Char`
- `delete_matching`: `Boolean` (relation=Delete matches)
- `domain`: `Char`
- `fetch_unseen_only`: `Boolean`
- `flag_nonmatching`: `Boolean`
- `mail_field`: `Char` (relation=Field (email))
- `match_algorithm`: `Selection` (required)
- `match_first`: `Boolean` (relation=Use 1st match)
- `model_field`: `Char` (relation=Field (model))
- `model_id`: `Many2one` (required, ondelete=cascade)
- `model_order`: `Char` (relation=Order (model))
- `msg_state`: `Selection`
- `path`: `Char` (required)
- `sequence`: `Integer`
- `server_id`: `Many2one` (relation=fetchmail.server)
- `state`: `Selection` (required)

### Non-persisted fields
- _none_

## finance.bir.deadline

- Module: `ipai`
- Model type: `Model`
- Table: `finance_bir_deadline`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `active`: `Boolean`
- `deadline_date`: `Date` (required)
- `description`: `Text`
- `display_name`: `Char` (compute=_compute_display_name)
- `form_type`: `Selection`
- `name`: `Char` (required)
- `period_covered`: `Char`
- `responsible_approval_id`: `Many2one` (relation=ipai.finance.person)
- `responsible_prep_id`: `Many2one` (relation=ipai.finance.person)
- `responsible_review_id`: `Many2one` (relation=ipai.finance.person)
- `state`: `Selection`
- `target_payment_approval_date`: `Date` (compute=_compute_targets)
- `target_prep_date`: `Date` (compute=_compute_targets)
- `target_report_approval_date`: `Date` (compute=_compute_targets)

### Non-persisted fields
- _none_

## finance.ppm.bir.calendar

- Module: `ipai`
- Model type: `Model`
- Table: `finance_ppm_bir_calendar`
- SQL constraints:
  - `unique_form_period`: `UNIQUE(form_code, period)` (BIR form and period combination must be unique!)
  - `unique_form_period`: `UNIQUE(form_code, period)` (BIR form and period combination must be unique!)

### Persisted fields
- `description`: `Text`
- `filing_deadline`: `Date` (required)
- `form_code`: `Char` (required)
- `form_name`: `Char` (required)
- `period`: `Char` (required)
- `responsible_role`: `Char` (required)

### Non-persisted fields
- _none_

## finance.ppm.dashboard

- Module: `ipai`
- Model type: `Model`
- Table: `finance_ppm_dashboard`

### Persisted fields
- `failures_24h`: `Integer`
- `last_message`: `Text`
- `last_run_at`: `Datetime`
- `last_status`: `Selection`
- `name`: `Char` (required)
- `next_scheduled_at`: `Datetime`
- `sequence`: `Integer`
- `status_color`: `Selection` (compute=_compute_status_color)
- `total_runs`: `Integer`
- `workflow_code`: `Selection` (required, index)

### Non-persisted fields
- _none_

## finance.ppm.import.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `finance_ppm_import_wizard`

### Persisted fields
- `error_log`: `Text`
- `file_data`: `Binary` (required)
- `file_name`: `Char`
- `file_type`: `Selection` (compute=_compute_file_type)
- `import_summary`: `Text`
- `import_type`: `Selection` (required)
- `records_created`: `Integer`
- `records_failed`: `Integer`
- `records_skipped`: `Integer`
- `records_updated`: `Integer`
- `skip_header`: `Boolean`
- `state`: `Selection`
- `update_existing`: `Boolean`

### Non-persisted fields
- _none_

## finance.ppm.logframe

- Module: `ipai`
- Model type: `Model`
- Table: `finance_ppm_logframe`
- SQL constraints:
  - `unique_code`: `UNIQUE(code)` (Logframe code must be unique!)
  - `unique_code`: `UNIQUE(code)` (Logframe code must be unique!)
- Python constraints:
  - `_check_parent_hierarchy`

### Persisted fields
- `code`: `Char` (required)
- `description`: `Text`
- `kpi_baseline`: `Char`
- `kpi_measure`: `Char`
- `kpi_target`: `Char`
- `level`: `Selection` (required)
- `measurement_frequency`: `Selection`
- `name`: `Char` (required)
- `parent_id`: `Many2one` (relation=finance.ppm.logframe, ondelete=cascade)
- `parent_path`: `Char` (index)
- `responsible_role`: `Char`

### Non-persisted fields
- `child_ids`: `One2many` (relation=finance.ppm.logframe)

## finance.ppm.ph.holiday

- Module: `ipai`
- Model type: `Model`
- Table: `finance_ppm_ph_holiday`
- SQL constraints:
  - `unique_date_name`: `UNIQUE(date, name)` (Holiday date and name combination must be unique!)
  - `unique_date_name`: `UNIQUE(date, name)` (Holiday date and name combination must be unique!)

### Persisted fields
- `date`: `Date` (required)
- `description`: `Text`
- `holiday_type`: `Selection` (required)
- `is_nationwide`: `Boolean`
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## finance.ppm.tdi.audit

- Module: `ipai`
- Model type: `Model`
- Table: `finance_ppm_tdi_audit`

### Persisted fields
- `display_name`: `Char` (compute=_compute_display_name)
- `error_log`: `Text`
- `file_name`: `Char` (required)
- `has_errors`: `Boolean` (compute=_compute_has_errors)
- `import_date`: `Datetime` (required, index)
- `import_summary`: `Text`
- `import_type`: `Selection` (required, index)
- `records_created`: `Integer`
- `records_failed`: `Integer`
- `records_skipped`: `Integer`
- `records_updated`: `Integer`
- `state`: `Selection` (required, index)
- `success_rate`: `Float` (compute=_compute_success_rate)
- `total_records`: `Integer` (compute=_compute_total_records)
- `user_id`: `Many2one` (relation=res.users, required, ondelete=restrict)

### Non-persisted fields
- _none_

## finance.task

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `finance_task`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `approve_done`: `Boolean`
- `approve_done_by`: `Many2one` (relation=res.users)
- `approve_done_date`: `Datetime`
- `approve_due_date`: `Date`
- `approve_user_id`: `Many2one` (relation=res.users)
- `bir_form_type`: `Selection`
- `bir_reference`: `Char`
- `bir_return_id`: `Many2one` (relation=bir.return)
- `closing_id`: `Many2one` (relation=closing.period, required, ondelete=cascade)
- `company_id`: `Many2one` (related=closing_id.company_id)
- `days_overdue`: `Integer` (compute=_compute_overdue)
- `filed_date`: `Datetime`
- `filing_due_date`: `Date`
- `is_overdue`: `Boolean` (compute=_compute_overdue)
- `name`: `Char` (required)
- `notes`: `Text`
- `phase`: `Selection`
- `prep_done`: `Boolean`
- `prep_done_by`: `Many2one` (relation=res.users)
- `prep_done_date`: `Datetime`
- `prep_due_date`: `Date`
- `prep_user_id`: `Many2one` (relation=res.users)
- `review_done`: `Boolean`
- `review_done_by`: `Many2one` (relation=res.users)
- `review_done_date`: `Datetime`
- `review_due_date`: `Date`
- `review_user_id`: `Many2one` (relation=res.users)
- `sequence`: `Integer`
- `state`: `Selection` (compute=_compute_state)
- `task_type`: `Selection` (required)
- `template_id`: `Many2one` (relation=finance.task.template)

### Non-persisted fields
- _none_

## finance.task.template

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `finance_task_template`

### Persisted fields
- `active`: `Boolean`
- `approve_day_offset`: `Integer`
- `approve_user_id`: `Many2one` (relation=res.users)
- `bir_form_type`: `Selection`
- `depends_on_ids`: `Many2many` (relation=finance.task.template)
- `description`: `Html`
- `filing_day_offset`: `Integer`
- `frequency`: `Selection`
- `name`: `Char` (required)
- `oca_module`: `Char`
- `odoo_model`: `Char`
- `phase`: `Selection`
- `prep_day_offset`: `Integer`
- `prep_user_id`: `Many2one` (relation=res.users)
- `review_day_offset`: `Integer`
- `review_user_id`: `Many2one` (relation=res.users)
- `sequence`: `Integer`
- `task_count`: `Integer` (compute=_compute_task_count)
- `task_type`: `Selection` (required)

### Non-persisted fields
- _none_

## fs.storage

- Module: `attachment_synchronize`
- Model type: `Model`
- Table: `fs_storage`
- _inherit: `fs.storage`

### Persisted fields
- `export_task_count`: `Integer` (relation=Export Tasks, compute=_compute_export_task_count)
- `import_task_count`: `Integer` (relation=Import Tasks, compute=_compute_import_task_count)

### Non-persisted fields
- `synchronize_task_ids`: `One2many` (relation=attachment.synchronize.task)

## general.ledger.report.wizard

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `general_ledger_report_wizard`
- _inherit: `account_financial_report_abstract_wizard`
- Python constraints:
  - `_check_company_id_date_range_id`

### Persisted fields
- `account_code_from`: `Many2one`
- `account_code_to`: `Many2one`
- `account_ids`: `Many2many`
- `account_journal_ids`: `Many2many`
- `centralize`: `Boolean`
- `cost_center_ids`: `Many2many`
- `date_from`: `Date` (required)
- `date_range_id`: `Many2one`
- `date_to`: `Date` (required)
- `domain`: `Char`
- `foreign_currency`: `Boolean`
- `fy_start_date`: `Date` (compute=_compute_fy_start_date)
- `grouped_by`: `Selection` (required)
- `hide_account_at_0`: `Boolean`
- `only_one_unaffected_earnings_account`: `Boolean`
- `partner_ids`: `Many2many`
- `payable_accounts_only`: `Boolean`
- `receivable_accounts_only`: `Boolean`
- `show_cost_center`: `Boolean`
- `target_move`: `Selection` (required)
- `unaffected_earnings_account`: `Many2one` (compute=_compute_unaffected_earnings_account)

### Non-persisted fields
- _none_

## hr.employee

- Module: `ipai`
- Model type: `Model`
- Table: `hr_employee`
- _inherit: `hr.employee, master.control.mixin`

### Persisted fields
- `x_master_control_offboarded`: `Boolean`
- `x_master_control_onboarded`: `Boolean`

### Non-persisted fields
- _none_

## hr.expense

- Module: `ipai`
- Model type: `Model`
- Table: `hr_expense`
- _inherit: `hr.expense, master.control.mixin`
- Python constraints:
  - `_check_project_required`
  - `_check_travel_request_consistency`

### Persisted fields
- `project_id`: `Many2one` (relation=project.project)
- `requires_project`: `Boolean` (compute=_compute_requires_project)
- `travel_request_id`: `Many2one` (relation=ipai.travel.request)
- `x_master_control_submitted`: `Boolean`

### Non-persisted fields
- _none_

## hr.timesheet.switch

- Module: `project_timesheet_time_control`
- Model type: `TransientModel`
- Table: `hr_timesheet_switch`

### Persisted fields
- `analytic_line_id`: `Many2one`
- `company_id`: `Many2one` (required)
- `date_time`: `Datetime` (required)
- `date_time_end`: `Datetime`
- `name`: `Char` (required)
- `project_id`: `Many2one` (compute=_compute_project_id)
- `running_timer_duration`: `Float` (compute=_compute_running_timer_duration)
- `running_timer_id`: `Many2one` (ondelete=cascade)
- `running_timer_start`: `Datetime` (related=running_timer_id.date_time)
- `task_id`: `Many2one` (compute=_compute_task_id, index)

### Non-persisted fields
- _none_

## hr.timesheet.time_control.mixin

- Module: `project_timesheet_time_control`
- Model type: `AbstractModel`
- Table: `hr_timesheet_time_control_mixin`

### Persisted fields
- `show_time_control`: `Selection` (compute=_compute_show_time_control)

### Non-persisted fields
- _none_

## iap.account

- Module: `iap_alternative_provider`
- Model type: `Model`
- Table: `iap_account`
- _inherit: `iap.account`

### Persisted fields
- `provider`: `Selection` (required)

### Non-persisted fields
- _none_

## import.xlsx.wizard

- Module: `excel_import_export`
- Model type: `TransientModel`
- Table: `import_xlsx_wizard`

### Persisted fields
- `attachment_ids`: `Many2many` (relation=ir.attachment, required)
- `datas`: `Binary` (related=template_id.datas)
- `filename`: `Char` (relation=Import File Name)
- `fname`: `Char` (related=template_id.fname)
- `import_file`: `Binary`
- `res_id`: `Integer`
- `res_model`: `Char`
- `state`: `Selection`
- `template_id`: `Many2one` (relation=xlsx.template, required, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.ai.studio.mixin

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ipai_ai_studio_mixin`

### Persisted fields

### Non-persisted fields
- _none_

## ipai.approval.mixin

- Module: `ipai_platform_approvals`
- Model type: `AbstractModel`
- Table: `ipai_approval_mixin`

### Persisted fields
- `approval_notes`: `Text`
- `approval_requested`: `Boolean`
- `approval_requested_by`: `Many2one` (relation=res.users)
- `approval_requested_date`: `Datetime`
- `current_approver_id`: `Many2one` (relation=res.users, compute=_compute_current_approver)

### Non-persisted fields
- _none_

## ipai.ask.ai.service

- Module: `ipai_ask_ai`
- Model type: `TransientModel`
- Table: `ipai_ask_ai_service`

### Persisted fields

### Non-persisted fields
- _none_

## ipai.asset

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_asset`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `active_checkout_id`: `Many2one` (relation=ipai.asset.checkout, compute=_compute_active_checkout)
- `barcode`: `Char`
- `category_id`: `Many2one` (relation=ipai.asset.category, required)
- `code`: `Char`
- `currency_id`: `Many2one` (relation=res.currency)
- `current_value`: `Monetary` (compute=_compute_current_value)
- `custodian_id`: `Many2one` (relation=hr.employee)
- `description`: `Text`
- `image`: `Image`
- `location_id`: `Many2one` (relation=stock.location)
- `name`: `Char` (required)
- `purchase_date`: `Date`
- `purchase_value`: `Monetary`
- `state`: `Selection`

### Non-persisted fields
- `checkout_ids`: `One2many` (relation=ipai.asset.checkout)
- `reservation_ids`: `One2many` (relation=ipai.asset.reservation)

## ipai.asset.category

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_asset_category`

### Persisted fields
- `allow_reservations`: `Boolean`
- `asset_count`: `Integer` (compute=_compute_asset_count)
- `code`: `Char` (required)
- `description`: `Text`
- `max_checkout_days`: `Integer`
- `name`: `Char` (required)
- `requires_approval`: `Boolean`
- `sequence`: `Integer`

### Non-persisted fields
- `asset_ids`: `One2many` (relation=ipai.asset)

## ipai.asset.checkout

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_asset_checkout`
- _inherit: `mail.activity.mixin, mail.thread`
- Python constraints:
  - `_check_asset_available`

### Persisted fields
- `actual_return_date`: `Datetime`
- `approval_date`: `Datetime`
- `approved_by`: `Many2one` (relation=res.users)
- `asset_id`: `Many2one` (relation=ipai.asset, required)
- `checkout_date`: `Datetime` (required)
- `checkout_notes`: `Text`
- `condition_on_return`: `Selection`
- `employee_id`: `Many2one` (relation=hr.employee, required)
- `expected_return_date`: `Date`
- `name`: `Char` (compute=_compute_name)
- `return_notes`: `Text`
- `state`: `Selection`

### Non-persisted fields
- _none_

## ipai.asset.reservation

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_asset_reservation`
- _inherit: `mail.thread`
- Python constraints:
  - `_check_dates`
  - `_check_overlap`

### Persisted fields
- `asset_id`: `Many2one` (relation=ipai.asset, required)
- `employee_id`: `Many2one` (relation=hr.employee, required)
- `end_date`: `Date` (required)
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `start_date`: `Date` (required)
- `state`: `Selection`

### Non-persisted fields
- _none_

## ipai.audit.log

- Module: `ipai_platform_audit`
- Model type: `Model`
- Table: `ipai_audit_log`

### Persisted fields
- `action`: `Selection` (required)
- `display_name`: `Char` (compute=_compute_display_name)
- `field_name`: `Char`
- `new_value`: `Text`
- `old_value`: `Text`
- `res_id`: `Integer` (required, index)
- `res_model`: `Char` (required, index)
- `res_name`: `Char`
- `user_id`: `Many2one` (relation=res.users, required)

### Non-persisted fields
- _none_

## ipai.audit.mixin

- Module: `ipai_platform_audit`
- Model type: `AbstractModel`
- Table: `ipai_audit_mixin`

### Persisted fields
- `audit_log_count`: `Integer` (compute=_compute_audit_log_count)

### Non-persisted fields
- `audit_log_ids`: `One2many` (relation=ipai.audit.log)

## ipai.bir.dat.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_bir_dat_wizard`

### Persisted fields
- `currency_id`: `Many2one` (relation=res.currency)
- `date_end`: `Date` (required)
- `date_start`: `Date` (required)
- `file_data`: `Binary` (relation=DAT File)
- `file_name`: `Char` (relation=File Name)
- `record_count`: `Integer` (relation=Records Processed)
- `report_type`: `Selection` (required)
- `state`: `Selection`
- `total_amount`: `Monetary` (relation=Total Income)
- `total_tax`: `Monetary` (relation=Total Tax Withheld)

### Non-persisted fields
- _none_

## ipai.bir.form.schedule

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_bir_form_schedule`
- _inherit: `ipai.bir.form.schedule, mail.activity.mixin, mail.thread`

### Persisted fields
- `approval_date`: `Date`
- `bir_deadline`: `Date` (required)
- `filing_date`: `Date`
- `form_code`: `Char` (required)
- `last_reminder_sent`: `Datetime`
- `period`: `Char` (required)
- `prep_date`: `Date`
- `reminder_count`: `Integer`
- `responsible_approval_id`: `Many2one` (relation=ipai.finance.person)
- `responsible_prep_id`: `Many2one` (relation=ipai.finance.person)
- `responsible_review_id`: `Many2one` (relation=ipai.finance.person)
- `review_date`: `Date`
- `status`: `Selection`

### Non-persisted fields
- `step_ids`: `One2many` (relation=ipai.bir.process.step)

## ipai.bir.generator

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ipai_bir_generator`

### Persisted fields

### Non-persisted fields
- _none_

## ipai.bir.process.step

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_bir_process_step`

### Persisted fields
- `detail`: `Text`
- `person_id`: `Many2one` (relation=ipai.finance.person)
- `role`: `Char`
- `schedule_id`: `Many2one` (relation=ipai.bir.form.schedule, ondelete=cascade)
- `step_no`: `Integer` (required)
- `target_offset`: `Integer`
- `title`: `Char` (required)

### Non-persisted fields
- _none_

## ipai.bir.schedule.item

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_bir_schedule_item`
- SQL constraints:
  - `bir_schedule_unique`: `unique(bir_form, period_covered, deadline)` (BIR schedule item must be unique per form/period/deadline!)
  - `bir_schedule_unique`: `unique(bir_form, period_covered, deadline)` (BIR schedule item must be unique per form/period/deadline!)

### Persisted fields
- `active`: `Boolean`
- `bir_form`: `Char` (required, index)
- `deadline`: `Date` (required, index)
- `im_xml_id`: `Char` (required)
- `period_covered`: `Char` (required, index)

### Non-persisted fields
- `step_ids`: `One2many` (relation=ipai.bir.schedule.step)

## ipai.bir.schedule.line

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_bir_schedule_line`
- SQL constraints:
  - `bir_sched_unique`: `unique(bir_form, period_label)` (BIR form+period must be unique.)
  - `bir_sched_unique`: `unique(bir_form, period_label)` (BIR form+period must be unique.)
- Python constraints:
  - `_check_dates`

### Persisted fields
- `approve_by_code`: `Char`
- `approve_due_date`: `Date`
- `bir_form`: `Char` (required, index)
- `deadline_date`: `Date` (required, index)
- `notes`: `Char`
- `period_label`: `Char` (required)
- `prep_by_code`: `Char`
- `prep_due_date`: `Date`
- `review_by_code`: `Char`
- `review_due_date`: `Date`

### Non-persisted fields
- _none_

## ipai.bir.schedule.step

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_bir_schedule_step`

### Persisted fields
- `activity_type`: `Selection` (required)
- `business_days_before`: `Integer`
- `item_id`: `Many2one` (relation=ipai.bir.schedule.item, required, ondelete=cascade)
- `on_or_before_deadline`: `Boolean`
- `role_code`: `Char`
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## ipai.close.generated.map

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_close_generated_map`
- SQL constraints:
  - `external_key_uniq`: `UNIQUE(external_key)` (External key must be unique (prevents duplicate task creation))
  - `external_key_uniq`: `UNIQUE(external_key)` (External key must be unique (prevents duplicate task creation))
  - `external_key_uniq`: `unique(external_key)` (External key must be unique.)
  - `external_key_uniq`: `unique(external_key)` (External key must be unique.)

### Persisted fields
- `external_key`: `Char` (required, index)
- `generation_run_id`: `Many2one` (relation=ipai.close.generation.run, required, index, ondelete=cascade)
- `operation`: `Selection` (required)
- `run_id`: `Many2one` (relation=ipai.close.generation.run, required, index, ondelete=cascade)
- `seed_hash`: `Char` (index)
- `seed_hash_at_generation`: `Char`
- `task_id`: `Many2one` (relation=project.task, required, index, ondelete=cascade)
- `template_id`: `Many2one` (relation=ipai.close.task.template, ondelete=set null)

### Non-persisted fields
- _none_

## ipai.close.generation.run

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_close_generation_run`

### Persisted fields
- `created_count`: `Integer`
- `cycle_code`: `Char` (required, index)
- `cycle_key`: `Char` (index)
- `cycle_type`: `Selection` (compute=_compute_cycle_type)
- `dry_run`: `Boolean`
- `duration_seconds`: `Integer` (compute=_compute_duration)
- `end_time`: `Datetime`
- `error_count`: `Integer` (compute=_compute_counts)
- `name`: `Char` (compute=_compute_name)
- `obsolete_marked_count`: `Integer`
- `period_end`: `Date` (required)
- `period_start`: `Date` (required)
- `project_id`: `Many2one` (relation=project.project)
- `report_json`: `Json`
- `report_status`: `Selection` (compute=_compute_report_status)
- `seed_id`: `Char` (required, index)
- `seed_version`: `Char`
- `start_time`: `Datetime`
- `status`: `Selection` (required)
- `task_count_created`: `Integer`
- `task_count_obsolete`: `Integer`
- `task_count_skipped`: `Integer`
- `task_count_updated`: `Integer`
- `unchanged_count`: `Integer`
- `unresolved_assignee_count`: `Integer`
- `updated_count`: `Integer`
- `user_id`: `Many2one` (relation=res.users)
- `warning_count`: `Integer` (compute=_compute_counts)

### Non-persisted fields
- `generated_map_ids`: `One2many` (relation=ipai.close.generated.map)
- `generated_task_ids`: `One2many` (relation=ipai.close.generated.map)

## ipai.close.generator

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_close_generator`

### Persisted fields
- `name`: `Char`

### Non-persisted fields
- _none_

## ipai.close.task.step

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_close_task_step`
- SQL constraints:
  - `unique_template_step`: `UNIQUE(template_id, step_code)` (Each template can only have one instance of each step code (PREP, REVIEW, APPROVAL, FILE_PAY))
  - `unique_template_step`: `UNIQUE(template_id, step_code)` (Each template can only have one instance of each step code (PREP, REVIEW, APPROVAL, FILE_PAY))

### Persisted fields
- `default_employee_code`: `Char`
- `sequence`: `Integer`
- `step_code`: `Selection` (required, index)
- `step_name`: `Char` (required)
- `template_id`: `Many2one` (relation=ipai.close.task.template, required, index, ondelete=cascade)
- `user_id`: `Many2one` (relation=res.users, compute=_compute_user)
- `x_legacy_template_code`: `Char`

### Non-persisted fields
- _none_

## ipai.close.task.template

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_close_task_template`
- SQL constraints:
  - `template_code_uniq`: `UNIQUE(template_code, template_version)` (Template code + version must be unique)
  - `template_code_uniq`: `UNIQUE(template_code, template_version)` (Template code + version must be unique)

### Persisted fields
- `category_code`: `Char` (index)
- `category_name`: `Char`
- `category_seq`: `Integer`
- `critical_path`: `Boolean`
- `cycle_code`: `Selection` (required, index)
- `duration_days`: `Integer`
- `employee_code`: `Char`
- `is_active`: `Boolean` (index)
- `offset_from_period_end`: `Integer`
- `phase_code`: `Char` (required, index)
- `phase_name`: `Char` (required)
- `phase_seq`: `Integer`
- `phase_type`: `Selection`
- `recurrence_rule`: `Char`
- `responsible_role`: `Char`
- `seed_hash`: `Char` (compute=_compute_seed_hash, index)
- `step_code`: `Selection` (index)
- `step_seq`: `Integer`
- `task_description`: `Text`
- `task_name_template`: `Char` (required)
- `template_code`: `Char` (required, index)
- `template_seq`: `Integer`
- `template_version`: `Char`
- `wbs_code_template`: `Char`
- `workstream_code`: `Char` (index)
- `workstream_name`: `Char`
- `workstream_seq`: `Integer`
- `x_legacy_migration`: `Boolean`

### Non-persisted fields
- `step_ids`: `One2many` (relation=ipai.close.task.step)

## ipai.convert.phases.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_convert_phases_wizard`

### Persisted fields
- `im1_keywords`: `Char`
- `im1_name`: `Char` (required)
- `im2_keywords`: `Char`
- `im2_name`: `Char` (required)
- `move_tasks_by_keyword`: `Boolean`
- `parent_project_id`: `Many2one` (relation=project.project, required)

### Non-persisted fields
- _none_

## ipai.directory.person

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_directory_person`
- SQL constraints:
  - `code_unique`: `unique(code)` (Directory code must be unique!)
  - `code_unique`: `unique(code)` (Directory code must be unique!)

### Persisted fields
- `active`: `Boolean`
- `code`: `Char` (required, index)
- `email`: `Char`
- `name`: `Char` (required)
- `role`: `Char`

### Non-persisted fields
- `user_id`: `Many2one` (relation=res.users, compute=_compute_user_id)

## ipai.equipment.asset

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_equipment_asset`

### Persisted fields
- `booking_count`: `Integer` (compute=_compute_booking_count)
- `category_id`: `Many2one` (relation=product.category)
- `company_id`: `Many2one` (relation=res.company)
- `condition`: `Selection` (required)
- `image_1920`: `Image` (relation=Image)
- `incident_count`: `Integer` (compute=_compute_incident_count)
- `location_id`: `Many2one` (relation=stock.location)
- `name`: `Char` (required)
- `product_id`: `Many2one` (relation=product.product)
- `serial_number`: `Char`
- `status`: `Selection` (required)

### Non-persisted fields
- _none_

## ipai.equipment.booking

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_equipment_booking`
- Python constraints:
  - `_check_booking_conflict`

### Persisted fields
- `asset_id`: `Many2one` (relation=ipai.equipment.asset, required)
- `borrower_id`: `Many2one` (relation=res.users, required)
- `end_datetime`: `Datetime` (required)
- `is_overdue`: `Boolean` (compute=_compute_is_overdue)
- `name`: `Char` (required)
- `project_id`: `Many2one` (relation=project.project)
- `start_datetime`: `Datetime` (required)
- `state`: `Selection` (required)

### Non-persisted fields
- _none_

## ipai.equipment.incident

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_equipment_incident`

### Persisted fields
- `asset_id`: `Many2one` (relation=ipai.equipment.asset, required)
- `booking_id`: `Many2one` (relation=ipai.equipment.booking)
- `description`: `Text`
- `name`: `Char` (required)
- `reported_by`: `Many2one` (relation=res.users, required)
- `severity`: `Selection` (required)
- `status`: `Selection` (required)

### Non-persisted fields
- _none_

## ipai.finance.bir_schedule

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_finance_bir_schedule`

### Persisted fields
- `approval_deadline`: `Date`
- `approval_task_id`: `Many2one` (relation=project.task)
- `approver_id`: `Many2one` (relation=res.users)
- `completion_pct`: `Float`
- `filing_deadline`: `Date` (required)
- `logframe_id`: `Many2one` (relation=ipai.finance.logframe)
- `name`: `Char` (required)
- `period_covered`: `Char`
- `prep_deadline`: `Date`
- `prep_task_id`: `Many2one` (relation=project.task)
- `review_deadline`: `Date`
- `review_task_id`: `Many2one` (relation=project.task)
- `reviewer_id`: `Many2one` (relation=res.users)
- `status`: `Selection` (required)
- `supervisor_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- _none_

## ipai.finance.directory

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_finance_directory`
- SQL constraints:
  - `code_uniq`: `unique(code)` (Directory code must be unique.)
  - `code_uniq`: `unique(code)` (Directory code must be unique.)
- Python constraints:
  - `_check_email`

### Persisted fields
- `active`: `Boolean`
- `code`: `Char` (required, index)
- `email`: `Char` (index)
- `name`: `Char` (required)
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- _none_

## ipai.finance.logframe

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_finance_logframe`

### Persisted fields
- `assumptions`: `Text`
- `code`: `Char`
- `indicators`: `Text`
- `level`: `Selection` (required)
- `means_of_verification`: `Text`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `task_count`: `Integer` (compute=_compute_task_count)

### Non-persisted fields
- `bir_schedule_ids`: `One2many` (relation=ipai.finance.bir_schedule)
- `task_ids`: `One2many` (relation=project.task)

## ipai.finance.person

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_finance_person`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `code_unique`: `unique(code)` (Personnel code must be unique!)
  - `code_unique`: `unique(code)` (Personnel code must be unique!)

### Persisted fields
- `code`: `Char` (required)
- `email`: `Char`
- `name`: `Char` (required)
- `role`: `Selection`
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- _none_

## ipai.finance.ppm.golive.checklist

- Module: `ipai_finance_ppm_golive`
- Model type: `Model`
- Table: `ipai_finance_ppm_golive_checklist`

### Persisted fields
- `completed_items`: `Integer` (compute=_compute_progress)
- `completion_pct`: `Float` (compute=_compute_progress)
- `create_date`: `Datetime`
- `created_by`: `Many2one` (relation=res.users)
- `director_id`: `Many2one` (relation=res.users)
- `director_notes`: `Text`
- `director_review_date`: `Datetime`
- `director_signoff_date`: `Datetime`
- `name`: `Char` (required)
- `section_ids`: `Many2many` (relation=ipai.finance.ppm.golive.section)
- `senior_supervisor_id`: `Many2one` (relation=res.users)
- `senior_supervisor_notes`: `Text`
- `senior_supervisor_review_date`: `Datetime`
- `state`: `Selection`
- `supervisor_id`: `Many2one` (relation=res.users)
- `supervisor_notes`: `Text`
- `supervisor_review_date`: `Datetime`
- `total_items`: `Integer` (compute=_compute_progress)
- `version`: `Char`
- `write_date`: `Datetime`

### Non-persisted fields
- _none_

## ipai.finance.ppm.golive.item

- Module: `ipai_finance_ppm_golive`
- Model type: `Model`
- Table: `ipai_finance_ppm_golive_item`

### Persisted fields
- `checked_by`: `Many2one` (relation=res.users)
- `checked_date`: `Datetime`
- `description`: `Text`
- `evidence_url`: `Char`
- `is_checked`: `Boolean`
- `is_critical`: `Boolean`
- `name`: `Char` (required)
- `notes`: `Text`
- `section_id`: `Many2one` (relation=ipai.finance.ppm.golive.section, required, ondelete=cascade)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## ipai.finance.ppm.golive.section

- Module: `ipai_finance_ppm_golive`
- Model type: `Model`
- Table: `ipai_finance_ppm_golive_section`

### Persisted fields
- `completed_items`: `Integer` (compute=_compute_progress)
- `completion_pct`: `Float` (compute=_compute_progress)
- `description`: `Text`
- `name`: `Char` (required)
- `section_type`: `Selection` (required)
- `sequence`: `Integer`
- `total_items`: `Integer` (compute=_compute_progress)

### Non-persisted fields
- `item_ids`: `One2many` (relation=ipai.finance.ppm.golive.item)

## ipai.finance.seed.service

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_finance_seed_service`

### Persisted fields

### Non-persisted fields
- _none_

## ipai.finance.seed.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_finance_seed_wizard`

### Persisted fields
- `strict`: `Boolean`

### Non-persisted fields
- _none_

## ipai.finance.task.template

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_finance_task_template`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `tmpl_name_unique`: `unique(name, category)` (Template name must be unique per category.)
  - `tmpl_name_unique`: `unique(name, category)` (Template name must be unique per category.)

### Persisted fields
- `active`: `Boolean`
- `anchor`: `Selection` (required)
- `approval_duration`: `Float`
- `approve_by_code`: `Char`
- `approved_by_id`: `Many2one` (relation=ipai.finance.person)
- `bir_form_id`: `Many2one` (relation=finance.bir.deadline)
- `category`: `Selection` (required, index)
- `day_of_month`: `Integer`
- `default_duration_days`: `Integer`
- `description`: `Text`
- `employee_code_id`: `Many2one` (relation=ipai.finance.person)
- `name`: `Char` (required)
- `offset_days`: `Integer`
- `prep_by_code`: `Char`
- `prep_duration`: `Float`
- `review_by_code`: `Char`
- `review_duration`: `Float`
- `reviewed_by_id`: `Many2one` (relation=ipai.finance.person)
- `sequence`: `Integer`
- `task_category`: `Selection` (index)
- `trigger_type`: `Selection` (required)

### Non-persisted fields
- _none_

## ipai.generate.bir.tasks.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_generate_bir_tasks_wizard`

### Persisted fields
- `date_from`: `Date`
- `date_to`: `Date`
- `dry_run`: `Boolean`
- `program_project_id`: `Many2one` (relation=project.project, required)

### Non-persisted fields
- _none_

## ipai.generate.im.projects.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_generate_im_projects_wizard`

### Persisted fields
- `create_bir_tasks`: `Boolean`
- `create_children`: `Boolean`
- `create_month_end_tasks`: `Boolean`
- `project_id`: `Many2one` (relation=project.project, required)

### Non-persisted fields
- _none_

## ipai.generate.month.end.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_generate_month_end_wizard`

### Persisted fields
- `anchor_date`: `Date` (required)
- `dry_run`: `Boolean`
- `program_project_id`: `Many2one` (relation=project.project, required)

### Non-persisted fields
- _none_

## ipai.grid.column

- Module: `ipai_grid_view`
- Model type: `Model`
- Table: `ipai_grid_column`

### Persisted fields
- `alignment`: `Selection`
- `cell_css_class`: `Char`
- `clickable`: `Boolean`
- `column_type`: `Selection`
- `css_class`: `Char`
- `currency_field`: `Char`
- `date_format`: `Char`
- `decimal_places`: `Integer`
- `display_name`: `Char` (compute=_compute_display_name)
- `editable`: `Boolean`
- `field_name`: `Char` (required)
- `field_type`: `Selection`
- `filterable`: `Boolean`
- `format_string`: `Char`
- `grid_view_id`: `Many2one` (relation=ipai.grid.view, required, ondelete=cascade)
- `header_css_class`: `Char`
- `is_action_column`: `Boolean`
- `is_avatar_column`: `Boolean`
- `is_primary`: `Boolean`
- `is_selection_column`: `Boolean`
- `label`: `Char`
- `max_width`: `Integer`
- `min_width`: `Integer`
- `resizable`: `Boolean`
- `searchable`: `Boolean`
- `sequence`: `Integer`
- `sortable`: `Boolean`
- `visible`: `Boolean`
- `widget_options`: `Text`
- `width`: `Integer`

### Non-persisted fields
- _none_

## ipai.grid.filter

- Module: `ipai_grid_view`
- Model type: `Model`
- Table: `ipai_grid_filter`

### Persisted fields
- `active`: `Boolean`
- `color`: `Selection`
- `condition_count`: `Integer` (compute=_compute_condition_count)
- `domain`: `Char`
- `filter_json`: `Text`
- `grid_view_id`: `Many2one` (relation=ipai.grid.view, ondelete=cascade)
- `icon`: `Char`
- `is_default`: `Boolean`
- `is_global`: `Boolean`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- _none_

## ipai.grid.filter.condition

- Module: `ipai_grid_view`
- Model type: `TransientModel`
- Table: `ipai_grid_filter_condition`

### Persisted fields
- `field_label`: `Char`
- `field_name`: `Char` (required)
- `field_type`: `Selection`
- `filter_id`: `Many2one` (relation=ipai.grid.filter)
- `operator`: `Selection` (required)
- `value_boolean`: `Boolean`
- `value_char`: `Char`
- `value_date`: `Date`
- `value_datetime`: `Datetime`
- `value_float`: `Float`
- `value_integer`: `Integer`
- `value_many2one`: `Integer`
- `value_selection`: `Char`

### Non-persisted fields
- _none_

## ipai.grid.view

- Module: `ipai_grid_view`
- Model type: `Model`
- Table: `ipai_grid_view`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `active_filter_id`: `Many2one` (relation=ipai.grid.filter)
- `column_count`: `Integer` (compute=_compute_column_count)
- `config_json`: `Text`
- `enable_column_reorder`: `Boolean`
- `enable_column_resize`: `Boolean`
- `enable_export`: `Boolean`
- `enable_quick_search`: `Boolean`
- `enable_row_selection`: `Boolean`
- `model_id`: `Many2one` (relation=ir.model, required, ondelete=cascade)
- `model_name`: `Char` (related=model_id.model)
- `name`: `Char` (required)
- `page_size`: `Integer`
- `page_size_options`: `Char`
- `sequence`: `Integer`
- `show_checkboxes`: `Boolean`
- `show_row_numbers`: `Boolean`
- `sort_json`: `Text`
- `view_type`: `Selection` (required)
- `visible_column_ids`: `Many2many` (relation=ipai.grid.column)

### Non-persisted fields
- `column_ids`: `One2many` (relation=ipai.grid.column)
- `filter_ids`: `One2many` (relation=ipai.grid.filter)

## ipai.month.end.closing

- Module: `ipai_month_end`
- Model type: `Model`
- Table: `ipai_month_end_closing`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `company_id`: `Many2one` (relation=res.company, required)
- `completed_tasks`: `Integer` (compute=_compute_progress)
- `last_workday`: `Date` (compute=_compute_last_workday)
- `name`: `Char` (required)
- `overdue_tasks`: `Integer` (compute=_compute_overdue)
- `period_date`: `Date` (required)
- `progress`: `Float` (compute=_compute_progress)
- `state`: `Selection`
- `total_tasks`: `Integer` (compute=_compute_progress)

### Non-persisted fields
- `task_ids`: `One2many` (relation=ipai.month.end.task)

## ipai.month.end.generator

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ipai_month_end_generator`

### Persisted fields

### Non-persisted fields
- _none_

## ipai.month.end.task

- Module: `ipai_month_end`
- Model type: `Model`
- Table: `ipai_month_end_task`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `approve_done`: `Boolean`
- `approve_done_by`: `Many2one` (relation=res.users)
- `approve_done_date`: `Datetime`
- `approve_due_date`: `Date`
- `approve_user_id`: `Many2one` (relation=res.users)
- `closing_id`: `Many2one` (relation=ipai.month.end.closing, required, ondelete=cascade)
- `days_overdue`: `Integer` (compute=_compute_days_overdue)
- `is_overdue`: `Boolean` (compute=_compute_days_overdue)
- `name`: `Char` (required)
- `notes`: `Html` (relation=Notes)
- `phase`: `Selection` (required)
- `prep_done`: `Boolean`
- `prep_done_by`: `Many2one` (relation=res.users)
- `prep_done_date`: `Datetime`
- `prep_due_date`: `Date`
- `prep_user_id`: `Many2one` (relation=res.users)
- `review_done`: `Boolean`
- `review_done_by`: `Many2one` (relation=res.users)
- `review_done_date`: `Datetime`
- `review_due_date`: `Date`
- `review_user_id`: `Many2one` (relation=res.users)
- `sequence`: `Integer`
- `state`: `Selection` (compute=_compute_state)
- `template_id`: `Many2one` (relation=ipai.month.end.task.template, ondelete=set null)

### Non-persisted fields
- _none_

## ipai.month.end.task.template

- Module: `ipai_month_end`
- Model type: `Model`
- Table: `ipai_month_end_task_template`

### Persisted fields
- `active`: `Boolean`
- `approve_day_offset`: `Integer`
- `approve_user_id`: `Many2one` (relation=res.users)
- `depends_on_ids`: `Many2many` (relation=ipai.month.end.task.template)
- `description`: `Html` (relation=Description)
- `name`: `Char` (required)
- `oca_module`: `Char`
- `odoo_model`: `Char`
- `phase`: `Selection` (required)
- `prep_day_offset`: `Integer`
- `prep_user_id`: `Many2one` (relation=res.users)
- `review_day_offset`: `Integer`
- `review_user_id`: `Many2one` (relation=res.users)
- `sequence`: `Integer`
- `task_count`: `Integer` (compute=_compute_task_count)

### Non-persisted fields
- _none_

## ipai.month.end.template

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_month_end_template`
- SQL constraints:
  - `task_base_name_unique`: `unique(task_base_name)` (Task base name must be unique!)
  - `task_base_name_unique`: `unique(task_base_name)` (Task base name must be unique!)

### Persisted fields
- `active`: `Boolean`
- `category`: `Char`
- `default_im_xml_id`: `Char`
- `task_base_name`: `Char` (required, index)

### Non-persisted fields
- `step_ids`: `One2many` (relation=ipai.month.end.template.step)

## ipai.month.end.template.step

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_month_end_template_step`

### Persisted fields
- `activity_type`: `Selection` (required)
- `business_days_before`: `Integer`
- `offset_days`: `Integer`
- `role_code`: `Char`
- `sequence`: `Integer`
- `template_id`: `Many2one` (relation=ipai.month.end.template, required, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.permission

- Module: `ipai_platform_permissions`
- Model type: `Model`
- Table: `ipai_permission`

### Persisted fields
- `active`: `Boolean`
- `group_id`: `Many2one` (relation=res.groups, ondelete=cascade)
- `name`: `Char` (required)
- `permission_level`: `Selection` (required)
- `role`: `Selection` (required)
- `scope_ref`: `Reference`
- `scope_type`: `Selection` (required)
- `user_id`: `Many2one` (relation=res.users, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.ph.holiday

- Module: `ipai_month_end`
- Model type: `Model`
- Table: `ipai_ph_holiday`
- SQL constraints:
  - `date_unique`: `UNIQUE(date)` (Holiday already exists for this date!)

### Persisted fields
- `date`: `Date` (required, index)
- `holiday_type`: `Selection` (required)
- `name`: `Char` (required)
- `year`: `Integer` (compute=_compute_year)

### Non-persisted fields
- _none_

## ipai.share.token

- Module: `ipai_platform_permissions`
- Model type: `Model`
- Table: `ipai_share_token`

### Persisted fields
- `active`: `Boolean`
- `created_by`: `Many2one` (relation=res.users)
- `expires_at`: `Datetime`
- `is_public`: `Boolean`
- `name`: `Char` (required)
- `permission_level`: `Selection` (required)
- `scope_ref`: `Reference`
- `scope_type`: `Selection` (required)

### Non-persisted fields
- _none_

## ipai.studio.ai.history

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_studio_ai_history`

### Persisted fields
- `analysis`: `Text`
- `automation_id`: `Many2one` (relation=base.automation, ondelete=set null)
- `command`: `Text` (required)
- `command_type`: `Selection`
- `confidence`: `Float`
- `feedback_comment`: `Text`
- `feedback_score`: `Selection`
- `field_id`: `Many2one` (relation=ir.model.fields, ondelete=set null)
- `model_id`: `Many2one` (relation=ir.model, ondelete=set null)
- `model_name`: `Char` (related=model_id.model)
- `result`: `Selection`
- `result_message`: `Text`
- `user_id`: `Many2one` (relation=res.users, required)

### Non-persisted fields
- _none_

## ipai.studio.ai.service

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ipai_studio_ai_service`

### Persisted fields

### Non-persisted fields
- _none_

## ipai.studio.ai.stats

- Module: `ipai`
- Model type: `Model`
- Table: `N/A`

### Persisted fields
- `avg_confidence`: `Float`
- `command_type`: `Selection`
- `date`: `Date`
- `executed_commands`: `Integer`
- `failed_commands`: `Integer`
- `total_commands`: `Integer`

### Non-persisted fields
- _none_

## ipai.studio.ai.wizard

- Module: `ipai`
- Model type: `TransientModel`
- Table: `ipai_studio_ai_wizard`

### Persisted fields
- `analysis_json`: `Text`
- `command`: `Text` (required)
- `command_type`: `Selection`
- `confidence`: `Float`
- `context_model_id`: `Many2one` (relation=ir.model)
- `created_field_id`: `Many2one` (relation=ir.model.fields)
- `field_label`: `Char`
- `field_name`: `Char`
- `field_required`: `Boolean`
- `field_type`: `Selection`
- `history_id`: `Many2one` (relation=ipai.studio.ai.history)
- `is_ready`: `Boolean`
- `message`: `Html`
- `relation_model_id`: `Many2one` (relation=ir.model)
- `result_message`: `Html`
- `selection_options`: `Text`
- `state`: `Selection`
- `target_model_id`: `Many2one` (relation=ir.model)

### Non-persisted fields
- _none_

## ipai.travel.request

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_travel_request`

### Persisted fields
- `company_id`: `Many2one` (relation=res.company)
- `currency_id`: `Many2one` (relation=res.currency)
- `destination`: `Char` (required)
- `employee_id`: `Many2one` (relation=hr.employee, required)
- `end_date`: `Date` (required)
- `estimated_budget`: `Monetary`
- `name`: `Char` (required)
- `project_id`: `Many2one` (relation=project.project)
- `purpose`: `Text`
- `start_date`: `Date` (required)
- `state`: `Selection` (required)

### Non-persisted fields
- _none_

## ipai.workflow.mixin

- Module: `ipai_platform_workflow`
- Model type: `AbstractModel`
- Table: `ipai_workflow_mixin`

### Persisted fields
- `workflow_state`: `Selection` (index)
- `workflow_state_date`: `Datetime`
- `workflow_state_user_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- _none_

## ipai.workos.block

- Module: `ipai_workos_blocks`
- Model type: `Model`
- Table: `ipai_workos_block`
- Python constraints:
  - `_check_content_json`

### Persisted fields
- `attachment_id`: `Many2one` (relation=ir.attachment, ondelete=set null)
- `block_type`: `Selection` (required)
- `callout_color`: `Char`
- `callout_icon`: `Char`
- `content_html`: `Html` (compute=_compute_content_html)
- `content_json`: `Text`
- `content_text`: `Text` (compute=_compute_content_text)
- `is_checked`: `Boolean`
- `is_collapsed`: `Boolean`
- `name`: `Char` (compute=_compute_name)
- `page_id`: `Many2one` (relation=ipai.workos.page, required, index, ondelete=cascade)
- `parent_block_id`: `Many2one` (relation=ipai.workos.block, ondelete=cascade)
- `sequence`: `Integer`

### Non-persisted fields
- `child_block_ids`: `One2many` (relation=ipai.workos.block)

## ipai.workos.canvas

- Module: `ipai_workos_canvas`
- Model type: `Model`
- Table: `ipai_workos_canvas`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `name`: `Char` (required)
- `nodes_json`: `Text`
- `page_id`: `Many2one` (relation=ipai.workos.page, index, ondelete=cascade)
- `viewport_json`: `Text`

### Non-persisted fields
- _none_

## ipai.workos.comment

- Module: `ipai_workos_collab`
- Model type: `Model`
- Table: `ipai_workos_comment`
- _inherit: `mail.thread`

### Persisted fields
- `anchor_block_id`: `Integer`
- `author_id`: `Many2one` (relation=res.users, required)
- `content`: `Html` (required)
- `content_text`: `Text` (compute=_compute_content_text)
- `is_resolved`: `Boolean`
- `mentioned_user_ids`: `Many2many` (relation=res.users)
- `parent_id`: `Many2one` (relation=ipai.workos.comment, ondelete=cascade)
- `reply_count`: `Integer` (compute=_compute_reply_count)
- `resolved_at`: `Datetime`
- `resolved_by`: `Many2one` (relation=res.users)
- `target_id`: `Integer` (required, index)
- `target_model`: `Char` (required, index)
- `target_name`: `Char` (compute=_compute_target_name)

### Non-persisted fields
- `child_ids`: `One2many` (relation=ipai.workos.comment)

## ipai.workos.database

- Module: `ipai_workos_db`
- Model type: `Model`
- Table: `ipai_workos_database`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `description`: `Text`
- `icon`: `Char`
- `name`: `Char` (required)
- `page_id`: `Many2one` (relation=ipai.workos.page, ondelete=cascade)
- `row_count`: `Integer` (compute=_compute_row_count)
- `space_id`: `Many2one` (relation=ipai.workos.space, ondelete=cascade)

### Non-persisted fields
- `property_ids`: `One2many` (relation=ipai.workos.property)
- `row_ids`: `One2many` (relation=ipai.workos.row)

## ipai.workos.page

- Module: `ipai_workos_core`
- Model type: `Model`
- Table: `ipai_workos_page`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `child_count`: `Integer` (compute=_compute_child_count)
- `content_preview`: `Text` (compute=_compute_content_preview)
- `cover_image`: `Binary`
- `icon`: `Char`
- `is_archived`: `Boolean`
- `last_edited_by`: `Many2one` (relation=res.users, compute=_compute_last_edited)
- `name`: `Char` (required)
- `parent_id`: `Many2one` (relation=ipai.workos.page, index, ondelete=cascade)
- `parent_path`: `Char` (index)
- `sequence`: `Integer`
- `space_id`: `Many2one` (relation=ipai.workos.space, compute=_compute_space_id, ondelete=cascade)
- `template_id`: `Many2one` (relation=ipai.workos.template)
- `workspace_id`: `Many2one` (relation=ipai.workos.workspace, related=space_id.workspace_id)

### Non-persisted fields
- `child_ids`: `One2many` (relation=ipai.workos.page)

## ipai.workos.property

- Module: `ipai_workos_db`
- Model type: `Model`
- Table: `ipai_workos_property`

### Persisted fields
- `database_id`: `Many2one` (relation=ipai.workos.database, required, ondelete=cascade)
- `is_title`: `Boolean`
- `is_visible`: `Boolean`
- `name`: `Char` (required)
- `options_json`: `Text`
- `property_type`: `Selection` (required)
- `related_database_id`: `Many2one` (relation=ipai.workos.database, ondelete=set null)
- `sequence`: `Integer`
- `width`: `Integer`

### Non-persisted fields
- _none_

## ipai.workos.row

- Module: `ipai_workos_db`
- Model type: `Model`
- Table: `ipai_workos_row`

### Persisted fields
- `active`: `Boolean`
- `database_id`: `Many2one` (relation=ipai.workos.database, required, index, ondelete=cascade)
- `name`: `Char` (compute=_compute_name)
- `sequence`: `Integer`
- `values_json`: `Text`

### Non-persisted fields
- _none_

## ipai.workos.search

- Module: `ipai_workos_search`
- Model type: `TransientModel`
- Table: `ipai_workos_search`

### Persisted fields
- `block_results`: `Text`
- `database_results`: `Text`
- `page_results`: `Text`
- `query`: `Char`
- `scope`: `Selection`
- `scope_id`: `Integer`

### Non-persisted fields
- _none_

## ipai.workos.search.history

- Module: `ipai_workos_search`
- Model type: `Model`
- Table: `ipai_workos_search_history`

### Persisted fields
- `query`: `Char` (required)
- `result_count`: `Integer`
- `user_id`: `Many2one` (relation=res.users, required, index)

### Non-persisted fields
- _none_

## ipai.workos.space

- Module: `ipai_workos_core`
- Model type: `Model`
- Table: `ipai_workos_space`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `color`: `Integer`
- `description`: `Text`
- `icon`: `Char`
- `name`: `Char` (required)
- `page_count`: `Integer` (compute=_compute_page_count)
- `sequence`: `Integer`
- `visibility`: `Selection` (required)
- `workspace_id`: `Many2one` (relation=ipai.workos.workspace, required, ondelete=cascade)

### Non-persisted fields
- `page_ids`: `One2many` (relation=ipai.workos.page)

## ipai.workos.template

- Module: `ipai_workos_templates`
- Model type: `Model`
- Table: `ipai_workos_template`

### Persisted fields
- `blocks_json`: `Text`
- `category`: `Selection` (required)
- `description`: `Text`
- `icon`: `Char`
- `is_published`: `Boolean`
- `is_system`: `Boolean`
- `name`: `Char` (required)
- `properties_json`: `Text`
- `sequence`: `Integer`
- `tag_ids`: `Many2many` (relation=ipai.workos.template.tag)
- `views_json`: `Text`

### Non-persisted fields
- _none_

## ipai.workos.template.tag

- Module: `ipai_workos_templates`
- Model type: `Model`
- Table: `ipai_workos_template_tag`

### Persisted fields
- `color`: `Integer`
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## ipai.workos.view

- Module: `ipai_workos_views`
- Model type: `Model`
- Table: `ipai_workos_view`

### Persisted fields
- `config_json`: `Text`
- `database_id`: `Many2one` (relation=ipai.workos.database, required, index, ondelete=cascade)
- `date_property_id`: `Many2one` (relation=ipai.workos.property)
- `filter_json`: `Text`
- `group_by_property_id`: `Many2one` (relation=ipai.workos.property)
- `is_default`: `Boolean`
- `is_shared`: `Boolean`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `sort_json`: `Text`
- `user_id`: `Many2one` (relation=res.users)
- `view_type`: `Selection` (required)
- `visible_property_ids`: `Many2many` (relation=ipai.workos.property)

### Non-persisted fields
- _none_

## ipai.workos.workspace

- Module: `ipai_workos_core`
- Model type: `Model`
- Table: `ipai_workos_workspace`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `color`: `Integer`
- `description`: `Text`
- `icon`: `Char`
- `member_ids`: `Many2many` (relation=res.users)
- `name`: `Char` (required)
- `owner_id`: `Many2one` (relation=res.users, required)
- `space_count`: `Integer` (compute=_compute_space_count)

### Non-persisted fields
- `space_ids`: `One2many` (relation=ipai.workos.space)

## ipai.workspace

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_workspace`
- _inherit: `ipai.workspace, mail.activity.mixin, mail.thread`
- SQL constraints:
  - `name_company_uniq`: `unique(name, company_id)` (Workspace name must be unique per company.)
  - `name_company_uniq`: `unique(name, company_id)` (Workspace name must be unique per company.)

### Persisted fields
- `account_manager_id`: `Many2one` (relation=res.users)
- `active`: `Boolean`
- `brand_name`: `Char`
- `campaign_type`: `Selection`
- `channel_mix`: `Char`
- `client_id`: `Many2one` (relation=res.partner, index)
- `closing_stage`: `Selection`
- `code`: `Char` (index)
- `color`: `Integer` (relation=Color Index)
- `company_id`: `Many2one` (relation=res.company, index)
- `date_end`: `Datetime`
- `date_start`: `Datetime`
- `engagement_count`: `Integer` (compute=_compute_counters)
- `entity_code`: `Char`
- `fiscal_period`: `Char`
- `industry`: `Selection` (required)
- `invoice_count`: `Integer` (compute=_compute_counters)
- `is_critical`: `Boolean`
- `name`: `Char` (required)
- `parent_id`: `Many2one` (relation=ipai.workspace, index, ondelete=cascade)
- `planned_hours`: `Float`
- `progress`: `Float`
- `project_count`: `Integer` (compute=_compute_counters)
- `remaining_hours`: `Float`
- `sequence`: `Integer`
- `stage`: `Selection`
- `workspace_type`: `Selection` (required)

### Non-persisted fields
- `child_ids`: `One2many` (relation=ipai.workspace)
- `link_ids`: `One2many` (relation=ipai.workspace.link)

## ipai.workspace.link

- Module: `ipai`
- Model type: `Model`
- Table: `ipai_workspace_link`
- SQL constraints:
  - `workspace_res_uniq`: `unique(workspace_id, res_model, res_id)` (This record is already linked to the workspace.)
  - `workspace_res_uniq`: `unique(workspace_id, res_model, res_id)` (This record is already linked to the workspace.)

### Persisted fields
- `display_name`: `Char` (compute=_compute_display_name)
- `link_type`: `Selection`
- `res_id`: `Integer` (required)
- `res_model`: `Char` (required)
- `workspace_id`: `Many2one` (relation=ipai.workspace, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## ir.actions.act_multi

- Module: `web_ir_actions_act_multi`
- Model type: `Model`
- Table: `ir_actions`
- _inherit: `ir.actions.actions`

### Persisted fields
- `type`: `Char`

### Non-persisted fields
- _none_

## ir.actions.act_window.message

- Module: `web_ir_actions_act_window_message`
- Model type: `Model`
- Table: `ir_actions`
- _inherit: `ir.actions.actions`

### Persisted fields
- `type`: `Char`

### Non-persisted fields
- _none_

## ir.actions.act_window.view

- Module: `web_timeline`
- Model type: `Model`
- Table: `ir_actions_act_window_view`
- _inherit: `ir.actions.act_window.view`

### Persisted fields
- `view_mode`: `Selection`

### Non-persisted fields
- _none_

## ir.actions.actions

- Module: `base_temporary_action`
- Model type: `Model`
- Table: `ir_actions_actions`
- _inherit: `ir.actions.actions`

### Persisted fields
- `is_temporary`: `Boolean`

### Non-persisted fields
- _none_

## ir.actions.report

- Module: `account_financial_report`
- Model type: `Model`
- Table: `ir_actions_report`
- _inherit: `ir.actions.report`

### Persisted fields
- `report_type`: `Selection`

### Non-persisted fields
- _none_

## ir.attachment

- Module: `attachment_unindex_content`
- Model type: `Model`
- Table: `ir_attachment`
- _inherit: `autovacuum.mixin, ir.attachment`

### Persisted fields

### Non-persisted fields
- _none_

## ir.config_parameter

- Module: `web_m2x_options`
- Model type: `Model`
- Table: `ir_config_parameter`
- _inherit: `ir.config_parameter`

### Persisted fields

### Non-persisted fields
- _none_

## ir.cron

- Module: `base_cron_exclusion`
- Model type: `Model`
- Table: `ir_cron`
- _inherit: `ir.cron`
- Python constraints:
  - `_check_auto_exclusion`

### Persisted fields
- `email_template_id`: `Many2one`
- `mutually_exclusive_cron_ids`: `Many2many`

### Non-persisted fields
- _none_

## ir.exports

- Module: `jsonifier`
- Model type: `Model`
- Table: `ir_exports`
- _inherit: `ir.exports`

### Persisted fields
- `global_resolver_id`: `Many2one`
- `language_agnostic`: `Boolean`

### Non-persisted fields
- _none_

## ir.exports.line

- Module: `jsonifier`
- Model type: `Model`
- Table: `ir_exports_line`
- _inherit: `ir.exports.line`
- Python constraints:
  - `_check_function_resolver`
  - `_check_target`

### Persisted fields
- `active`: `Boolean`
- `instance_method_name`: `Char`
- `lang_id`: `Many2one`
- `resolver_id`: `Many2one`
- `target`: `Char`

### Non-persisted fields
- _none_

## ir.exports.resolver

- Module: `jsonifier`
- Model type: `Model`
- Table: `ir_exports_resolver`

### Persisted fields
- `name`: `Char`
- `python_code`: `Text`
- `type`: `Selection`

### Non-persisted fields
- _none_

## ir.fields.converter

- Module: `html_text`
- Model type: `AbstractModel`
- Table: `ir_fields_converter`
- _inherit: `ir.fields.converter`

### Persisted fields

### Non-persisted fields
- _none_

## ir.filters

- Module: `web_widget_dropdown_dynamic`
- Model type: `Model`
- Table: `ir_filters`
- _inherit: `ir.filters`

### Persisted fields

### Non-persisted fields
- _none_

## ir.http

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ir_http`
- _inherit: `ir.http`

### Persisted fields

### Non-persisted fields
- _none_

## ir.model

- Module: `base_force_record_noupdate`
- Model type: `Model`
- Table: `ir_model`
- _inherit: `ir.model`
- Python constraints:
  - `check_name_search_domain`
  - `update_search_wo_restart`

### Persisted fields
- `active_custom_tracking`: `Boolean`
- `add_open_tab_field`: `Boolean`
- `add_smart_search`: `Boolean`
- `automatic_custom_tracking`: `Boolean` (compute=_compute_automatic_custom_tracking)
- `automatic_custom_tracking_domain`: `Char` (compute=_compute_automatic_custom_tracking_domain)
- `force_noupdate`: `Boolean` (relation=Force No-Update)
- `name_search_domain`: `Char`
- `name_search_ids`: `Many2many` (relation=ir.model.fields)
- `restrict_update`: `Boolean` (relation=Update Restrict Model)
- `rpc_config_edit`: `Text`
- `smart_search_warning`: `Html` (compute=_compute_smart_search_warning)
- `tracked_field_count`: `Integer` (compute=_compute_tracked_field_count)
- `update_allowed_group_ids`: `Many2many` (relation=res.groups)
- `use_smart_name_search`: `Boolean`

### Non-persisted fields
- `comodel_field_ids`: `One2many` (relation=ir.model.fields)
- `m2x_comodels_option_ids`: `One2many` (relation=m2x.create.edit.option)
- `m2x_option_ids`: `One2many` (relation=m2x.create.edit.option)

## ir.model.access

- Module: `base_model_restrict_update`
- Model type: `Model`
- Table: `ir_model_access`
- _inherit: `ir.model.access`

### Persisted fields

### Non-persisted fields
- _none_

## ir.model.data

- Module: `base_force_record_noupdate`
- Model type: `Model`
- Table: `ir_model_data`
- _inherit: `ir.model.data`

### Persisted fields

### Non-persisted fields
- _none_

## ir.model.fields

- Module: `database_cleanup`
- Model type: `Model`
- Table: `ir_model_fields`
- _inherit: `ir.model.fields`

### Persisted fields
- `can_have_options`: `Boolean` (compute=_compute_can_have_options)
- `comodel_id`: `Many2one` (relation=ir.model, compute=_compute_comodel_id, index)
- `custom_tracking`: `Boolean` (compute=_compute_custom_tracking)
- `native_tracking`: `Boolean` (compute=_compute_native_tracking)
- `trackable`: `Boolean` (compute=_compute_trackable)
- `tracking_domain`: `Char`

### Non-persisted fields
- _none_

## ir.model.index.size

- Module: `database_size`
- Model type: `Model`
- Table: `ir_model_index_size`

### Persisted fields
- `ir_model_size_id`: `Many2one` (required, index, ondelete=cascade)
- `name`: `Char` (required)
- `size`: `Integer`

### Non-persisted fields
- _none_

## ir.model.relation.size

- Module: `database_size`
- Model type: `Model`
- Table: `ir_model_relation_size`

### Persisted fields
- `ir_model_size_id`: `Many2one` (required, index, ondelete=cascade)
- `name`: `Char` (required)
- `size`: `Integer`

### Non-persisted fields
- _none_

## ir.model.size

- Module: `database_size`
- Model type: `Model`
- Table: `ir_model_size`
- SQL constraints:
  - `uniq_model_measurement_date`: `unique(model, measurement_date)` (There is already a measurement for this model on the given date)

### Persisted fields
- `attachment_size`: `Integer`
- `indexes_size`: `Integer` (compute=_compute_indexes_size)
- `measurement_date`: `Date` (relation=Date of Measurement, required)
- `model`: `Char` (index)
- `model_name`: `Char` (compute=_compute_model_name)
- `relations_size`: `Integer` (compute=_compute_relations_size)
- `table_size`: `Integer`
- `total_database_size`: `Integer` (compute=_compute_total_sizes)
- `total_model_size`: `Integer` (compute=_compute_total_sizes)
- `total_table_size`: `Integer`
- `tuples`: `Integer`

### Non-persisted fields
- `ir_model_index_size_ids`: `One2many`
- `ir_model_relation_size_ids`: `One2many`

## ir.model.size.report

- Module: `database_size`
- Model type: `Model`
- Table: `N/A`

### Persisted fields
- `attachment_size`: `Integer`
- `diff_total_database_size`: `Integer` (relation=Change in Total Database Size)
- `diff_total_model_size`: `Integer` (relation=Change in Total Model Size)
- `historical_attachment_size`: `Integer`
- `historical_indexes_size`: `Integer` (relation=Historical Index Size)
- `historical_measurement_date`: `Date` (relation=Historical Date of Measurement)
- `historical_relations_size`: `Integer` (relation=Historical Many2many Tables Size)
- `historical_table_size`: `Integer` (relation=Historical Bare Table Size)
- `historical_total_database_size`: `Integer`
- `historical_total_model_size`: `Integer`
- `historical_total_table_size`: `Integer`
- `historical_tuples`: `Integer` (relation=Historical Estimated Rows)
- `indexes_size`: `Integer` (relation=Index Size)
- `measurement_date`: `Date` (relation=Date of Measurement)
- `model`: `Char`
- `model_name`: `Char`
- `relations_size`: `Integer` (relation=Many2many Tables Size)
- `table_size`: `Integer` (relation=Bare Table Size)
- `total_database_size`: `Integer`
- `total_model_size`: `Integer`
- `total_table_size`: `Integer`
- `tuples`: `Integer` (relation=Estimated Rows)

### Non-persisted fields
- _none_

## ir.module.author

- Module: `module_analysis`
- Model type: `Model`
- Table: `ir_module_author`
- SQL constraints:
  - `name_uniq`: `unique(name)` (The name of the modules author should be unique per database!)

### Persisted fields
- `installed_module_ids`: `Many2many`
- `installed_module_qty`: `Integer` (compute=_compute_installed_module_qty)
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## ir.module.module

- Module: `module_analysis`
- Model type: `Model`
- Table: `ir_module_module`
- _inherit: `ir.module.module`

### Persisted fields
- `author_ids`: `Many2many`
- `css_code_qty`: `Integer`
- `is_oca_module`: `Boolean` (compute=_compute_is_oca_module)
- `is_odoo_module`: `Boolean` (compute=_compute_is_odoo_module)
- `js_code_qty`: `Integer`
- `module_type_id`: `Many2one`
- `python_code_qty`: `Integer`
- `scss_code_qty`: `Integer`
- `xml_code_qty`: `Integer`

### Non-persisted fields
- _none_

## ir.module.type

- Module: `module_analysis`
- Model type: `Model`
- Table: `ir_module_type`

### Persisted fields
- `installed_module_qty`: `Integer` (compute=_compute_installed_module_qty)
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- `installed_module_ids`: `One2many`

## ir.module.type.rule

- Module: `module_analysis`
- Model type: `Model`
- Table: `ir_module_type_rule`

### Persisted fields
- `module_domain`: `Char` (required)
- `module_type_id`: `Many2one` (required)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## ir.qweb

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ir_qweb`
- _inherit: `ir.qweb`

### Persisted fields

### Non-persisted fields
- _none_

## ir.sequence

- Module: `base_sequence_option`
- Model type: `Model`
- Table: `ir_sequence`
- _inherit: `ir.sequence`

### Persisted fields

### Non-persisted fields
- _none_

## ir.sequence.option

- Module: `base_sequence_option`
- Model type: `Model`
- Table: `ir_sequence_option`
- _inherit: `ir.sequence.option`

### Persisted fields
- `company_id`: `Many2one` (required, index)
- `model`: `Selection` (required, index)
- `name`: `Char`
- `use_sequence_option`: `Boolean`

### Non-persisted fields
- `option_ids`: `One2many`

## ir.sequence.option.line

- Module: `base_sequence_option`
- Model type: `Model`
- Table: `ir_sequence_option_line`

### Persisted fields
- `base_id`: `Many2one` (required, index, ondelete=cascade)
- `company_id`: `Many2one` (related=base_id.company_id)
- `filter_domain`: `Char`
- `implementation`: `Selection` (related=sequence_id.implementation)
- `model`: `Selection` (related=base_id.model)
- `name`: `Char` (required)
- `prefix`: `Char` (related=sequence_id.prefix)
- `sequence_id`: `Many2one` (required)
- `suffix`: `Char` (related=sequence_id.suffix)
- `use_sequence_option`: `Boolean` (related=base_id.use_sequence_option)

### Non-persisted fields
- _none_

## ir.ui.view

- Module: `base_view_inheritance_extension`
- Model type: `Model`
- Table: `ir_ui_view`
- _inherit: `ir.ui.view`

### Persisted fields
- `type`: `Selection`

### Non-persisted fields
- _none_

## journal.ledger.report.wizard

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `journal_ledger_report_wizard`
- _inherit: `account_financial_report_abstract_wizard`

### Persisted fields
- `date_from`: `Date` (required)
- `date_range_id`: `Many2one`
- `date_to`: `Date` (required)
- `foreign_currency`: `Boolean`
- `group_option`: `Selection` (required)
- `journal_ids`: `Many2many`
- `move_target`: `Selection` (required)
- `sort_option`: `Selection` (required)
- `with_account_name`: `Boolean`
- `with_auto_sequence`: `Boolean`

### Non-persisted fields
- _none_

## m2x.create.edit.option

- Module: `web_m2x_options_manager`
- Model type: `Model`
- Table: `m2x_create_edit_option`
- SQL constraints:
  - `field_uniqueness`: `unique(field_id)` (Options must be unique for each field!)
- Python constraints:
  - `_check_field_can_have_options`

### Persisted fields
- `comodel_id`: `Many2one` (relation=ir.model, related=field_id.comodel_id)
- `comodel_name`: `Char` (related=field_id.relation)
- `field_id`: `Many2one` (relation=ir.model.fields, required, index, ondelete=cascade)
- `field_name`: `Char` (related=field_id.name)
- `model_id`: `Many2one` (relation=ir.model, related=field_id.model_id)
- `model_name`: `Char` (related=field_id.model)
- `name`: `Char` (compute=_compute_name)
- `option_create`: `Selection` (required)
- `option_create_edit`: `Selection` (required)

### Non-persisted fields
- _none_

## mail.message

- Module: `autovacuum_message_attachment`
- Model type: `Model`
- Table: `mail_message`
- _inherit: `mail.message, autovacuum.mixin`

### Persisted fields

### Non-persisted fields
- _none_

## mail.thread

- Module: `fetchmail_notify_error_to_sender`
- Model type: `AbstractModel`
- Table: `mail_thread`
- _inherit: `mail.thread`

### Persisted fields

### Non-persisted fields
- _none_

## mail.tracking.value

- Module: `tracking_manager`
- Model type: `Model`
- Table: `mail_tracking_value`
- _inherit: `mail.tracking.value`

### Persisted fields

### Non-persisted fields
- _none_

## master.control.mixin

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `master_control_mixin`

### Persisted fields

### Non-persisted fields
- _none_

## mis.cash_flow

- Module: `mis_builder_cash_flow`
- Model type: `Model`
- Table: `N/A`

### Persisted fields
- `account_id`: `Many2one` (index)
- `account_type`: `Selection` (related=account_id.account_type)
- `company_id`: `Many2one` (index)
- `credit`: `Float`
- `date`: `Date` (index)
- `debit`: `Float`
- `full_reconcile_id`: `Many2one` (relation=account.full.reconcile, index)
- `line_type`: `Selection` (index)
- `move_line_id`: `Many2one`
- `name`: `Char`
- `parent_state`: `Selection`
- `partner_id`: `Many2one`
- `reconciled`: `Boolean`

### Non-persisted fields
- _none_

## mis.cash_flow.forecast_line

- Module: `mis_builder_cash_flow`
- Model type: `Model`
- Table: `mis_cash_flow_forecast_line`
- Python constraints:
  - `_check_company_id_account_id`

### Persisted fields
- `account_id`: `Many2one` (required)
- `balance`: `Float` (required)
- `company_id`: `Many2one` (relation=res.company, required, index)
- `date`: `Date` (required, index)
- `name`: `Char` (required)
- `partner_id`: `Many2one`

### Non-persisted fields
- _none_

## mis.report.instance

- Module: `mis_template_financial_report`
- Model type: `Model`
- Table: `mis_report_instance`
- _inherit: `mis.report.instance`

### Persisted fields
- `allow_horizontal`: `Boolean` (compute=_compute_allow_horizontal)
- `horizontal`: `Boolean`

### Non-persisted fields
- _none_

## mis.report.kpi

- Module: `mis_template_financial_report`
- Model type: `Model`
- Table: `mis_report_kpi`
- _inherit: `mis.report.kpi`

### Persisted fields
- `split_after`: `Boolean`

### Non-persisted fields
- _none_

## open.items.report.wizard

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `open_items_report_wizard`
- _inherit: `account_financial_report_abstract_wizard, open.items.report.wizard`

### Persisted fields
- `account_code_from`: `Many2one`
- `account_code_to`: `Many2one`
- `account_ids`: `Many2many` (required)
- `date_at`: `Date` (required)
- `date_from`: `Date`
- `foreign_currency`: `Boolean`
- `grouped_by`: `Selection`
- `hide_account_at_0`: `Boolean`
- `partner_ids`: `Many2many`
- `payable_accounts_only`: `Boolean`
- `receivable_accounts_only`: `Boolean`
- `show_partner_details`: `Boolean`
- `target_move`: `Selection` (required)

### Non-persisted fields
- _none_

## outstanding.statement.wizard

- Module: `partner_statement`
- Model type: `TransientModel`
- Table: `outstanding_statement_wizard`
- _inherit: `statement.common.wizard`

### Persisted fields

### Non-persisted fields
- _none_

## ph.holiday

- Module: `ipai_tbwa_finance`
- Model type: `Model`
- Table: `ph_holiday`
- SQL constraints:
  - `date_unique`: `unique(date, company_id)` (Holiday date must be unique per company)

### Persisted fields
- `company_id`: `Many2one` (relation=res.company)
- `date`: `Date` (required, index)
- `holiday_type`: `Selection` (required)
- `name`: `Char` (required)
- `year`: `Integer` (compute=_compute_year, index)

### Non-persisted fields
- _none_

## ppm.close.task

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_close_task`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `agency_code`: `Selection` (required)
- `approval_completed_by`: `Char`
- `approval_completed_date`: `Date`
- `approval_days`: `Float`
- `approval_due`: `Date` (related=monthly_close_id.approval_due_date)
- `approver_code`: `Char`
- `completion_notes`: `Text`
- `detailed_task`: `Text` (required)
- `monthly_close_id`: `Many2one` (relation=ppm.monthly.close, required, index, ondelete=cascade)
- `name`: `Char` (required)
- `notes`: `Text`
- `owner_code`: `Char` (required)
- `prep_completed_by`: `Char`
- `prep_completed_date`: `Date`
- `prep_days`: `Float`
- `prep_start`: `Date` (related=monthly_close_id.prep_start_date)
- `review_completed_by`: `Char`
- `review_completed_date`: `Date`
- `review_days`: `Float`
- `review_due`: `Date` (related=monthly_close_id.review_due_date)
- `reviewer_code`: `Char`
- `sequence`: `Integer`
- `state`: `Selection` (required)
- `template_id`: `Many2one` (relation=ppm.close.template)
- `total_days`: `Float` (compute=_compute_total_days)

### Non-persisted fields
- _none_

## ppm.close.template

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_close_template`

### Persisted fields
- `active`: `Boolean`
- `agency_code`: `Selection` (required)
- `approval_days`: `Float`
- `approver_code`: `Char`
- `detailed_task`: `Text` (required)
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `owner_code`: `Char` (required)
- `prep_days`: `Float`
- `review_days`: `Float`
- `reviewer_code`: `Char`
- `sequence`: `Integer`
- `task_category`: `Char` (required)
- `total_days`: `Float` (compute=_compute_total_days)

### Non-persisted fields
- _none_

## ppm.kpi.snapshot

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_kpi_snapshot`

### Persisted fields
- `as_of`: `Datetime` (required, index)
- `kpi_category`: `Selection`
- `kpi_key`: `Char` (required, index)
- `kpi_label`: `Char`
- `name`: `Char` (compute=_compute_name)
- `portfolio_id`: `Many2one` (relation=ppm.portfolio, index)
- `program_id`: `Many2one` (relation=ppm.program, index)
- `project_id`: `Many2one` (relation=project.project, index)
- `scope`: `Selection` (required)
- `source`: `Selection`
- `source_ref`: `Char`
- `status`: `Selection` (compute=_compute_status)
- `target_value`: `Float`
- `threshold_green`: `Float`
- `threshold_yellow`: `Float`
- `unit`: `Char`
- `value`: `Float` (required)
- `value_text`: `Char`

### Non-persisted fields
- _none_

## ppm.monthly.close

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_monthly_close`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `approval_due_date`: `Date` (compute=_compute_schedule_dates)
- `close_month`: `Date` (required)
- `created_by_cron`: `Boolean`
- `month_end_date`: `Date` (compute=_compute_schedule_dates)
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `prep_start_date`: `Date` (compute=_compute_schedule_dates)
- `progress_percentage`: `Float` (compute=_compute_task_stats)
- `review_due_date`: `Date` (compute=_compute_schedule_dates)
- `state`: `Selection`
- `task_completed`: `Integer` (compute=_compute_task_stats)
- `task_count`: `Integer` (compute=_compute_task_stats)

### Non-persisted fields
- `task_ids`: `One2many` (relation=ppm.close.task)

## ppm.portfolio

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_portfolio`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `code_unique`: `UNIQUE(code)` (Portfolio code must be unique!)
  - `code_unique`: `UNIQUE(code)` (Portfolio code must be unique!)

### Persisted fields
- `active`: `Boolean`
- `budget_variance_pct`: `Float` (compute=_compute_budget_rollup)
- `code`: `Char` (required)
- `currency_id`: `Many2one` (relation=res.currency)
- `date_end`: `Date`
- `date_start`: `Date`
- `description`: `Html`
- `health_score`: `Integer` (compute=_compute_health_status)
- `health_status`: `Selection` (compute=_compute_health_status)
- `name`: `Char` (required)
- `objective`: `Text`
- `owner_id`: `Many2one` (relation=res.users)
- `program_count`: `Integer` (compute=_compute_program_count)
- `sequence`: `Integer`
- `sponsor_id`: `Many2one` (relation=res.users)
- `total_actual`: `Monetary` (compute=_compute_budget_rollup)
- `total_budget`: `Monetary` (compute=_compute_budget_rollup)

### Non-persisted fields
- `kpi_snapshot_ids`: `One2many` (relation=ppm.kpi.snapshot)
- `program_ids`: `One2many` (relation=ppm.program)

## ppm.program

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_program`
- _inherit: `mail.activity.mixin, mail.thread`
- SQL constraints:
  - `code_unique`: `UNIQUE(code)` (Program code must be unique!)
  - `code_unique`: `UNIQUE(code)` (Program code must be unique!)

### Persisted fields
- `active`: `Boolean`
- `actual_cost`: `Monetary` (compute=_compute_actual_cost)
- `budget`: `Monetary`
- `code`: `Char` (required)
- `currency_id`: `Many2one` (relation=res.currency)
- `date_end`: `Date`
- `date_start`: `Date`
- `description`: `Html`
- `health_notes`: `Text`
- `health_score`: `Integer`
- `health_status`: `Selection`
- `name`: `Char` (required)
- `objectives`: `Text`
- `open_high_risks`: `Integer` (compute=_compute_risk_count)
- `portfolio_id`: `Many2one` (relation=ppm.portfolio, ondelete=restrict)
- `program_manager_id`: `Many2one` (relation=res.users)
- `project_count`: `Integer` (compute=_compute_project_count)
- `project_ids`: `Many2many` (relation=project.project)
- `risk_count`: `Integer` (compute=_compute_risk_count)
- `sequence`: `Integer`
- `sponsor_id`: `Many2one` (relation=res.users)

### Non-persisted fields
- `allocation_ids`: `One2many` (relation=ppm.resource.allocation)
- `kpi_snapshot_ids`: `One2many` (relation=ppm.kpi.snapshot)
- `risk_ids`: `One2many` (relation=ppm.risk)

## ppm.resource.allocation

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_resource_allocation`
- Python constraints:
  - `_check_allocation`
  - `_check_dates`

### Persisted fields
- `allocation_pct`: `Float`
- `date_end`: `Date` (required)
- `date_start`: `Date` (required)
- `employee_id`: `Many2one` (relation=hr.employee, required, index)
- `is_overloaded`: `Boolean` (compute=_compute_overload)
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `planned_hours`: `Float`
- `program_id`: `Many2one` (relation=ppm.program, index)
- `project_id`: `Many2one` (relation=project.project, index)
- `role`: `Selection`
- `status`: `Selection`
- `task_id`: `Many2one` (relation=project.task)
- `total_allocation`: `Float` (compute=_compute_overload)
- `user_id`: `Many2one` (related=employee_id.user_id)

### Non-persisted fields
- _none_

## ppm.risk

- Module: `ipai`
- Model type: `Model`
- Table: `ppm_risk`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `assigned_to_id`: `Many2one` (relation=res.users)
- `category`: `Selection` (required)
- `code`: `Char`
- `contingency_plan`: `Text`
- `currency_id`: `Many2one` (relation=res.currency)
- `date_closed`: `Date`
- `date_identified`: `Date`
- `date_target`: `Date`
- `description`: `Text`
- `impact`: `Selection` (required)
- `mitigation_plan`: `Text`
- `mitigation_strategy`: `Selection`
- `name`: `Char` (required)
- `owner_id`: `Many2one` (relation=res.users)
- `portfolio_id`: `Many2one` (relation=ppm.portfolio)
- `potential_cost`: `Monetary`
- `probability`: `Selection` (required)
- `program_id`: `Many2one` (relation=ppm.program)
- `project_id`: `Many2one` (relation=project.project)
- `risk_score`: `Integer` (compute=_compute_risk_score)
- `scope`: `Selection` (required)
- `severity`: `Selection` (compute=_compute_risk_score)
- `status`: `Selection`

### Non-persisted fields
- _none_

## product.product

- Module: `sale_project_task_recurrency`
- Model type: `Model`
- Table: `product_product`
- _inherit: `product.product`

### Persisted fields

### Non-persisted fields
- _none_

## product.set.line

- Module: `project_task_stock_product_set`
- Model type: `Model`
- Table: `product_set_line`
- _inherit: `product.set.line`

### Persisted fields

### Non-persisted fields
- _none_

## product.template

- Module: `sale_project_copy_tasks`
- Model type: `Model`
- Table: `product_template`
- _inherit: `product.template`

### Persisted fields
- `recurring_task`: `Boolean`
- `service_tracking`: `Selection`
- `task_force_month`: `Selection`
- `task_force_month_quarter`: `Selection`
- `task_force_month_semester`: `Selection`
- `task_repeat_interval`: `Integer`
- `task_repeat_number`: `Integer`
- `task_repeat_type`: `Selection`
- `task_repeat_unit`: `Selection`
- `task_repeat_until`: `Date`
- `task_start_date_method`: `Selection`

### Non-persisted fields
- _none_

## project.assignment

- Module: `project_role`
- Model type: `Model`
- Table: `project_assignment`
- _inherit: `mail.thread`
- SQL constraints:
  - `company_role_user_uniq`: `EXCLUDE (    company_id WITH =, role_id WITH =, user_id WITH =) WHERE (    project_id IS NULL)` (User may be assigned per role only once within a company!)
  - `nocompany_role_user_uniq`: `EXCLUDE (role_id WITH =, user_id WITH =) WHERE (    project_id IS NULL AND company_id IS NULL)` (User may be assigned per role only once!)
  - `project_role_user_uniq`: `UNIQUE (project_id, role_id, user_id)` (User may be assigned per role only once within a project!)
- Python constraints:
  - `_check`

### Persisted fields
- `active`: `Boolean`
- `company_id`: `Many2one` (ondelete=cascade)
- `name`: `Char` (compute=_compute_name, index)
- `project_id`: `Many2one` (ondelete=cascade)
- `role_id`: `Many2one` (required, ondelete=restrict)
- `user_id`: `Many2one` (required, ondelete=restrict)

### Non-persisted fields
- _none_

## project.milestone

- Module: `ipai`
- Model type: `Model`
- Table: `project_milestone`
- _inherit: `project.milestone`
- Python constraints:
  - `_check_deadlines`

### Persisted fields
- `alert_days_before`: `Integer`
- `approval_date`: `Date`
- `approval_required`: `Boolean`
- `approver_id`: `Many2one` (relation=res.users)
- `baseline_deadline`: `Date`
- `completed_task_count`: `Integer` (compute=_compute_task_count)
- `completion_criteria`: `Text`
- `dedication`: `Integer` (compute=_compute_dedication)
- `deliverables`: `Text`
- `execution`: `Integer` (compute=_compute_execution)
- `gate_status`: `Selection`
- `last_alert_sent`: `Date`
- `milestone_type`: `Selection` (required)
- `risk_level`: `Selection`
- `risk_notes`: `Text`
- `task_count`: `Integer` (compute=_compute_task_count)
- `variance_days`: `Integer` (compute=_compute_variance)

### Non-persisted fields
- `task_ids`: `One2many` (relation=project.task)

## project.project

- Module: `ipai`
- Model type: `Model`
- Table: `project_project`
- _inherit: `hr.timesheet.time_control.mixin, project.project`
- SQL constraints:
  - `name_required`: `CHECK(name IS NOT NULL)` (Project name is required)
  - `project_key_unique`: `UNIQUE(key)` (Project key must be unique)
  - `sequence_code_unique`: `UNIQUE(sequence_code)` (Sequence code must be unique)

### Persisted fields
- `actual_finish`: `Date`
- `actual_start`: `Date`
- `baseline_finish`: `Date`
- `baseline_start`: `Date`
- `child_ids_count`: `Integer` (compute=_compute_child_ids_count)
- `clarity_id`: `Char` (required, index)
- `critical_milestone_count`: `Integer` (compute=_compute_milestone_stats)
- `department_id`: `Many2one`
- `group_ids`: `Many2many` (relation=res.groups)
- `health_status`: `Selection` (required)
- `hr_category_ids`: `Many2many`
- `im_code`: `Char` (index)
- `inherit_assignments`: `Boolean`
- `ipai_finance_enabled`: `Boolean`
- `ipai_im_code`: `Selection` (index)
- `ipai_is_im_project`: `Boolean` (index)
- `ipai_root_project_id`: `Many2one` (relation=project.project, index, ondelete=set null)
- `is_program`: `Boolean` (index)
- `is_template`: `Boolean`
- `key`: `Char` (index)
- `limit_role_to_assignments`: `Boolean`
- `location_dest_id`: `Many2one` (index)
- `location_id`: `Many2one` (index)
- `milestone_count`: `Integer` (compute=_compute_milestone_stats)
- `name`: `Char`
- `overall_progress`: `Float` (compute=_compute_overall_progress)
- `overall_status`: `Selection` (compute=_compute_overall_status)
- `parent_id`: `Many2one` (index)
- `parent_path`: `Char`
- `phase_count`: `Integer` (compute=_compute_phase_stats)
- `picking_type_id`: `Many2one` (index)
- `portfolio_id`: `Many2one` (relation=project.category)
- `ppm_program_ids`: `Many2many` (relation=ppm.program)
- `pr_required_states`: `Many2many` (relation=project.task.type)
- `program_code`: `Char` (index)
- `program_type`: `Selection` (index)
- `purchase_count`: `Integer` (compute=_compute_purchase_info)
- `purchase_invoice_count`: `Integer` (compute=_compute_purchase_invoice_info)
- `purchase_invoice_line_total`: `Float` (compute=_compute_purchase_invoice_info)
- `purchase_line_total`: `Integer` (compute=_compute_purchase_info)
- `sequence_code`: `Char`
- `stage_last_update_date`: `Datetime`
- `stock_analytic_date`: `Date`
- `tag_ids`: `Many2many`
- `task_key_sequence_id`: `Many2one` (ondelete=restrict)
- `type_id`: `Many2one`
- `type_ids`: `Many2many`
- `variance_finish`: `Integer` (compute=_compute_variances)
- `variance_start`: `Integer` (compute=_compute_variances)
- `x_cycle_code`: `Char` (index)

### Non-persisted fields
- `assignment_ids`: `One2many`
- `child_ids`: `One2many`
- `im_count`: `Integer` (compute=_compute_im_rollups)
- `im_task_count`: `Integer` (compute=_compute_im_rollups)
- `show_key_warning`: `Boolean` (compute=_compute_show_key_warning)
- `stakeholder_ids`: `One2many` (relation=project.stakeholder)
- `version_ids`: `One2many`

## project.role

- Module: `project_role`
- Model type: `Model`
- Table: `project_role`
- SQL constraints:
  - `name_company_uniq`: `UNIQUE (name, company_id)` (Role with such name already exists in the company!)
  - `name_nocompany_uniq`: `EXCLUDE (name WITH =) WHERE (    company_id IS NULL)` (Shared role with such name already exists!)
- Python constraints:
  - `_check_active`
  - `_check_name`

### Persisted fields
- `active`: `Boolean`
- `company_id`: `Many2one` (ondelete=cascade)
- `complete_name`: `Char` (compute=_compute_complete_name)
- `description`: `Html`
- `name`: `Char` (required)
- `parent_id`: `Many2one` (index, ondelete=cascade)
- `parent_path`: `Char` (index)

### Non-persisted fields
- `child_ids`: `One2many`

## project.stakeholder

- Module: `project_stakeholder`
- Model type: `Model`
- Table: `project_stakeholder`

### Persisted fields
- `note`: `Text`
- `partner_id`: `Many2one` (relation=res.partner, required, index, ondelete=cascade)
- `project_id`: `Many2one` (relation=project.project, required, index, ondelete=cascade)
- `role_id`: `Many2one` (relation=project.stakeholder.role, required, ondelete=restrict)

### Non-persisted fields
- _none_

## project.stakeholder.role

- Module: `project_stakeholder`
- Model type: `Model`
- Table: `project_stakeholder_role`

### Persisted fields
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## project.tags

- Module: `project_tag_hierarchy`
- Model type: `Model`
- Table: `project_tags`
- _inherit: `project.tags`
- Python constraints:
  - `_check_parent_id`

### Persisted fields
- `allowed_project_ids`: `Many2many`
- `company_id`: `Many2one`
- `parent_id`: `Many2one` (index, ondelete=cascade)
- `parent_path`: `Char` (index)

### Non-persisted fields
- `child_ids`: `One2many`

## project.task

- Module: `ipai`
- Model type: `Model`
- Table: `project_task`
- _inherit: `analytic.mixin, hr.timesheet.time_control.mixin, project.task`
- SQL constraints:
  - `project_task_unique_code`: `UNIQUE (company_id, code)` (The code must be unique!)
  - `task_key_unique`: `UNIQUE(key)` (Task key must be unique!)
- Python constraints:
  - `_check_employee_category_project`
  - `_check_employee_category_user`
  - `_check_phase_hierarchy`
  - `_check_planned_dates`
  - `_check_pr_uri_required`
  - `_check_subtasks_done_before_closing`

### Persisted fields
- `activity_type`: `Selection` (index)
- `actual_cost`: `Float`
- `actual_hours`: `Float` (compute=_compute_actual_hours)
- `allow_moves_action_assign`: `Boolean` (compute=_compute_allow_moves_action_assign)
- `allow_moves_action_confirm`: `Boolean` (compute=_compute_allow_moves_action_confirm)
- `ancestor_id`: `Many2one` (compute=_compute_ancestor_id)
- `approval_duration`: `Float`
- `approver_id`: `Many2one` (relation=res.users)
- `auto_sync`: `Boolean`
- `bir_approval_due_date`: `Date`
- `bir_deadline`: `Date`
- `bir_form`: `Char` (index)
- `bir_payment_due_date`: `Date`
- `bir_period_label`: `Char`
- `bir_prep_due_date`: `Date`
- `bir_related`: `Boolean`
- `bir_schedule_id`: `Many2one` (relation=ipai.finance.bir_schedule)
- `child_task_count`: `Integer` (compute=_compute_child_task_count)
- `closing_due_date`: `Date`
- `cluster`: `Selection`
- `code`: `Char` (required)
- `cost_variance`: `Float` (compute=_compute_variances)
- `critical_path`: `Boolean` (compute=_compute_critical_path, index)
- `description_template_id`: `Many2one` (relation=project.task.description.template)
- `domain_hr_category_ids`: `Binary` (compute=_compute_domain_hr_category_ids)
- `domain_user_ids`: `Binary` (compute=_compute_domain_user_ids)
- `done_stock_moves`: `Boolean` (related=stage_id.done_stock_moves)
- `earned_value`: `Float` (compute=_compute_earned_value)
- `employee_ids`: `Many2many` (compute=_compute_employee_ids)
- `erp_ref`: `Char`
- `fd_id`: `Many2one` (relation=res.users)
- `finance_category`: `Selection`
- `finance_code`: `Char`
- `finance_deadline_type`: `Selection`
- `finance_logframe_id`: `Many2one` (relation=ipai.finance.logframe)
- `finance_person_id`: `Many2one` (relation=ipai.finance.person)
- `finance_supervisor_id`: `Many2one` (relation=res.users)
- `free_float`: `Integer` (compute=_compute_float)
- `gate_approver_id`: `Many2one` (relation=res.users)
- `gate_decision`: `Selection`
- `gate_milestone_id`: `Many2one` (relation=project.milestone)
- `group_id`: `Many2one`
- `has_gate`: `Boolean`
- `hr_category_ids`: `Many2many`
- `ipai_compliance_step`: `Selection` (index)
- `ipai_days_to_deadline`: `Integer` (compute=_compute_ipai_deadline_metrics)
- `ipai_owner_code`: `Char` (index)
- `ipai_owner_role`: `Selection` (index)
- `ipai_status_bucket`: `Selection` (compute=_compute_ipai_deadline_metrics, index)
- `ipai_task_category`: `Selection` (index)
- `ipai_template_id`: `Many2one` (relation=ipai.finance.task.template, index, ondelete=set null)
- `is_finance_ppm`: `Boolean` (compute=_compute_is_finance_ppm)
- `is_phase`: `Boolean` (index)
- `key`: `Char` (index)
- `lag_days`: `Integer`
- `lead_days`: `Integer`
- `location_dest_id`: `Many2one` (index)
- `location_id`: `Many2one` (index)
- `milestone_count`: `Integer` (compute=_compute_milestone_count)
- `notes`: `Html`
- `owner_code`: `Char`
- `period_covered`: `Char` (index)
- `phase_baseline_finish`: `Date`
- `phase_baseline_start`: `Date`
- `phase_progress`: `Float` (compute=_compute_phase_progress)
- `phase_status`: `Selection`
- `phase_type`: `Selection`
- `phase_variance_days`: `Integer` (compute=_compute_phase_variance)
- `picking_type_id`: `Many2one` (index)
- `planned_date_end`: `Datetime` (compute=_compute_planned_date_end)
- `planned_date_start`: `Datetime` (compute=_compute_planned_date_start)
- `planned_hours`: `Float`
- `planned_value`: `Float`
- `portal_url`: `Char` (compute=_compute_portal_url)
- `portal_url_visible`: `Boolean` (compute=_compute_portal_url)
- `pr_required_states`: `Many2many` (related=project_id.pr_required_states)
- `pr_uri`: `Char`
- `prep_duration`: `Float`
- `priority`: `Selection`
- `project_department_id`: `Many2one` (related=project_id.department_id)
- `relative_due`: `Char`
- `remaining_hours`: `Float`
- `resource_allocation`: `Float`
- `review_duration`: `Float`
- `reviewer_id`: `Many2one` (relation=res.users)
- `role_code`: `Char` (index)
- `schedule_variance`: `Float` (compute=_compute_variances)
- `scrap_count`: `Integer` (compute=_compute_scrap_move_count)
- `sfm_id`: `Many2one` (relation=res.users)
- `stage_id`: `Many2one`
- `stock_analytic_account_id`: `Many2one`
- `stock_analytic_date`: `Date`
- `stock_analytic_distribution`: `Json`
- `stock_moves_is_locked`: `Boolean`
- `stock_state`: `Selection` (compute=_compute_stock_state)
- `tag_ids`: `Many2many`
- `target_date`: `Date` (index)
- `total_float`: `Integer` (compute=_compute_float)
- `type_id`: `Many2one`
- `unreserve_visible`: `Boolean` (compute=_compute_unreserve_visible)
- `url`: `Char` (compute=_compute_task_url)
- `use_stock_moves`: `Boolean` (related=stage_id.use_stock_moves)
- `user_ids`: `Many2many`
- `version_id`: `Many2one`
- `wbs_code`: `Char` (compute=_compute_wbs_code)
- `x_cycle_key`: `Char` (index)
- `x_external_key`: `Char` (index)
- `x_obsolete`: `Boolean` (index)
- `x_seed_hash`: `Char` (index)
- `x_step_code`: `Char` (index)
- `x_task_template_code`: `Char` (index)

### Non-persisted fields
- `move_ids`: `One2many`
- `scrap_ids`: `One2many`
- `stock_analytic_line_ids`: `One2many`

## project.task.checklist.item

- Module: `ipai`
- Model type: `Model`
- Table: `project_task_checklist_item`
- _inherit: `project.task.checklist.item`

### Persisted fields
- `actual_hours`: `Float`
- `assigned_user_id`: `Many2one` (relation=res.users)
- `blocker_description`: `Text`
- `completed_date`: `Date`
- `due_date`: `Date`
- `estimated_hours`: `Float`
- `notes`: `Text`
- `priority`: `Selection`
- `status`: `Selection` (compute=_compute_status)

### Non-persisted fields
- _none_

## project.task.description.template

- Module: `project_task_description_template`
- Model type: `Model`
- Table: `project_task_description_template`

### Persisted fields
- `active`: `Boolean`
- `company_id`: `Many2one` (relation=res.company)
- `description`: `Html` (required)
- `name`: `Char` (required)

### Non-persisted fields
- _none_

## project.task.merge

- Module: `project_merge`
- Model type: `TransientModel`
- Table: `project_task_merge`

### Persisted fields
- `create_new_task`: `Boolean`
- `dst_project_id`: `Many2one` (relation=project.project)
- `dst_task_id`: `Many2one` (relation=project.task)
- `dst_task_name`: `Char`
- `task_ids`: `Many2many` (relation=project.task, required)
- `user_ids`: `Many2many` (relation=res.users)

### Non-persisted fields
- _none_

## project.task.stock.product.set.wizard

- Module: `project_task_stock_product_set`
- Model type: `TransientModel`
- Table: `project_task_stock_product_set_wizard`
- _inherit: `product.set.wizard`

### Persisted fields
- `task_id`: `Many2one` (required, ondelete=cascade)

### Non-persisted fields
- _none_

## project.task.type

- Module: `project_task_default_stage`
- Model type: `Model`
- Table: `project_task_type`
- _inherit: `project.task.type`

### Persisted fields
- `case_default`: `Boolean`
- `done_stock_moves`: `Boolean`
- `task_state`: `Selection`
- `use_stock_moves`: `Boolean`

### Non-persisted fields
- _none_

## project.type

- Module: `project_type`
- Model type: `Model`
- Table: `project_type`
- Python constraints:
  - `check_parent_id`

### Persisted fields
- `code`: `Char`
- `complete_name`: `Char` (compute=_compute_complete_name)
- `description`: `Text`
- `name`: `Char` (required)
- `parent_id`: `Many2one`
- `project_ok`: `Boolean`
- `task_ok`: `Boolean`

### Non-persisted fields
- `child_ids`: `One2many`

## project.version

- Module: `project_version`
- Model type: `Model`
- Table: `project_version`

### Persisted fields
- `name`: `Char` (required)
- `project_id`: `Many2one` (required)

### Non-persisted fields
- _none_

## purchase.order

- Module: `ipai`
- Model type: `Model`
- Table: `purchase_order`
- _inherit: `master.control.mixin, purchase.order`

### Persisted fields
- `x_master_control_submitted`: `Boolean`

### Non-persisted fields
- _none_

## quick.start.screen

- Module: `web_quick_start_screen`
- Model type: `Model`
- Table: `quick_start_screen`

### Persisted fields
- `action_ids`: `Many2many`
- `name`: `Char`

### Non-persisted fields
- _none_

## quick.start.screen.action

- Module: `web_quick_start_screen`
- Model type: `Model`
- Table: `quick_start_screen_action`

### Persisted fields
- `action_ref_id`: `Reference` (required)
- `active`: `Boolean`
- `color`: `Integer`
- `context`: `Char`
- `description`: `Html`
- `domain`: `Char`
- `icon_name`: `Char`
- `image`: `Image` (relation=Start screen icon)
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## report.a_f_r.report_aged_partner_balance_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_a_f_r_report_aged_partner_balance_xlsx`
- _inherit: `report.account_financial_report.abstract_report_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.a_f_r.report_general_ledger_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_a_f_r_report_general_ledger_xlsx`
- _inherit: `report.account_financial_report.abstract_report_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.a_f_r.report_journal_ledger_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_a_f_r_report_journal_ledger_xlsx`
- _inherit: `report.account_financial_report.abstract_report_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.a_f_r.report_open_items_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_a_f_r_report_open_items_xlsx`
- _inherit: `report.account_financial_report.abstract_report_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.a_f_r.report_trial_balance_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_a_f_r_report_trial_balance_xlsx`
- _inherit: `report.account_financial_report.abstract_report_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.a_f_r.report_vat_report_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_a_f_r_report_vat_report_xlsx`
- _inherit: `report.account_financial_report.abstract_report_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.abstract_report

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_abstract_report`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.abstract_report_xlsx

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_abstract_report_xlsx`
- _inherit: `report.report_xlsx.abstract`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.aged_partner_balance

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_aged_partner_balance`
- _inherit: `report.account_financial_report.abstract_report`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.general_ledger

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_general_ledger`
- _inherit: `report.account_financial_report.abstract_report`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.journal_ledger

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_journal_ledger`
- _inherit: `report.account_financial_report.abstract_report`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.open_items

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_open_items`
- _inherit: `report.account_financial_report.abstract_report, report.account_financial_report.open_items`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.trial_balance

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_trial_balance`
- _inherit: `report.account_financial_report.abstract_report`

### Persisted fields

### Non-persisted fields
- _none_

## report.account_financial_report.vat_report

- Module: `account_financial_report`
- Model type: `AbstractModel`
- Table: `report_account_financial_report_vat_report`
- _inherit: `report.account_financial_report.abstract_report`

### Persisted fields

### Non-persisted fields
- _none_

## report.p_s.report_activity_statement_xlsx

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `report_p_s_report_activity_statement_xlsx`
- _inherit: `report.report_xlsx.abstract`

### Persisted fields

### Non-persisted fields
- _none_

## report.p_s.report_detailed_activity_statement_xlsx

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `report_p_s_report_detailed_activity_statement_xlsx`
- _inherit: `report.p_s.report_activity_statement_xlsx`

### Persisted fields

### Non-persisted fields
- _none_

## report.p_s.report_outstanding_statement_xlsx

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `report_p_s_report_outstanding_statement_xlsx`
- _inherit: `report.report_xlsx.abstract`

### Persisted fields

### Non-persisted fields
- _none_

## report.partner_statement.activity_statement

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `report_partner_statement_activity_statement`
- _inherit: `statement.common`

### Persisted fields

### Non-persisted fields
- _none_

## report.partner_statement.detailed_activity_statement

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `report_partner_statement_detailed_activity_statement`
- _inherit: `report.partner_statement.activity_statement`

### Persisted fields

### Non-persisted fields
- _none_

## report.partner_statement.outstanding_statement

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `report_partner_statement_outstanding_statement`
- _inherit: `statement.common`

### Persisted fields

### Non-persisted fields
- _none_

## report.project.task.user

- Module: `project_task_ancestor`
- Model type: `Model`
- Table: `report_project_task_user`
- _inherit: `report.project.task.user`

### Persisted fields
- `ancestor_id`: `Many2one`
- `planned_date_end`: `Datetime`
- `planned_date_start`: `Datetime`

### Non-persisted fields
- _none_

## report.xlsx.wizard

- Module: `excel_import_export`
- Model type: `TransientModel`
- Table: `report_xlsx_wizard`

### Persisted fields
- `domain`: `Char`
- `res_model`: `Char`

### Non-persisted fields
- _none_

## res.company

- Module: `account_reconcile_oca`
- Model type: `Model`
- Table: `res_company`
- _inherit: `res.company`

### Persisted fields
- `account_auto_reconcile_queue`: `Boolean`
- `color_button_bg`: `Char` (relation=Button Background Color)
- `color_button_bg_hover`: `Char` (relation=Button Background Color Hover)
- `color_button_text`: `Char` (relation=Button Text Color)
- `color_link_text`: `Char` (relation=Link Text Color)
- `color_link_text_hover`: `Char` (relation=Link Text Color Hover)
- `color_navbar_bg`: `Char` (relation=Navbar Background Color)
- `color_navbar_bg_hover`: `Char` (relation=Navbar Background Color Hover)
- `color_navbar_text`: `Char` (relation=Navbar Text Color)
- `color_submenu_text`: `Char` (relation=Submenu Text Color)
- `company_colors`: `Serialized`
- `favicon`: `Binary`
- `project_inherit_assignments`: `Boolean`
- `project_limit_role_to_assignments`: `Boolean`
- `reconcile_aggregate`: `Selection`
- `scss_modif_timestamp`: `Char` (relation=SCSS Modif. Timestamp)
- `user_tech_id`: `Many2one`

### Non-persisted fields
- _none_

## res.config.settings

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `res_config_settings`
- _inherit: `res.config.settings`

### Persisted fields
- `account_auto_reconcile_queue`: `Boolean` (related=company_id.account_auto_reconcile_queue)
- `age_partner_config_id`: `Many2one` (relation=account.age.report.configuration)
- `database_size_purge`: `Boolean`
- `database_size_retention_daily`: `Integer`
- `database_size_retention_monthly`: `Integer`
- `default_aging_type`: `Selection` (required)
- `default_filter_negative_balances`: `Boolean` (relation=Exclude Negative Balances)
- `default_filter_partners_non_due`: `Boolean`
- `default_show_aging_buckets`: `Boolean`
- `excluded_models_from_readonly`: `Char` (relation=Excluded Models from Read-only)
- `group_activity_statement`: `Boolean` (relation=Enable OCA Activity & Detailed Activity Statements)
- `group_outstanding_statement`: `Boolean` (relation=Enable OCA Outstanding Statements)
- `ipai_enable_finance_project_analytics`: `Boolean`
- `project_display_name_pattern`: `Char`
- `project_inherit_assignments`: `Boolean` (related=company_id.project_inherit_assignments)
- `project_limit_role_to_assignments`: `Boolean` (related=company_id.project_limit_role_to_assignments)
- `pwa_background_color`: `Char` (relation=Background Color)
- `pwa_icon`: `Binary` (relation=Icon)
- `pwa_short_name`: `Char` (relation=Web App Short Name)
- `pwa_theme_color`: `Char` (relation=Theme Color)
- `reconcile_aggregate`: `Selection` (related=company_id.reconcile_aggregate)
- `session_auto_close_timeout`: `Integer`
- `superset_auto_sync`: `Boolean`
- `superset_connection_id`: `Many2one` (relation=superset.connection)
- `superset_create_analytics_views`: `Boolean`
- `superset_enable_rls`: `Boolean`
- `superset_sync_interval`: `Selection`

### Non-persisted fields
- _none_

## res.partner

- Module: `account_move_base_import`
- Model type: `Model`
- Table: `res_partner`
- _inherit: `res.partner`
- Python constraints:
  - `_check_tin_format`

### Persisted fields
- `bank_statement_label`: `Char`
- `bir_registered`: `Boolean`
- `bir_registration_date`: `Date`
- `srm_overall_score`: `Float` (related=srm_supplier_id.overall_score)
- `srm_supplier_id`: `Many2one` (relation=srm.supplier)
- `srm_tier`: `Selection` (related=srm_supplier_id.tier)
- `tax_type`: `Selection`
- `tin`: `Char` (index)
- `tin_branch_code`: `Char`

### Non-persisted fields
- `stakeholder_ids`: `One2many` (relation=project.stakeholder)
- `time_window_ids`: `One2many`

## res.remote

- Module: `base_remote`
- Model type: `Model`
- Table: `res_remote`
- SQL constraints:
  - `name_unique`: `unique(name)` (Hostname must be unique)

### Persisted fields
- `in_network`: `Boolean` (required)
- `ip`: `Char` (required)
- `name`: `Char` (required, index)

### Non-persisted fields
- _none_

## res.users

- Module: `base_model_restrict_update`
- Model type: `Model`
- Table: `res_users`
- _inherit: `res.users`
- SQL constraints:
  - `x_employee_code_uniq`: `UNIQUE(x_employee_code)` (Employee code must be unique)
  - `x_employee_code_uniq`: `UNIQUE(x_employee_code)` (Employee code must be unique)
  - `x_employee_code_unique`: `unique(x_employee_code)` (Employee code must be unique when set!)
  - `x_employee_code_unique`: `unique(x_employee_code)` (Employee code must be unique when set!)
- Python constraints:
  - `_check_is_readonly_user`

### Persisted fields
- `apps_menu_search_type`: `Selection` (required)
- `apps_menu_theme`: `Selection` (required)
- `chatter_position`: `Selection`
- `hr_category_ids`: `Many2many` (compute=_compute_hr_category_ids)
- `is_readonly_user`: `Boolean` (relation=Read-only User)
- `is_redirect_home`: `Boolean` (compute=_compute_redirect_home)
- `notify_danger_channel_name`: `Char` (compute=_compute_channel_names)
- `notify_default_channel_name`: `Char` (compute=_compute_channel_names)
- `notify_info_channel_name`: `Char` (compute=_compute_channel_names)
- `notify_success_channel_name`: `Char` (compute=_compute_channel_names)
- `notify_warning_channel_name`: `Char` (compute=_compute_channel_names)
- `quick_start_screen_id`: `Many2one`
- `x_employee_code`: `Char` (index)

### Non-persisted fields
- _none_

## sale.order

- Module: `base_transaction_id`
- Model type: `Model`
- Table: `sale_order`
- _inherit: `sale.order`

### Persisted fields
- `has_project_service_tracking_lines`: `Boolean` (compute=_compute_has_project_service_tracking_lines)
- `transaction_id`: `Char` (relation=Transaction ID)

### Non-persisted fields
- _none_

## sale.order.line

- Module: `sale_project_copy_tasks`
- Model type: `Model`
- Table: `sale_order_line`
- _inherit: `sale.order.line`

### Persisted fields
- `is_project_service_tracking_line`: `Boolean` (compute=_compute_is_project_service_tracking_line)

### Non-persisted fields
- _none_

## srm.kpi.category

- Module: `ipai`
- Model type: `Model`
- Table: `srm_kpi_category`

### Persisted fields
- `active`: `Boolean`
- `code`: `Char` (required)
- `compute_source`: `Selection`
- `description`: `Text`
- `eval_method`: `Selection`
- `name`: `Char` (required)
- `sequence`: `Integer`
- `weight`: `Float`

### Non-persisted fields
- _none_

## srm.qualification

- Module: `ipai`
- Model type: `Model`
- Table: `srm_qualification`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `approval_date`: `Datetime`
- `approver_id`: `Many2one` (relation=res.users)
- `checklist_complete`: `Boolean` (compute=_compute_checklist_complete)
- `completion_date`: `Date`
- `document_ids`: `Many2many` (relation=ir.attachment)
- `expiry_date`: `Date`
- `name`: `Char` (compute=_compute_name)
- `notes`: `Text`
- `qualification_type`: `Selection` (required)
- `rejection_reason`: `Text`
- `reviewer_id`: `Many2one` (relation=res.users)
- `risk_notes`: `Text`
- `risk_score`: `Float`
- `start_date`: `Date`
- `state`: `Selection`
- `supplier_id`: `Many2one` (relation=srm.supplier, required)
- `target_completion`: `Date`

### Non-persisted fields
- `checklist_ids`: `One2many` (relation=srm.qualification.checklist)

## srm.qualification.checklist

- Module: `ipai`
- Model type: `Model`
- Table: `srm_qualification_checklist`

### Persisted fields
- `completed_by`: `Many2one` (relation=res.users)
- `completed_date`: `Date`
- `description`: `Text`
- `is_complete`: `Boolean`
- `is_required`: `Boolean`
- `name`: `Char` (required)
- `notes`: `Text`
- `qualification_id`: `Many2one` (relation=srm.qualification, required, ondelete=cascade)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## srm.scorecard

- Module: `ipai`
- Model type: `Model`
- Table: `srm_scorecard`
- _inherit: `mail.thread`

### Persisted fields
- `action_items`: `Text`
- `as_of`: `Date` (required)
- `comments`: `Text`
- `evaluator_id`: `Many2one` (relation=res.users)
- `grade`: `Selection` (compute=_compute_grade)
- `name`: `Char` (compute=_compute_name)
- `overall_score`: `Float` (compute=_compute_overall_score)
- `period`: `Selection`
- `state`: `Selection`
- `supplier_id`: `Many2one` (relation=srm.supplier, required)

### Non-persisted fields
- `line_ids`: `One2many` (relation=srm.scorecard.line)

## srm.scorecard.line

- Module: `ipai`
- Model type: `Model`
- Table: `srm_scorecard_line`

### Persisted fields
- `evidence`: `Text`
- `kpi_category_id`: `Many2one` (relation=srm.kpi.category, required)
- `notes`: `Text`
- `score`: `Float`
- `scorecard_id`: `Many2one` (relation=srm.scorecard, required, ondelete=cascade)
- `sequence`: `Integer` (related=kpi_category_id.sequence)
- `weight`: `Float`
- `weighted_score`: `Float` (compute=_compute_weighted_score)

### Non-persisted fields
- _none_

## srm.supplier

- Module: `ipai`
- Model type: `Model`
- Table: `srm_supplier`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `category_ids`: `Many2many` (relation=product.category)
- `code`: `Char`
- `compliance_docs_complete`: `Boolean`
- `currency_id`: `Many2one` (relation=res.currency)
- `is_qualified`: `Boolean` (compute=_compute_is_qualified)
- `last_audit_date`: `Date`
- `latest_scorecard_id`: `Many2one` (relation=srm.scorecard, compute=_compute_latest_scorecard)
- `name`: `Char` (required)
- `next_audit_date`: `Date`
- `open_po_count`: `Integer` (compute=_compute_po_stats)
- `overall_score`: `Float` (compute=_compute_overall_score)
- `partner_id`: `Many2one` (relation=res.partner, required)
- `primary_contact_id`: `Many2one` (relation=res.partner)
- `qualification_expiry`: `Date`
- `risk_level`: `Selection`
- `risk_notes`: `Text`
- `sales_contact_id`: `Many2one` (relation=res.partner)
- `state`: `Selection`
- `tier`: `Selection`
- `total_po_count`: `Integer` (compute=_compute_po_stats)
- `ytd_spend`: `Monetary` (compute=_compute_ytd_spend)

### Non-persisted fields
- `qualification_ids`: `One2many` (relation=srm.qualification)
- `scorecard_ids`: `One2many` (relation=srm.scorecard)

## statement.common

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `statement_common`

### Persisted fields

### Non-persisted fields
- _none_

## statement.common.wizard

- Module: `partner_statement`
- Model type: `AbstractModel`
- Table: `statement_common_wizard`

### Persisted fields
- `account_type`: `Selection`
- `aging_type`: `Selection` (required)
- `company_id`: `Many2one` (required)
- `date_end`: `Date` (required)
- `excluded_accounts_selector`: `Char`
- `filter_negative_balances`: `Boolean` (relation=Exclude Negative Balances)
- `filter_partners_non_due`: `Boolean`
- `name`: `Char`
- `number_partner_ids`: `Integer`
- `show_aging_buckets`: `Boolean`
- `show_only_overdue`: `Boolean`

### Non-persisted fields
- _none_

## stock.move

- Module: `project_task_stock`
- Model type: `Model`
- Table: `stock_move`
- _inherit: `stock.move`

### Persisted fields
- `raw_material_task_id`: `Many2one`
- `show_cancel_button_in_task`: `Boolean` (compute=_compute_show_cancel_button_in_task)
- `task_id`: `Many2one`

### Non-persisted fields
- `analytic_line_ids`: `One2many`

## stock.move.line

- Module: `project_task_stock`
- Model type: `Model`
- Table: `stock_move_line`
- _inherit: `stock.move.line`

### Persisted fields
- `task_id`: `Many2one` (compute=_compute_task_id)

### Non-persisted fields
- _none_

## stock.scrap

- Module: `project_task_stock`
- Model type: `Model`
- Table: `stock_scrap`
- _inherit: `stock.scrap`

### Persisted fields
- `task_id`: `Many2one`

### Non-persisted fields
- _none_

## superset.analytics.view

- Module: `ipai_superset_connector`
- Model type: `Model`
- Table: `superset_analytics_view`

### Persisted fields
- `active`: `Boolean`
- `category`: `Selection` (required)
- `description`: `Text`
- `is_created`: `Boolean`
- `last_refresh`: `Datetime`
- `name`: `Char` (required)
- `required_modules`: `Char`
- `sequence`: `Integer`
- `sql_definition`: `Text` (required)
- `technical_name`: `Char` (required)

### Non-persisted fields
- _none_

## superset.bulk.dataset.wizard

- Module: `ipai_superset_connector`
- Model type: `TransientModel`
- Table: `superset_bulk_dataset_wizard`

### Persisted fields
- `connection_id`: `Many2one` (relation=superset.connection, required)
- `create_analytics_views`: `Boolean`
- `preset`: `Selection`

### Non-persisted fields
- _none_

## superset.connection

- Module: `ipai_superset_connector`
- Model type: `Model`
- Table: `superset_connection`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `access_token`: `Char`
- `active`: `Boolean`
- `api_key`: `Char`
- `auth_method`: `Selection` (required)
- `base_url`: `Char` (required)
- `csrf_token`: `Char`
- `dataset_count`: `Integer` (compute=_compute_dataset_count)
- `db_connection_id`: `Integer`
- `db_connection_name`: `Char`
- `last_error`: `Text`
- `last_sync`: `Datetime`
- `name`: `Char` (required)
- `password`: `Char`
- `pg_database`: `Char`
- `pg_host`: `Char`
- `pg_password`: `Char`
- `pg_port`: `Integer`
- `pg_schema`: `Char`
- `pg_username`: `Char`
- `refresh_token`: `Char`
- `state`: `Selection`
- `token_expiry`: `Datetime`
- `use_ssl`: `Boolean`
- `username`: `Char`

### Non-persisted fields
- `dataset_ids`: `One2many` (relation=superset.dataset)

## superset.dataset

- Module: `ipai_superset_connector`
- Model type: `Model`
- Table: `superset_dataset`
- _inherit: `mail.thread, mail.activity.mixin`
- SQL constraints:
  - `technical_name_uniq`: `unique(technical_name)` (Technical name must be unique!)

### Persisted fields
- `active`: `Boolean`
- `category`: `Selection`
- `column_count`: `Integer` (compute=_compute_column_count)
- `connection_id`: `Many2one` (relation=superset.connection, required, ondelete=cascade)
- `custom_sql`: `Text`
- `description`: `Text`
- `enable_rls`: `Boolean`
- `field_ids`: `Many2many` (relation=ir.model.fields)
- `include_all_fields`: `Boolean`
- `last_sync`: `Datetime`
- `model_id`: `Many2one` (relation=ir.model)
- `model_name`: `Char` (related=model_id.model)
- `name`: `Char` (required)
- `rls_filter_column`: `Char`
- `sequence`: `Integer`
- `source_type`: `Selection` (required)
- `superset_dataset_id`: `Integer`
- `sync_error`: `Text`
- `sync_status`: `Selection`
- `technical_name`: `Char` (required)
- `view_created`: `Boolean`
- `view_name`: `Char` (compute=_compute_view_name)
- `view_sql`: `Text`

### Non-persisted fields
- _none_

## superset.dataset.column

- Module: `ipai_superset_connector`
- Model type: `Model`
- Table: `superset_dataset_column`

### Persisted fields
- `aggregation`: `Selection`
- `column_type`: `Selection`
- `data_type`: `Selection`
- `dataset_id`: `Many2one` (relation=superset.dataset, required, ondelete=cascade)
- `description`: `Text`
- `filterable`: `Boolean`
- `format_string`: `Char`
- `groupable`: `Boolean`
- `label`: `Char`
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## superset.dataset.wizard

- Module: `ipai_superset_connector`
- Model type: `TransientModel`
- Table: `superset_dataset_wizard`

### Persisted fields
- `category`: `Selection`
- `connection_id`: `Many2one` (relation=superset.connection, required)
- `create_view`: `Boolean`
- `enable_rls`: `Boolean`
- `field_ids`: `Many2many` (relation=ir.model.fields)
- `include_all_fields`: `Boolean`
- `model_id`: `Many2one` (relation=ir.model, required)
- `name`: `Char`
- `sync_to_superset`: `Boolean`
- `technical_name`: `Char`

### Non-persisted fields
- _none_

## test.partner.time.window

- Module: `test_base_time_window`
- Model type: `Model`
- Table: `test_partner_time_window`
- _inherit: `time.window.mixin`
- Python constraints:
  - `check_window_no_overlaps`

### Persisted fields
- `partner_id`: `Many2one` (relation=res.partner, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## test.time.window.model

- Module: `base_time_window`
- Model type: `Model`
- Table: `test_time_window_model`
- _inherit: `time.window.mixin`

### Persisted fields
- `partner_id`: `Many2one` (relation=res.partner, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## time.weekday

- Module: `base_time_window`
- Model type: `Model`
- Table: `time_weekday`
- SQL constraints:
  - `name_uniq`: `UNIQUE(name)` (Name must be unique)

### Persisted fields
- `name`: `Selection` (required)

### Non-persisted fields
- _none_

## time.window.mixin

- Module: `base_time_window`
- Model type: `AbstractModel`
- Table: `time_window_mixin`
- Python constraints:
  - `_check_window_under_twenty_four_hours`
  - `check_window_no_overlaps`

### Persisted fields
- `time_window_end`: `Float` (relation=To, required)
- `time_window_start`: `Float` (relation=From, required)
- `time_window_weekday_ids`: `Many2many` (required)

### Non-persisted fields
- _none_

## timesheets.analysis.report

- Module: `project_task_ancestor`
- Model type: `Model`
- Table: `timesheets_analysis_report`
- _inherit: `timesheets.analysis.report`

### Persisted fields
- `ancestor_task_id`: `Many2one`

### Non-persisted fields
- _none_

## trgm.index

- Module: `base_search_fuzzy`
- Model type: `Model`
- Table: `trgm_index`

### Persisted fields
- `field_id`: `Many2one` (required, ondelete=set default)
- `index_name`: `Char`
- `index_type`: `Selection` (required)

### Non-persisted fields
- _none_

## trial.balance.report.wizard

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `trial_balance_report_wizard`
- _inherit: `account_financial_report_abstract_wizard`
- Python constraints:
  - `_check_company_id_date_range_id`
  - `_check_show_hierarchy_level`

### Persisted fields
- `account_code_from`: `Many2one`
- `account_code_to`: `Many2one`
- `account_ids`: `Many2many`
- `date_from`: `Date` (required)
- `date_range_id`: `Many2one`
- `date_to`: `Date` (required)
- `foreign_currency`: `Boolean`
- `fy_start_date`: `Date` (compute=_compute_fy_start_date)
- `grouped_by`: `Selection`
- `hide_account_at_0`: `Boolean`
- `hide_parent_hierarchy_level`: `Boolean` (relation=Do not display parent levels)
- `journal_ids`: `Many2many`
- `limit_hierarchy_level`: `Boolean` (relation=Limit hierarchy levels)
- `only_one_unaffected_earnings_account`: `Boolean`
- `partner_ids`: `Many2many`
- `payable_accounts_only`: `Boolean`
- `receivable_accounts_only`: `Boolean`
- `show_hierarchy`: `Boolean`
- `show_hierarchy_level`: `Integer` (relation=Hierarchy Levels to display)
- `show_partner_details`: `Boolean`
- `target_move`: `Selection` (required)
- `unaffected_earnings_account`: `Many2one` (compute=_compute_unaffected_earnings_account)

### Non-persisted fields
- _none_

## upgrade.analysis

- Module: `upgrade_analysis`
- Model type: `Model`
- Table: `upgrade_analysis`

### Persisted fields
- `analysis_date`: `Datetime`
- `config_id`: `Many2one` (required)
- `log`: `Text`
- `state`: `Selection`
- `upgrade_path`: `Char` (compute=_compute_upgrade_path)
- `write_files`: `Boolean`

### Non-persisted fields
- _none_

## upgrade.attribute

- Module: `upgrade_analysis`
- Model type: `Model`
- Table: `upgrade_attribute`

### Persisted fields
- `name`: `Char`
- `record_id`: `Many2one` (index, ondelete=CASCADE)
- `value`: `Char`

### Non-persisted fields
- _none_

## upgrade.comparison.config

- Module: `upgrade_analysis`
- Model type: `Model`
- Table: `upgrade_comparison_config`

### Persisted fields
- `analysis_qty`: `Integer` (compute=_compute_analysis_qty)
- `database`: `Char` (required)
- `name`: `Char`
- `password`: `Char` (required)
- `port`: `Integer` (required)
- `server`: `Char` (required)
- `username`: `Char` (required)
- `version`: `Char`

### Non-persisted fields
- `analysis_ids`: `One2many`

## upgrade.generate.record.wizard

- Module: `upgrade_analysis`
- Model type: `TransientModel`
- Table: `upgrade_generate_record_wizard`

### Persisted fields
- `state`: `Selection`

### Non-persisted fields
- _none_

## upgrade.install.wizard

- Module: `upgrade_analysis`
- Model type: `TransientModel`
- Table: `upgrade_install_wizard`

### Persisted fields
- `module_ids`: `Many2many`
- `module_qty`: `Integer` (compute=_compute_module_qty)
- `state`: `Selection`

### Non-persisted fields
- _none_

## upgrade.record

- Module: `upgrade_analysis`
- Model type: `Model`
- Table: `upgrade_record`

### Persisted fields
- `definition`: `Char`
- `domain`: `Char`
- `field`: `Char`
- `mode`: `Selection`
- `model`: `Char`
- `model_original_module`: `Char` (compute=_compute_model_original_module)
- `model_type`: `Char` (compute=_compute_model_type)
- `module`: `Char`
- `name`: `Char`
- `noupdate`: `Boolean`
- `prefix`: `Char` (compute=_compute_prefix_and_suffix)
- `suffix`: `Char` (compute=_compute_prefix_and_suffix)
- `type`: `Selection`

### Non-persisted fields
- `attribute_ids`: `One2many`

## vacuum.rule

- Module: `autovacuum_message_attachment`
- Model type: `Model`
- Table: `vacuum_rule`
- Python constraints:
  - `_check_inheriting_model`
  - `retention_time_not_null`

### Persisted fields
- `active`: `Boolean`
- `company_id`: `Many2one` (relation=res.company)
- `description`: `Text`
- `empty_model`: `Boolean`
- `empty_subtype`: `Boolean`
- `filename_pattern`: `Char`
- `inheriting_model`: `Char`
- `message_subtype_ids`: `Many2many` (relation=mail.message.subtype)
- `message_type`: `Selection`
- `model`: `Char` (compute=_compute_model_id)
- `model_filter_domain`: `Text`
- `model_id`: `Many2one` (relation=ir.model, compute=_compute_model_id)
- `model_ids`: `Many2many` (relation=ir.model)
- `name`: `Char` (required)
- `retention_time`: `Integer` (required)
- `ttype`: `Selection` (required)

### Non-persisted fields
- _none_

## vat.report.wizard

- Module: `account_financial_report`
- Model type: `TransientModel`
- Table: `vat_report_wizard`
- _inherit: `account_financial_report_abstract_wizard`
- Python constraints:
  - `_check_company_id_date_range_id`

### Persisted fields
- `based_on`: `Selection` (required)
- `date_from`: `Date` (relation=Start Date, required)
- `date_range_id`: `Many2one`
- `date_to`: `Date` (relation=End Date, required)
- `target_move`: `Selection` (required)
- `tax_detail`: `Boolean` (relation=Detail Taxes)

### Non-persisted fields
- _none_

## web.editor.class

- Module: `web_editor_class_selector`
- Model type: `Model`
- Table: `web_editor_class`
- SQL constraints:
  - `class_name_uniq`: `unique(class_name)` (Class name must be unique)

### Persisted fields
- `active`: `Boolean`
- `class_name`: `Char` (required)
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- _none_

## web.environment.ribbon.backend

- Module: `web_environment_ribbon`
- Model type: `AbstractModel`
- Table: `web_environment_ribbon_backend`

### Persisted fields

### Non-persisted fields
- _none_

## web.form.banner.rule

- Module: `web_form_banner`
- Model type: `Model`
- Table: `web_form_banner_rule`
- Python constraints:
  - `_check_target_xpath`

### Persisted fields
- `active`: `Boolean`
- `message`: `Text`
- `message_is_html`: `Boolean` (relation=HTML)
- `message_value_code`: `Text`
- `model_id`: `Many2one` (relation=ir.model, required, ondelete=cascade)
- `model_name`: `Char` (related=model_id.model)
- `name`: `Char` (required)
- `position`: `Selection` (required)
- `sequence`: `Integer`
- `severity`: `Selection` (required)
- `target_xpath`: `Char` (relation=Target XPath)
- `trigger_field_ids`: `Many2many` (relation=ir.model.fields)
- `view_ids`: `Many2many` (relation=ir.ui.view)

### Non-persisted fields
- _none_

## wizard.open.tax.balances

- Module: `account_tax_balance`
- Model type: `TransientModel`
- Table: `wizard_open_tax_balances`

### Persisted fields
- `company_ids`: `Many2many` (required)
- `date_range_id`: `Many2one` (relation=date.range)
- `from_date`: `Date` (compute=_compute_date_range, required)
- `target_move`: `Selection` (required)
- `to_date`: `Date` (compute=_compute_date_range, required)

### Non-persisted fields
- _none_

## xlsx.export

- Module: `excel_import_export`
- Model type: `AbstractModel`
- Table: `xlsx_export`

### Persisted fields

### Non-persisted fields
- _none_

## xlsx.import

- Module: `excel_import_export`
- Model type: `AbstractModel`
- Table: `xlsx_import`

### Persisted fields

### Non-persisted fields
- _none_

## xlsx.report

- Module: `excel_import_export`
- Model type: `AbstractModel`
- Table: `xlsx_report`

### Persisted fields
- `choose_template`: `Boolean`
- `data`: `Binary`
- `name`: `Char`
- `state`: `Selection`
- `template_id`: `Many2one` (relation=xlsx.template, required, ondelete=cascade)

### Non-persisted fields
- _none_

## xlsx.styles

- Module: `excel_import_export`
- Model type: `AbstractModel`
- Table: `xlsx_styles`

### Persisted fields

### Non-persisted fields
- _none_

## xlsx.template

- Module: `excel_import_export`
- Model type: `Model`
- Table: `xlsx_template`
- Python constraints:
  - `_check_action_model`

### Persisted fields
- `csv_delimiter`: `Char` (required)
- `csv_extension`: `Char` (required)
- `csv_quote`: `Boolean`
- `datas`: `Binary`
- `description`: `Char`
- `export_action_id`: `Many2one` (ondelete=set null)
- `fname`: `Char`
- `gname`: `Char`
- `import_action_id`: `Many2one` (ondelete=set null)
- `input_instruction`: `Text`
- `instruction`: `Text` (compute=_compute_output_instruction)
- `name`: `Char` (required)
- `post_import_hook`: `Char`
- `redirect_action`: `Many2one`
- `report_action_id`: `Many2one`
- `report_menu_id`: `Many2one`
- `res_model`: `Char`
- `result_field`: `Char` (compute=_compute_result_field)
- `result_model_id`: `Many2one`
- `show_instruction`: `Boolean`
- `to_csv`: `Boolean`
- `use_report_wizard`: `Boolean`

### Non-persisted fields
- `export_ids`: `One2many`
- `import_ids`: `One2many`

## xlsx.template.export

- Module: `excel_import_export`
- Model type: `Model`
- Table: `xlsx_template_export`

### Persisted fields
- `excel_cell`: `Char`
- `field_cond`: `Char`
- `field_name`: `Char`
- `is_cont`: `Boolean`
- `is_extend`: `Boolean`
- `is_sum`: `Boolean`
- `row_field`: `Char`
- `section_type`: `Selection` (required)
- `sequence`: `Integer`
- `sheet`: `Char`
- `style`: `Char`
- `style_cond`: `Char`
- `template_id`: `Many2one` (index, ondelete=cascade)

### Non-persisted fields
- _none_

## xlsx.template.import

- Module: `excel_import_export`
- Model type: `Model`
- Table: `xlsx_template_import`

### Persisted fields
- `excel_cell`: `Char`
- `field_cond`: `Char`
- `field_name`: `Char`
- `no_delete`: `Boolean`
- `row_field`: `Char`
- `section_type`: `Selection` (required)
- `sequence`: `Integer`
- `sheet`: `Char`
- `template_id`: `Many2one` (index, ondelete=cascade)

### Non-persisted fields
- _none_
