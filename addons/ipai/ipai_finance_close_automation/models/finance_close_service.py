# -*- coding: utf-8 -*-
"""Finance Close Service - Month-end project generator with working-day deadlines."""
import calendar
import csv
import logging
import re
from datetime import date, datetime, timedelta

from odoo import api, models
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


def _month_end(d: date) -> date:
    """Get the last day of the month."""
    last = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last)


def _add_workdays(env, start: date, delta_days: int, calendar_obj=None) -> date:
    """
    Add/subtract working days.

    Negative delta_days means go backwards.
    Uses resource.calendar work intervals (respects resource.calendar.leaves holidays).
    """
    if not calendar_obj:
        company = env.company
        calendar_obj = company.resource_calendar_id or env["resource.calendar"].search(
            [], limit=1
        )

    # Fallback: weekday-only if no calendar
    if not calendar_obj:
        step = 1 if delta_days >= 0 else -1
        remaining = abs(delta_days)
        cur = start
        while remaining:
            cur = cur + timedelta(days=step)
            if cur.weekday() < 5:
                remaining -= 1
        return cur

    step = 1 if delta_days >= 0 else -1
    remaining = abs(delta_days)
    cur = start

    while remaining:
        cur = cur + timedelta(days=step)
        dt_from = datetime(cur.year, cur.month, cur.day, 0, 0, 0)
        dt_to = datetime(cur.year, cur.month, cur.day, 23, 59, 59)

        try:
            intervals = calendar_obj._work_intervals_batch(
                dt_from, dt_to, resources=None, compute_leaves=True
            )
            # Some Odoo versions return {False: intervals} when resources=None
            has_work = any(bool(ints) for ints in intervals.values())
        except Exception:
            # Fallback: simple weekday check
            has_work = cur.weekday() < 5

        if has_work:
            remaining -= 1

    return cur


class IpaFinanceCloseService(models.AbstractModel):
    _name = "ipai.finance.close.service"
    _description = "IPAI Finance Close Service"

    @api.model
    def _load_offset_rules(self):
        """
        Load rules from CSV with columns:
          priority, task_name_exact, task_name_contains, task_name_regex, category, offset_workdays

        Deterministic: sort by (priority asc, row_order asc).
        """
        path = get_module_resource(
            "ipai_finance_close_automation", "data", "deadline_offset_rules.csv"
        )
        rules = []
        if not path:
            return rules

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                i = 0
                for row in reader:
                    i += 1
                    priority_raw = (row.get("priority") or "").strip()
                    try:
                        priority = int(float(priority_raw)) if priority_raw else 9999
                    except (ValueError, TypeError):
                        priority = 9999

                    def _s(k):
                        return (row.get(k) or "").strip()

                    try:
                        offset = int(float(_s("offset_workdays") or 0))
                    except (ValueError, TypeError):
                        offset = 0

                    rules.append(
                        {
                            "priority": priority,
                            "row_order": i,
                            "task_name_exact": _s("task_name_exact"),
                            "task_name_contains": _s("task_name_contains"),
                            "task_name_regex": _s("task_name_regex"),
                            "category": _s("category"),
                            "offset_workdays": offset,
                        }
                    )
        except Exception as e:
            _logger.warning("Failed to load offset rules: %s", e)
            return rules

        rules.sort(key=lambda r: (r["priority"], r["row_order"]))
        return rules

    @api.model
    def _pick_offset_for_task(self, task, rules, category_names_by_tag_id):
        """
        First match wins. Priority order is pre-sorted.
        Matching order per rule: exact -> contains -> regex -> category
        """
        name = (task.name or "").strip()
        task_tags = set(task.tag_ids.ids)

        for r in rules:
            off = int(r["offset_workdays"] or 0)

            exact = r["task_name_exact"]
            if exact and name == exact:
                return off

            contains = r["task_name_contains"]
            if contains and contains.lower() in name.lower():
                return off

            rx = r["task_name_regex"]
            if rx:
                try:
                    if re.search(rx, name):
                        return off
                except re.error:
                    # ignore invalid regex deterministically
                    pass

            cat = r["category"]
            if cat:
                # category matches if any task tag name equals category
                for tid in task_tags:
                    if category_names_by_tag_id.get(tid) == cat:
                        return off

        return None

    @api.model
    def _apply_template_deadline_offsets(self):
        """
        Apply offsets to template tasks based on rule file.

        Deterministic:
          - applies per-task offset based on first matching rule
          - only writes when value changes
        """
        rules = self._load_offset_rules()
        if not rules:
            return {"updated": 0, "reason": "no_rules"}

        Task = self.env["project.task"].sudo()
        Tag = self.env["project.tags"].sudo()

        template_tasks = Task.search(
            [("project_id.name", "=", "Month-End Close Template")]
        )
        if not template_tasks:
            return {"updated": 0, "reason": "no_template_tasks"}

        # Map tag_id -> tag_name
        tags = Tag.search([("id", "in", template_tasks.mapped("tag_ids").ids)])
        category_names_by_tag_id = {t.id: t.name for t in tags}

        updated = 0
        for t in template_tasks:
            off = self._pick_offset_for_task(t, rules, category_names_by_tag_id)
            if off is None:
                continue
            if int(t.ipai_deadline_offset_workdays or 0) != int(off):
                t.write({"ipai_deadline_offset_workdays": int(off)})
                updated += 1

        return {"updated": updated}

    @api.model
    def generate_month_close(self, year: int, month: int, calendar_id=None):
        """
        Idempotent generator:
        - Template project: 'Month-End Close Template'
        - Target project: 'Month-end closing YYYY-MM'
        - Clone tasks if target has none
        - Apply date_deadline: month_end - offset_workdays (working days)
        """
        # Ensure template offsets are applied before generation
        self._apply_template_deadline_offsets()

        Project = self.env["project.project"].sudo()
        Task = self.env["project.task"].sudo()
        Cal = self.env["resource.calendar"].sudo()

        template = Project.search([("name", "=", "Month-End Close Template")], limit=1)
        if not template:
            raise ValueError("Template project not found: Month-End Close Template")

        target_name = f"Month-end closing {year:04d}-{month:02d}"
        target = Project.search([("name", "=", target_name)], limit=1)
        if not target:
            target = Project.create({"name": target_name, "active": True})

        calendar_obj = (
            Cal.browse(calendar_id)
            if calendar_id
            else (self.env.company.resource_calendar_id or Cal.search([], limit=1))
        )

        if Task.search_count([("project_id", "=", target.id)]) == 0:
            source_tasks = Task.search(
                [("project_id", "=", template.id)], order="id asc"
            )
            for t in source_tasks:
                Task.create(
                    {
                        "name": t.name,
                        "project_id": target.id,
                        "description": t.description,
                        "planned_hours": t.planned_hours,
                        "tag_ids": [(6, 0, t.tag_ids.ids)],
                        "ipai_deadline_offset_workdays": t.ipai_deadline_offset_workdays,
                    }
                )

        base = _month_end(date(year, month, 1))
        tasks = Task.search([("project_id", "=", target.id)])
        for t in tasks:
            offset = int(t.ipai_deadline_offset_workdays or 0)
            deadline = _add_workdays(self.env, base, -offset, calendar_obj=calendar_obj)
            t.write({"date_deadline": deadline.isoformat()})

        return {"project_id": target.id, "project_name": target.name, "tasks": len(tasks)}
