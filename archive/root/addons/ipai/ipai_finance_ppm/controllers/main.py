# -*- coding: utf-8 -*-
"""
IPAI Finance PPM — OKR Dashboard controller
Serves the static HTML dashboard + a JSON data endpoint so the
ECharts visualisations are populated with live Odoo data.
"""
import os
from odoo import http
from odoo.http import request, Response


class FinancePPMDashboard(http.Controller):

    # ── HTML shell ──────────────────────────────────────────────────────
    @http.route(
        "/finance-ppm/okr-dashboard",
        auth="user",
        type="http",
        methods=["GET"],
    )
    def okr_dashboard(self):
        """Serve the standalone OKR dashboard HTML page directly from the
        static file so we avoid QWeb overhead for this self-contained doc."""
        html_path = os.path.join(
            os.path.dirname(__file__),
            "../static/src/html/okr_dashboard.html",
        )
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return Response(html_content, content_type="text/html; charset=utf-8")

    # ── Live data JSON ───────────────────────────────────────────────────
    @http.route(
        "/finance-ppm/okr-dashboard/data",
        auth="user",
        type="jsonrpc",
        methods=["POST"],
    )
    def okr_dashboard_data(self):
        """
        Returns live task counts by stage for the Finance PPM projects.
        Response shape:
          {
            team: [{code, name, role, tasks_total, tasks_done, pct}],
            stages: {<stage_name>: <count>},
            totals: {total, done, in_progress, todo},
          }
        """
        env = request.env

        # Locate the two canonical Finance PPM projects (name-match, CE-safe)
        projects = env["project.project"].search([
            ("name", "in", [
                "Finance PPM - Month-End Close",
                "Finance PPM - BIR Tax Filing",
            ])
        ])
        project_ids = projects.ids

        if not project_ids:
            return {"error": "Finance PPM projects not found"}

        # ── Per-user task counts ─────────────────────────────────────────
        # TBWA\SMP Finance team logins (UID 7-16 in prod)
        finance_logins = [
            "khalil.veracruz@omc.com",
            "jp.lorente@omc.com",
            "rey.meran@omc.com",
            "beng.manalo@omc.com",
            "jinky.paladin@omc.com",
            "amor.lasaga@omc.com",
            "jasmin.ignacio@omc.com",
            "sally.brillantes@omc.com",
            "jhoee.oliva@omc.com",
            "joana.maravillas@omc.com",
        ]
        users = env["res.users"].search([("login", "in", finance_logins)])

        team = []
        for u in users:
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
                "login": u.login,
                "name": u.name,
                "tasks_total": assigned,
                "tasks_done": done,
                "pct": pct,
            })

        # ── Stage distribution ───────────────────────────────────────────
        stages = env["project.task.type"].search([
            ("project_ids", "in", project_ids)
        ])
        stage_counts = {}
        for s in stages:
            cnt = env["project.task"].search_count([
                ("project_id", "in", project_ids),
                ("stage_id", "=", s.id),
            ])
            stage_counts[s.name] = cnt

        # ── Totals ───────────────────────────────────────────────────────
        total = env["project.task"].search_count([
            ("project_id", "in", project_ids)
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
