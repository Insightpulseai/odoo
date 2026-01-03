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

## account.move

- Module: `ipai`
- Model type: `Model`
- Table: `account_move`
- _inherit: `account.move`

### Persisted fields
- `bir_2307_date`: `Date`
- `bir_2307_generated`: `Boolean`
- `ewt_amount`: `Monetary` (compute=_compute_ewt_amount)

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

## close.approval.gate

- Module: `ipai`
- Model type: `Model`
- Table: `close_approval_gate`
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `actual_value`: `Float`
- `approval_notes`: `Text`
- `approved_by`: `Many2one` (relation=res.users)
- `approved_date`: `Datetime`
- `approver_id`: `Many2one` (relation=res.users)
- `approver_role`: `Selection` (required)
- `approver_user_id`: `Many2one` (relation=res.users)
- `block_on_exceptions`: `Boolean`
- `block_reason`: `Text`
- `blocking_exceptions`: `Many2many` (relation=close.exception)
- `blocking_reason`: `Text`
- `blocking_tasks`: `Many2many` (relation=close.task)
- `company_id`: `Many2one` (relation=res.company, related=cycle_id.company_id)
- `cycle_id`: `Many2one` (relation=close.cycle, required, index, ondelete=cascade)
- `gate_level`: `Integer` (required)
- `gate_type`: `Selection` (required)
- `min_completion_pct`: `Float`
- `name`: `Char` (required)
- `notes`: `Html`
- `required_approvals`: `Integer`
- `required_task_states`: `Char`
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
- `close_actual_date`: `Date`
- `close_start_date`: `Date`
- `close_target_date`: `Date`
- `closing_period_id`: `Many2one` (relation=closing.period)
- `company_id`: `Many2one` (relation=res.company, required)
- `cycle_time_days`: `Integer` (compute=_compute_cycle_time)
- `exception_count`: `Integer` (compute=_compute_exception_count)
- `gates_ready`: `Boolean` (compute=_compute_gates_ready)
- `name`: `Char` (required)
- `notes`: `Html`
- `open_exception_count`: `Integer` (compute=_compute_exception_count)
- `period_end`: `Date` (required)
- `period_label`: `Char` (compute=_compute_period_label)
- `period_start`: `Date` (required)
- `period_type`: `Selection` (required)
- `progress`: `Float` (compute=_compute_task_stats)
- `state`: `Selection` (required)
- `task_completion_pct`: `Float` (compute=_compute_task_stats)
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
- `amount`: `Monetary`
- `assigned_to`: `Many2one` (relation=res.users)
- `company_id`: `Many2one` (relation=res.company, related=cycle_id.company_id)
- `currency_id`: `Many2one` (relation=res.currency)
- `cycle_id`: `Many2one` (relation=close.cycle, required, index, ondelete=cascade)
- `description`: `Html`
- `detected_by`: `Many2one` (relation=res.users)
- `detected_date`: `Datetime`
- `escalated_date`: `Datetime`
- `escalated_to`: `Many2one` (relation=res.users)
- `escalation_count`: `Integer`
- `escalation_deadline`: `Datetime`
- `escalation_level`: `Integer`
- `exception_type`: `Selection` (required)
- `last_escalated`: `Datetime`
- `name`: `Char` (required)
- `related_account_id`: `Many2one` (relation=account.account)
- `related_move_id`: `Many2one` (relation=account.move)
- `related_partner_id`: `Many2one` (relation=res.partner)
- `reported_by`: `Many2one` (relation=res.users)
- `resolution`: `Html`
- `resolution_action`: `Text`
- `resolved_by`: `Many2one` (relation=res.users)
- `resolved_date`: `Datetime`
- `root_cause`: `Text`
- `severity`: `Selection` (required)
- `state`: `Selection` (required)
- `task_id`: `Many2one` (relation=close.task, index, ondelete=set null)
- `variance_pct`: `Float`

### Non-persisted fields
- _none_

## close.task

