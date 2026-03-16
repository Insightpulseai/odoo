# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FinanceControllerKPI(models.Model):
    """
    Finance Controller KPI Model

    Provides 6 data generation methods for Finance Controller Dashboard:
    1. get_kpi_gauge_data() - 3 gauge charts + operational velocity
    2. get_calendar_heatmap_data() - Workload density + BIR milestones
    3. get_wbs_tree_data() - Task hierarchy tree
    4. get_gantt_data() - Task execution timeline
    5. get_raci_sunburst_data() - Responsibility distribution
    6. get_dependency_graph_data() - Task prerequisite network
    """

    _name = "finance.controller.kpi"
    _description = "Finance Controller KPI Computation"

    name = fields.Char(string="KPI Snapshot Name", required=True)
    employee_code = fields.Char(string="Employee Code", required=True, index=True)
    snapshot_date = fields.Date(
        string="Snapshot Date", default=fields.Date.context_today, required=True
    )
    kpi_data = fields.Text(string="KPI JSON Data")

    @api.model
    def get_kpi_gauge_data(self, employee_code="RIM"):
        """
        KPI Gauges Data - 3 gauge charts + operational velocity

        Returns:
            dict: {
                'timeliness': float (0-100%),
                'reconciliation': float (0-100%),
                'filing_rate': float (0-100%),
                'tasks_completed': int,
                'closing_adjustments': int,
                'daily_completion_pct': list of dict (7 days)
            }
        """
        # Query Month-End Close tasks
        query_timeliness = """
            SELECT
                COUNT(*) FILTER (WHERE mec.actual_completion_date <= mec.target_completion_date) AS on_time_count,
                COUNT(*) AS total_count
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s
                AND mec.status = 'completed'
                AND mec.actual_completion_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        self.env.cr.execute(query_timeliness, (employee_code,))
        timeliness_result = self.env.cr.dictfetchone()
        timeliness_pct = (
            (
                timeliness_result["on_time_count"]
                / timeliness_result["total_count"]
                * 100
            )
            if timeliness_result["total_count"] > 0
            else 0
        )

        # Query reconciliation rate (example: bank reconciliation completion)
        query_reconciliation = """
            SELECT
                COUNT(*) FILTER (WHERE mec.status = 'completed') AS reconciled_count,
                COUNT(*) AS total_count
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s
                AND mec.name ILIKE '%%reconciliation%%'
                AND mec.created_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        self.env.cr.execute(query_reconciliation, (employee_code,))
        reconciliation_result = self.env.cr.dictfetchone()
        reconciliation_pct = (
            (
                reconciliation_result["reconciled_count"]
                / reconciliation_result["total_count"]
                * 100
            )
            if reconciliation_result["total_count"] > 0
            else 0
        )

        # Query BIR filing rate (LogFrame indicator)
        query_filing = """
            SELECT
                COUNT(*) FILTER (WHERE logframe.actual_value >= logframe.target_value) AS compliant_count,
                COUNT(*) AS total_count
            FROM finance_ppm_logframe logframe
            WHERE logframe.indicator_name ILIKE '%%BIR%%filed%%'
                AND logframe.frequency = 'monthly'
                AND logframe.created_at >= CURRENT_DATE - INTERVAL '90 days'
        """
        self.env.cr.execute(query_filing)
        filing_result = self.env.cr.dictfetchone()
        filing_pct = (
            (filing_result["compliant_count"] / filing_result["total_count"] * 100)
            if filing_result["total_count"] > 0
            else 0
        )

        # Query daily completion trend (7 days)
        query_daily = """
            SELECT
                DATE(mec.actual_completion_date) AS completion_date,
                COUNT(*) AS tasks_completed
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s
                AND mec.status = 'completed'
                AND mec.actual_completion_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(mec.actual_completion_date)
            ORDER BY completion_date ASC
        """
        self.env.cr.execute(query_daily, (employee_code,))
        daily_results = self.env.cr.dictfetchall()

        # Fill gaps for last 7 days
        daily_completion_pct = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6 - i)).date()
            matching = [r for r in daily_results if r["completion_date"] == date]
            daily_completion_pct.append(
                {
                    "date": date.isoformat(),
                    "tasks": matching[0]["tasks_completed"] if matching else 0,
                    "completion_pct": (
                        min(100, (matching[0]["tasks_completed"] / 10) * 100)
                        if matching
                        else 0
                    ),
                }
            )

        # Query closing adjustments (JE count)
        query_adjustments = """
            SELECT COUNT(*) AS adjustment_count
            FROM account_move am
            WHERE am.move_type = 'entry'
                AND am.create_uid IN (
                    SELECT u.id FROM res_users u
                    JOIN hr_employee e ON u.employee_id = e.id
                    WHERE e.code = %s
                )
                AND am.create_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        self.env.cr.execute(query_adjustments, (employee_code,))
        adjustments_result = self.env.cr.dictfetchone()

        return {
            "timeliness": round(timeliness_pct, 2),
            "reconciliation": round(reconciliation_pct, 2),
            "filing_rate": round(filing_pct, 2),
            "tasks_completed": timeliness_result["total_count"],
            "closing_adjustments": adjustments_result["adjustment_count"],
            "daily_completion_pct": daily_completion_pct,
        }

    @api.model
    def get_calendar_heatmap_data(self, employee_code="RIM"):
        """
        Calendar Heatmap Data - Workload density + BIR milestones

        Returns:
            dict: {
                'heatmap_data': list of [date, task_count],
                'milestones': list of dict with {date, type, label}
            }
        """
        # Query task workload for last 90 days
        query_workload = """
            SELECT
                DATE(mec.target_completion_date) AS task_date,
                COUNT(*) AS task_count
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s
                AND mec.target_completion_date >= CURRENT_DATE - INTERVAL '90 days'
                AND mec.target_completion_date <= CURRENT_DATE + INTERVAL '30 days'
            GROUP BY DATE(mec.target_completion_date)
            ORDER BY task_date ASC
        """
        self.env.cr.execute(query_workload, (employee_code,))
        workload_results = self.env.cr.dictfetchall()

        heatmap_data = [
            [r["task_date"].isoformat(), r["task_count"]] for r in workload_results
        ]

        # Query BIR milestones
        query_milestones = """
            SELECT
                mec.bir_form_code AS form_code,
                DATE(mec.target_completion_date) AS deadline_date
            FROM ipai_finance_monthly_close mec
            WHERE mec.bir_form_code IS NOT NULL
                AND mec.target_completion_date >= CURRENT_DATE - INTERVAL '30 days'
                AND mec.target_completion_date <= CURRENT_DATE + INTERVAL '60 days'
            GROUP BY mec.bir_form_code, DATE(mec.target_completion_date)
            ORDER BY deadline_date ASC
        """
        self.env.cr.execute(query_milestones)
        milestone_results = self.env.cr.dictfetchall()

        milestones = []
        for m in milestone_results:
            milestones.append(
                {
                    "date": m["deadline_date"].isoformat(),
                    "type": "BIR",
                    "label": f"BIR {m['form_code']} Deadline",
                }
            )

        # Add BOOK LOCK milestones (last day of month)
        today = datetime.now().date()
        for month_offset in range(-1, 3):
            target_date = (
                today.replace(day=1) + timedelta(days=32 * month_offset)
            ).replace(day=1) - timedelta(days=1)
            milestones.append(
                {
                    "date": target_date.isoformat(),
                    "type": "BOOK_LOCK",
                    "label": f"BOOK LOCK {target_date.strftime('%B')}",
                }
            )

        return {
            "heatmap_data": heatmap_data,
            "milestones": sorted(milestones, key=lambda x: x["date"]),
        }

    @api.model
    def get_wbs_tree_data(self, employee_code="RIM"):
        """
        WBS Tree Data - Task hierarchy

        Returns:
            dict: {
                'name': 'root',
                'children': list of nested dict with task hierarchy
            }
        """
        # Query all tasks with parent relationships
        query_tasks = """
            SELECT
                mec.id,
                mec.name AS task_name,
                mec.parent_id,
                mec.cluster_classification,
                mec.owner_code,
                mec.status
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s OR mec.owner_code IS NULL
            ORDER BY mec.parent_id NULLS FIRST, mec.sequence ASC
        """
        self.env.cr.execute(query_tasks, (employee_code,))
        task_results = self.env.cr.dictfetchall()

        # Build hierarchical tree
        def build_tree(parent_id=None):
            children = [t for t in task_results if t["parent_id"] == parent_id]
            tree_nodes = []
            for child in children:
                node = {
                    "name": child["task_name"],
                    "value": 1,
                    "itemStyle": {"color": self._get_status_color(child["status"])},
                }
                subtree = build_tree(child["id"])
                if subtree:
                    node["children"] = subtree
                tree_nodes.append(node)
            return tree_nodes

        root_tree = build_tree(parent_id=None)

        return {"name": "Month-End Close WBS", "children": root_tree}

    @api.model
    def get_gantt_data(self, employee_code="RIM"):
        """
        Gantt Chart Data - Task execution timeline

        Returns:
            list: [
                {
                    'name': 'Task Name',
                    'start': 'YYYY-MM-DD',
                    'end': 'YYYY-MM-DD',
                    'owner': 'RIM',
                    'phase': 'Phase 1'
                }
            ]
        """
        query_gantt = """
            SELECT
                mec.name AS task_name,
                mec.target_completion_date AS end_date,
                (mec.target_completion_date - INTERVAL '5 days')::date AS start_date,
                mec.owner_code,
                mec.cluster_classification AS phase,
                mec.status
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s
                AND mec.target_completion_date IS NOT NULL
            ORDER BY mec.target_completion_date ASC
        """
        self.env.cr.execute(query_gantt, (employee_code,))
        gantt_results = self.env.cr.dictfetchall()

        gantt_data = []
        for g in gantt_results:
            gantt_data.append(
                {
                    "name": g["task_name"],
                    "start": g["start_date"].isoformat(),
                    "end": g["end_date"].isoformat(),
                    "owner": g["owner_code"],
                    "phase": g["phase"] or "Uncategorized",
                    "status": g["status"],
                }
            )

        return gantt_data

    @api.model
    def get_raci_sunburst_data(self, employee_code="RIM"):
        """
        RACI Sunburst Data - Responsibility distribution

        Returns:
            dict: {
                'name': 'root',
                'children': list of nested dict with RACI hierarchy
            }
        """
        # Query RACI assignments by cluster and owner
        query_raci = """
            SELECT
                mec.cluster_classification AS cluster,
                mec.owner_code,
                mec.raci_role,
                COUNT(*) AS task_count
            FROM ipai_finance_monthly_close mec
            WHERE mec.cluster_classification IS NOT NULL
                AND mec.owner_code IS NOT NULL
            GROUP BY mec.cluster_classification, mec.owner_code, mec.raci_role
            ORDER BY mec.cluster_classification, mec.owner_code
        """
        self.env.cr.execute(query_raci)
        raci_results = self.env.cr.dictfetchall()

        # Build sunburst hierarchy: Root → Cluster → Owner → RACI Role
        clusters = {}
        for r in raci_results:
            cluster_name = r["cluster"] or "Uncategorized"
            if cluster_name not in clusters:
                clusters[cluster_name] = {}

            owner = r["owner_code"]
            if owner not in clusters[cluster_name]:
                clusters[cluster_name][owner] = []

            clusters[cluster_name][owner].append(
                {"name": r["raci_role"] or "Unassigned", "value": r["task_count"]}
            )

        sunburst_children = []
        for cluster_name, owners in clusters.items():
            cluster_node = {"name": cluster_name, "children": []}
            for owner, roles in owners.items():
                owner_node = {"name": owner, "children": roles}
                cluster_node["children"].append(owner_node)
            sunburst_children.append(cluster_node)

        return {"name": "RACI Distribution", "children": sunburst_children}

    @api.model
    def get_dependency_graph_data(self, employee_code="RIM"):
        """
        Dependency Graph Data - Task prerequisite network

        Returns:
            dict: {
                'nodes': list of dict {id, name, category},
                'links': list of dict {source, target}
            }
        """
        # Query tasks with dependencies (parent-child relationships)
        query_dependencies = """
            SELECT
                mec.id,
                mec.name AS task_name,
                mec.parent_id,
                mec.cluster_classification
            FROM ipai_finance_monthly_close mec
            WHERE mec.owner_code = %s OR mec.owner_code IS NULL
        """
        self.env.cr.execute(query_dependencies, (employee_code,))
        dependency_results = self.env.cr.dictfetchall()

        nodes = []
        links = []
        node_ids = set()

        for d in dependency_results:
            if d["id"] not in node_ids:
                nodes.append(
                    {
                        "id": str(d["id"]),
                        "name": d["task_name"][:30],  # Truncate for readability
                        "category": d["cluster_classification"] or "Uncategorized",
                    }
                )
                node_ids.add(d["id"])

            if d["parent_id"]:
                links.append({"source": str(d["parent_id"]), "target": str(d["id"])})

        return {"nodes": nodes, "links": links}

    def _get_status_color(self, status):
        """Helper method to map task status to ECharts color"""
        color_map = {
            "completed": "#4caf50",  # Green
            "in_progress": "#ff9800",  # Orange
            "pending": "#2196f3",  # Blue
            "blocked": "#f44336",  # Red
        }
        return color_map.get(status, "#9e9e9e")  # Default gray

    @api.model
    def cron_generate_kpi_snapshot(self, employee_code="RIM"):
        """
        Daily cron job to generate KPI snapshot

        Args:
            employee_code (str): Employee code for filtering

        Returns:
            dict: KPI snapshot data
        """
        _logger.info(f"Generating Finance Controller KPI snapshot for {employee_code}")

        kpi_data = {
            "gauges": self.get_kpi_gauge_data(employee_code),
            "calendar": self.get_calendar_heatmap_data(employee_code),
            "wbs": self.get_wbs_tree_data(employee_code),
            "gantt": self.get_gantt_data(employee_code),
            "raci": self.get_raci_sunburst_data(employee_code),
            "dependencies": self.get_dependency_graph_data(employee_code),
        }

        # Store snapshot
        snapshot = self.create(
            {
                "name": f"Finance KPI Snapshot {fields.Date.today()} - {employee_code}",
                "employee_code": employee_code,
                "snapshot_date": fields.Date.today(),
                "kpi_data": json.dumps(kpi_data),
            }
        )

        _logger.info(f"KPI snapshot created: {snapshot.id}")

        return kpi_data
