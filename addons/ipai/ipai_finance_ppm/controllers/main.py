# -*- coding: utf-8 -*-
"""
IPAI Finance PPM — OKR Dashboard controller
Serves a JSON data endpoint so the OWL dashboard component
is populated with live Odoo data.
"""
from odoo import http
from odoo.http import request


class FinancePPMDashboard(http.Controller):

    @http.route(
        "/finance-ppm/okr-dashboard/data",
        auth="user",
        type="json",
        methods=["POST"],
    )
    def okr_dashboard_data(self):
        """
        Returns live task counts by stage for Finance PPM projects.
        Response shape:
          {
            team: [{name, tasks_total, tasks_done, pct}],
            stages: {<stage_name>: <count>},
            totals: {total, done, pct},
          }
        """
        env = request.env

        # Finance PPM projects identified by cost center field presence
        projects = env["project.project"].search([
            ("ipai_ppm_cost_center", "!=", False),
        ])
        project_ids = projects.ids

        if not project_ids:
            return {"error": "Finance PPM projects not found"}

        # Per-user task counts — all users assigned to Finance PPM tasks
        all_tasks = env["project.task"].search([
            ("project_id", "in", project_ids),
            ("user_ids", "!=", False),
        ])
        user_ids = all_tasks.mapped("user_ids")

        team = []
        for u in user_ids:
            assigned = env["project.task"].search_count([
                ("project_id", "in", project_ids),
                ("user_ids", "in", [u.id]),
            ])
            done = env["project.task"].search_count([
                ("project_id", "in", project_ids),
                ("user_ids", "in", [u.id]),
                ("stage_id.fold", "=", True),
            ])
            pct = round(done / assigned * 100, 1) if assigned else 0
            team.append({
                "id": u.id,
                "name": u.name,
                "tasks_total": assigned,
                "tasks_done": done,
                "pct": pct,
            })

        # Stage distribution
        stages = env["project.task.type"].search([
            ("project_ids", "in", project_ids),
        ])
        stage_counts = {}
        for s in stages:
            cnt = env["project.task"].search_count([
                ("project_id", "in", project_ids),
                ("stage_id", "=", s.id),
            ])
            stage_counts[s.name] = cnt

        # Totals
        total = env["project.task"].search_count([
            ("project_id", "in", project_ids),
        ])
        done_total = env["project.task"].search_count([
            ("project_id", "in", project_ids),
            ("stage_id.fold", "=", True),
        ])

        return {
            "team": team,
            "stages": stage_counts,
            "totals": {
                "total": total,
                "done": done_total,
                "pct": round(done_total / total * 100, 1) if total else 0,
            },
        }