- Module: `ipai`
- Model type: `Model`
- Table: `close_task`
- _inherit: `close.task, mail.activity.mixin, mail.thread`

### Persisted fields
- `a1_task_id`: `Many2one` (relation=a1.task)
- `approval_deadline`: `Date`
- `approval_done_by`: `Many2one` (relation=res.users)
- `approval_done_date`: `Datetime`
- `approve_done_date`: `Datetime`
- `approve_due_date`: `Date`
- `approve_notes`: `Text`
- `approve_user_id`: `Many2one` (relation=res.users)
- `approver_id`: `Many2one` (relation=res.users)
- `attachment_ids`: `Many2many` (relation=ir.attachment)
- `category_id`: `Many2one` (relation=close.task.category)
- `checklist_done_pct`: `Float` (compute=_compute_checklist_pct)
- `checklist_progress`: `Float` (compute=_compute_checklist_progress)
- `company_id`: `Many2one` (relation=res.company, related=cycle_id.company_id)
- `cycle_id`: `Many2one` (relation=close.cycle, required, index, ondelete=cascade)
- `days_overdue`: `Integer` (compute=_compute_is_overdue)
- `description`: `Text`
- `external_key`: `Char` (index)
- `gl_entry_count`: `Integer` (compute=_compute_gl_entry_count)
- `gl_entry_ids`: `Many2many` (relation=account.move)
- `has_exceptions`: `Boolean` (compute=_compute_has_exceptions)
- `has_open_exceptions`: `Boolean` (compute=_compute_has_open_exceptions)
- `is_overdue`: `Boolean` (compute=_compute_is_overdue)
- `name`: `Char` (required)
- `notes`: `Html`
- `prep_deadline`: `Date`
- `prep_done_by`: `Many2one` (relation=res.users)
- `prep_done_date`: `Datetime`
- `prep_due_date`: `Date`
- `prep_notes`: `Text`
- `prep_user_id`: `Many2one` (relation=res.users)
- `preparer_id`: `Many2one` (relation=res.users)
- `review_deadline`: `Date`
- `review_done_by`: `Many2one` (relation=res.users)
- `review_done_date`: `Datetime`
- `review_due_date`: `Date`
- `review_notes`: `Text`
- `review_result`: `Selection`
- `review_user_id`: `Many2one` (relation=res.users)
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
  - `category_code_unique`: `unique(code)` (Category code must be unique)
  - `code_uniq`: `unique(code, company_id)` (Category code must be unique per company.)
  - `code_uniq`: `unique(code, company_id)` (Category code must be unique per company.)

### Persisted fields
- `a1_workstream_id`: `Many2one` (relation=a1.workstream)
- `active`: `Boolean`
- `code`: `Char` (required, index)
- `color`: `Integer`
- `company_id`: `Many2one` (relation=res.company, required)
- `default_approve_days`: `Integer`
- `default_approve_role`: `Selection`
- `default_prep_days`: `Integer`
- `default_prep_role`: `Selection`
- `default_review_days`: `Integer`
- `default_review_role`: `Selection`
- `description`: `Text`
- `gl_account_ids`: `Many2many` (relation=account.account)
- `name`: `Char` (required)
- `sequence`: `Integer`

### Non-persisted fields
- `template_ids`: `One2many` (relation=close.task.template)

## close.task.checklist

- Module: `ipai`
- Model type: `Model`
- Table: `close_task_checklist`

### Persisted fields
- `attachment_id`: `Many2one` (relation=ir.attachment)
- `code`: `Char` (required)
- `done_at`: `Datetime`
- `done_by`: `Many2one` (relation=res.users)
- `done_date`: `Datetime`
- `evidence_type`: `Selection`
- `instructions`: `Text`
- `is_done`: `Boolean`
- `is_required`: `Boolean`
- `name`: `Char` (required)
- `notes`: `Text`
- `required`: `Boolean`
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
  - `template_code_unique`: `unique(code)` (Template code must be unique)

### Persisted fields
- `a1_template_id`: `Many2one` (relation=a1.template)
- `active`: `Boolean`
- `approval_days`: `Float`
- `approval_offset`: `Integer`
- `approve_day_offset`: `Integer`
- `approver_id`: `Many2one` (relation=res.users)
- `approver_role`: `Selection`
- `category_id`: `Many2one` (relation=close.task.category, index, ondelete=cascade)
- `code`: `Char` (required, index)
- `company_id`: `Many2one` (relation=res.company, required)
- `creates_gl_entry`: `Boolean`
- `default_approve_user_id`: `Many2one` (relation=res.users)
- `default_prep_user_id`: `Many2one` (relation=res.users)
- `default_review_user_id`: `Many2one` (relation=res.users)
- `description`: `Html`
- `gl_account_ids`: `Many2many` (relation=account.account)
- `name`: `Char` (required)
- `period_type`: `Selection`
- `prep_day_offset`: `Integer`
- `prep_days`: `Float`
- `prep_offset`: `Integer`
- `preparer_id`: `Many2one` (relation=res.users)
- `preparer_role`: `Selection`
- `review_day_offset`: `Integer`
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
- `evidence_type`: `Selection`
- `instructions`: `Text`
- `is_required`: `Boolean`
- `name`: `Char` (required)
- `required`: `Boolean`
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

## discuss.channel

- Module: `ipai_ask_ai`
- Model type: `Model`
- Table: `discuss_channel`
- _inherit: `discuss.channel`

### Persisted fields
- `is_ai_channel`: `Boolean`

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
- _inherit: `mail.activity.mixin, mail.thread`

### Persisted fields
- `approval_date`: `Date`
- `bir_deadline`: `Date` (required)
- `form_code`: `Char` (required)
- `period`: `Char` (required)
- `prep_date`: `Date`
- `responsible_approval_id`: `Many2one` (relation=ipai.finance.person)
- `responsible_prep_id`: `Many2one` (relation=ipai.finance.person)
- `responsible_review_id`: `Many2one` (relation=ipai.finance.person)
- `review_date`: `Date`

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

## ipai.export.seed.wizard

- Module: `ipai_ppm_a1`
- Model type: `TransientModel`
- Table: `ipai_export_seed_wizard`

### Persisted fields
- `export_path`: `Char`
- `webhook_url`: `Char`

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

## ipai.import.seed.wizard

- Module: `ipai_ppm_a1`
- Model type: `TransientModel`
- Table: `ipai_import_seed_wizard`

### Persisted fields
- `mode`: `Selection` (required)
- `seed_json`: `Text` (required)

### Non-persisted fields
- _none_

## ipai.localization.overlay

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_localization_overlay`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `active`: `Boolean`
- `applies_to_code`: `Char` (required)
- `country`: `Selection` (required)
- `patch_payload`: `Text` (required)
- `patch_type`: `Selection` (required)
- `sequence`: `Integer`
- `workstream_id`: `Many2one` (relation=ipai.workstream, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

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

## ipai.ppm.task

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_ppm_task`
- _inherit: `mail.thread, mail.activity.mixin`
- SQL constraints:
  - `task_code_unique`: `unique(code, template_id)` (Task code must be unique per template.)

### Persisted fields
- `category`: `Char`
- `code`: `Char` (required)
- `due_offset_days`: `Integer`
- `evidence_required`: `Boolean`
- `name`: `Char` (required)
- `owner_role`: `Char`
- `phase`: `Selection`
- `prep_offset`: `Integer`
- `requires_approval`: `Boolean`
- `review_offset`: `Integer`
- `sap_reference`: `Char`
- `sequence`: `Integer`
- `template_id`: `Many2one` (relation=ipai.ppm.template, required, index, ondelete=cascade)

### Non-persisted fields
- `checklist_line_ids`: `One2many` (relation=ipai.ppm.task.checklist)

## ipai.ppm.task.checklist

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_ppm_task_checklist`

### Persisted fields
- `evidence_type`: `Selection` (required)
- `label`: `Char` (required)
- `notes`: `Char`
- `required`: `Boolean`
- `sequence`: `Integer`
- `task_id`: `Many2one` (relation=ipai.ppm.task, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.ppm.tasklist

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_ppm_tasklist`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `name`: `Char` (required)
- `period_end`: `Date` (required)
- `period_start`: `Date` (required)
- `status`: `Selection`
- `template_id`: `Many2one` (relation=ipai.ppm.template, required, index, ondelete=restrict)
- `workstream_id`: `Many2one` (relation=ipai.workstream, required, index, ondelete=restrict)

### Non-persisted fields
- `taskrun_ids`: `One2many` (relation=ipai.ppm.taskrun)

## ipai.ppm.taskrun

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_ppm_taskrun`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `approver_id`: `Many2one` (relation=res.users, ondelete=set null)
- `assignee_id`: `Many2one` (relation=res.users, ondelete=set null)
- `done_at`: `Datetime`
- `name`: `Char` (required)
- `started_at`: `Datetime`
- `status`: `Selection`
- `task_id`: `Many2one` (relation=ipai.ppm.task, required, index, ondelete=restrict)
- `tasklist_id`: `Many2one` (relation=ipai.ppm.tasklist, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.ppm.template

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_ppm_template`
- _inherit: `mail.thread, mail.activity.mixin`
- SQL constraints:
  - `template_code_unique`: `unique(code, workstream_id)` (Template code must be unique per workstream.)

### Persisted fields
- `code`: `Char` (required)
- `is_active`: `Boolean`
- `name`: `Char` (required)
- `period_type`: `Selection` (required)
- `sequence`: `Integer`
- `version`: `Char`
- `workstream_id`: `Many2one` (relation=ipai.workstream, required, index, ondelete=cascade)

### Non-persisted fields
- `task_ids`: `One2many` (relation=ipai.ppm.task)

## ipai.repo.export_run

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_repo_export_run`
- _inherit: `mail.thread, mail.activity.mixin`

### Persisted fields
- `export_path`: `Char`
- `exported_at`: `Datetime`
- `name`: `Char` (required)
- `payload_json`: `Text`
- `state`: `Selection`
- `webhook_status`: `Char`
- `webhook_url`: `Char`

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

## ipai.stc.check

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_stc_check`
- _inherit: `mail.thread, mail.activity.mixin`
- SQL constraints:
  - `stc_check_code_unique`: `unique(code)` (Check code must be unique.)

### Persisted fields
- `auto_run`: `Boolean`
- `category`: `Char`
- `code`: `Char` (required)
- `description`: `Text`
- `is_active`: `Boolean`
- `name`: `Char` (required)
- `rule_json`: `Text`
- `sap_reference`: `Char`
- `sequence`: `Integer`
- `severity`: `Selection`
- `worklist_type_id`: `Many2one` (relation=ipai.stc.worklist_type, ondelete=set null)
- `workstream_id`: `Many2one` (relation=ipai.workstream, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.stc.scenario

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_stc_scenario`
- _inherit: `mail.thread, mail.activity.mixin`
- SQL constraints:
  - `stc_scenario_code_unique`: `unique(code)` (Scenario code must be unique.)

### Persisted fields
- `bir_forms`: `Char`
- `check_ids`: `Many2many` (relation=ipai.stc.check)
- `code`: `Char` (required)
- `frequency`: `Selection`
- `name`: `Char` (required)
- `notes`: `Text`
- `run_day_offset`: `Integer`
- `sap_reference`: `Char`
- `sequence`: `Integer`
- `workstream_id`: `Many2one` (relation=ipai.workstream, required, index, ondelete=cascade)

### Non-persisted fields
- _none_

## ipai.stc.worklist_type

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_stc_worklist_type`
- SQL constraints:
  - `stc_worklist_code_unique`: `unique(code)` (Worklist type code must be unique.)

### Persisted fields
- `code`: `Char` (required)
- `description`: `Text`
- `name`: `Char` (required)

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

## ipai.workstream

- Module: `ipai_ppm_a1`
- Model type: `Model`
- Table: `ipai_workstream`
- _inherit: `mail.thread, mail.activity.mixin`
- SQL constraints:
  - `workstream_code_unique`: `unique(code)` (Workstream code must be unique.)

### Persisted fields
- `active`: `Boolean`
- `code`: `Selection` (required)
- `description`: `Text`
- `name`: `Char` (required)
- `odoo_anchor`: `Char`
- `sap_anchor`: `Char`

### Non-persisted fields
- `check_ids`: `One2many` (relation=ipai.stc.check)
- `overlay_ids`: `One2many` (relation=ipai.localization.overlay)
- `scenario_ids`: `One2many` (relation=ipai.stc.scenario)
- `tasklist_ids`: `One2many` (relation=ipai.ppm.tasklist)
- `template_ids`: `One2many` (relation=ipai.ppm.template)

## ir.http

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `ir_http`
- _inherit: `ir.http`

### Persisted fields

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

## master.control.mixin

- Module: `ipai`
- Model type: `AbstractModel`
- Table: `master_control_mixin`

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
- `deliverables`: `Text`
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
- _inherit: `project.project`

### Persisted fields
- `actual_finish`: `Date`
- `actual_start`: `Date`
- `baseline_finish`: `Date`
- `baseline_start`: `Date`
- `clarity_id`: `Char` (required, index)
- `critical_milestone_count`: `Integer` (compute=_compute_milestone_stats)
- `health_status`: `Selection` (required)
- `im_code`: `Char` (index)
- `ipai_finance_enabled`: `Boolean`
- `ipai_im_code`: `Selection` (index)
- `ipai_is_im_project`: `Boolean` (index)
- `ipai_root_project_id`: `Many2one` (relation=project.project, index, ondelete=set null)
- `is_program`: `Boolean` (index)
- `milestone_count`: `Integer` (compute=_compute_milestone_stats)
- `overall_progress`: `Float` (compute=_compute_overall_progress)
- `overall_status`: `Selection` (compute=_compute_overall_status)
- `parent_id`: `Many2one` (relation=project.project, index, ondelete=restrict)
- `phase_count`: `Integer` (compute=_compute_phase_stats)
- `portfolio_id`: `Many2one` (relation=project.category)
- `ppm_program_ids`: `Many2many` (relation=ppm.program)
- `program_code`: `Char` (index)
- `program_type`: `Selection` (index)
- `variance_finish`: `Integer` (compute=_compute_variances)
- `variance_start`: `Integer` (compute=_compute_variances)
- `x_cycle_code`: `Char` (index)

### Non-persisted fields
- `child_ids`: `One2many` (relation=project.project)
- `im_count`: `Integer` (compute=_compute_im_rollups)
- `im_task_count`: `Integer` (compute=_compute_im_rollups)

## project.task

- Module: `ipai`
- Model type: `Model`
- Table: `project_task`
- _inherit: `project.task`
- Python constraints:
  - `_check_phase_hierarchy`

### Persisted fields
- `activity_type`: `Selection` (index)
- `actual_cost`: `Float`
- `actual_hours`: `Float` (compute=_compute_actual_hours)
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
- `cost_variance`: `Float` (compute=_compute_variances)
- `critical_path`: `Boolean` (compute=_compute_critical_path, index)
- `earned_value`: `Float` (compute=_compute_earned_value)
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
- `has_gate`: `Boolean`
- `ipai_compliance_step`: `Selection` (index)
- `ipai_days_to_deadline`: `Integer` (compute=_compute_ipai_deadline_metrics)
- `ipai_owner_code`: `Char` (index)
- `ipai_owner_role`: `Selection` (index)
- `ipai_status_bucket`: `Selection` (compute=_compute_ipai_deadline_metrics, index)
- `ipai_task_category`: `Selection` (index)
- `ipai_template_id`: `Many2one` (relation=ipai.finance.task.template, index, ondelete=set null)
- `is_finance_ppm`: `Boolean` (compute=_compute_is_finance_ppm)
- `is_phase`: `Boolean` (index)
- `lag_days`: `Integer`
- `lead_days`: `Integer`
- `milestone_count`: `Integer` (compute=_compute_milestone_count)
- `owner_code`: `Char`
- `period_covered`: `Char` (index)
- `phase_baseline_finish`: `Date`
- `phase_baseline_start`: `Date`
- `phase_progress`: `Float` (compute=_compute_phase_progress)
- `phase_status`: `Selection`
- `phase_type`: `Selection`
- `phase_variance_days`: `Integer` (compute=_compute_phase_variance)
- `planned_hours`: `Float`
- `planned_value`: `Float`
- `prep_duration`: `Float`
- `relative_due`: `Char`
- `remaining_hours`: `Float`
- `resource_allocation`: `Float`
- `review_duration`: `Float`
- `reviewer_id`: `Many2one` (relation=res.users)
- `role_code`: `Char` (index)
- `schedule_variance`: `Float` (compute=_compute_variances)
- `sfm_id`: `Many2one` (relation=res.users)
- `target_date`: `Date` (index)
- `total_float`: `Integer` (compute=_compute_float)
- `wbs_code`: `Char` (compute=_compute_wbs_code)
- `x_cycle_key`: `Char` (index)
- `x_external_key`: `Char` (index)
- `x_obsolete`: `Boolean` (index)
- `x_seed_hash`: `Char` (index)
- `x_step_code`: `Char` (index)
- `x_task_template_code`: `Char` (index)

### Non-persisted fields
- _none_

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

## purchase.order

- Module: `ipai`
- Model type: `Model`
- Table: `purchase_order`
- _inherit: `master.control.mixin, purchase.order`

### Persisted fields
- `x_master_control_submitted`: `Boolean`

### Non-persisted fields
- _none_

## res.config.settings

- Module: `ipai`
- Model type: `TransientModel`
- Table: `res_config_settings`
- _inherit: `res.config.settings`

### Persisted fields
- `ipai_enable_finance_project_analytics`: `Boolean`
- `superset_auto_sync`: `Boolean`
- `superset_connection_id`: `Many2one` (relation=superset.connection)
- `superset_create_analytics_views`: `Boolean`
- `superset_enable_rls`: `Boolean`
- `superset_sync_interval`: `Selection`

### Non-persisted fields
- _none_

## res.partner

- Module: `ipai`
- Model type: `Model`
- Table: `res_partner`
- _inherit: `res.partner`
- Python constraints:
  - `_check_tin_format`

### Persisted fields
- `bir_registered`: `Boolean`
- `bir_registration_date`: `Date`
- `srm_overall_score`: `Float` (related=srm_supplier_id.overall_score)
- `srm_supplier_id`: `Many2one` (relation=srm.supplier)
- `srm_tier`: `Selection` (related=srm_supplier_id.tier)
- `tax_type`: `Selection`
- `tin`: `Char` (index)
- `tin_branch_code`: `Char`

### Non-persisted fields
- _none_

## res.users

- Module: `ipai`
- Model type: `Model`
- Table: `res_users`
- _inherit: `res.users`
- SQL constraints:
  - `x_employee_code_uniq`: `UNIQUE(x_employee_code)` (Employee code must be unique)
  - `x_employee_code_uniq`: `UNIQUE(x_employee_code)` (Employee code must be unique)
  - `x_employee_code_unique`: `unique(x_employee_code)` (Employee code must be unique when set!)
  - `x_employee_code_unique`: `unique(x_employee_code)` (Employee code must be unique when set!)

### Persisted fields
- `x_employee_code`: `Char` (index)

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
