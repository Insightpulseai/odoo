# -*- coding: utf-8 -*-
"""
AFC RAG Service.

Retrieval-Augmented Generation service for Finance Close workflows.
Provides context retrieval for AI responses.
"""
import json
import logging
from datetime import date, timedelta

from odoo import api, models

_logger = logging.getLogger(__name__)


class AfcRagService(models.AbstractModel):
    """
    AFC (Accounting/Finance Close) RAG Service.

    Retrieves relevant context for AI queries from:
    - Project tasks (overdue, upcoming deadlines)
    - BIR tax deadlines
    - Expense policy exceptions
    - Finance KPIs
    """

    _name = "afc.rag.service"
    _description = "AFC RAG Context Retrieval Service"

    @api.model
    def retrieve_context(self, query, project_id=None, max_items=10):
        """
        Retrieve relevant context for a query.

        Args:
            query: User's question
            project_id: Optional project to scope context
            max_items: Maximum items per category

        Returns:
            dict: Context data for prompt injection
        """
        context = {
            "query": query,
            "timestamp": date.today().isoformat(),
            "sources": [],
        }

        # Analyze query intent
        intent = self._analyze_query_intent(query)

        # Retrieve relevant data based on intent
        if intent.get("blocking_tasks"):
            context["blocking_tasks"] = self._get_blocking_tasks(project_id, max_items)
            context["sources"].append("project.task (blocking)")

        if intent.get("deadlines"):
            context["upcoming_deadlines"] = self._get_upcoming_deadlines(max_items)
            context["sources"].append("project.task (deadlines)")

        if intent.get("bir_compliance"):
            context["bir_deadlines"] = self._get_bir_deadlines(max_items)
            context["sources"].append("finance.bir.deadline")

        if intent.get("expenses"):
            context["expense_summary"] = self._get_expense_summary()
            context["sources"].append("hr.expense")

        if intent.get("finance_summary"):
            context["finance_kpis"] = self._get_finance_kpis(project_id)
            context["sources"].append("project.task (KPIs)")

        # Always include basic context
        context["today"] = date.today().isoformat()
        context["user_name"] = self.env.user.name

        return context

    @api.model
    def _analyze_query_intent(self, query):
        """
        Analyze query to determine what context to retrieve.

        Uses keyword matching for efficiency.
        Could be enhanced with ML classification.
        """
        query_lower = query.lower()

        intent = {
            "blocking_tasks": False,
            "deadlines": False,
            "bir_compliance": False,
            "expenses": False,
            "finance_summary": False,
        }

        # Blocking tasks keywords
        blocking_keywords = ["blocking", "overdue", "late", "missed", "behind"]
        if any(kw in query_lower for kw in blocking_keywords):
            intent["blocking_tasks"] = True

        # Deadline keywords
        deadline_keywords = ["deadline", "due", "when", "upcoming", "schedule"]
        if any(kw in query_lower for kw in deadline_keywords):
            intent["deadlines"] = True

        # BIR/Tax keywords
        bir_keywords = ["bir", "tax", "compliance", "filing", "vat", "withholding"]
        if any(kw in query_lower for kw in bir_keywords):
            intent["bir_compliance"] = True

        # Expense keywords
        expense_keywords = ["expense", "receipt", "reimbursement", "travel", "cost"]
        if any(kw in query_lower for kw in expense_keywords):
            intent["expenses"] = True

        # Summary keywords
        summary_keywords = ["summary", "status", "overview", "priorities", "today"]
        if any(kw in query_lower for kw in summary_keywords):
            intent["finance_summary"] = True
            intent["blocking_tasks"] = True
            intent["deadlines"] = True

        return intent

    @api.model
    def _get_blocking_tasks(self, project_id=None, limit=10):
        """Get overdue tasks grouped by owner"""
        Task = self.env["project.task"].sudo()
        today = date.today()

        domain = [
            ("date_deadline", "<", today.isoformat()),
            ("finance_state", "!=", "done"),
            "|",
            ("is_closing_task", "=", True),
            ("is_compliance_task", "=", True),
        ]

        if project_id:
            domain.append(("project_id", "=", project_id))

        tasks = Task.search(domain, limit=limit, order="date_deadline asc")

        by_owner = {}
        for task in tasks:
            owner = task.user_id.name if task.user_id else "Unassigned"
            if owner not in by_owner:
                by_owner[owner] = []
            by_owner[owner].append(
                {
                    "name": task.name,
                    "deadline": (
                        task.date_deadline.isoformat() if task.date_deadline else None
                    ),
                    "days_overdue": (
                        (today - task.date_deadline).days if task.date_deadline else 0
                    ),
                    "project": task.project_id.name if task.project_id else None,
                }
            )

        return {
            "total": len(tasks),
            "by_owner": by_owner,
        }

    @api.model
    def _get_upcoming_deadlines(self, limit=10):
        """Get tasks with upcoming deadlines"""
        Task = self.env["project.task"].sudo()
        today = date.today()
        next_week = today + timedelta(days=7)

        tasks = Task.search(
            [
                ("date_deadline", ">=", today.isoformat()),
                ("date_deadline", "<=", next_week.isoformat()),
                ("finance_state", "!=", "done"),
            ],
            limit=limit,
            order="date_deadline asc",
        )

        return [
            {
                "name": t.name,
                "deadline": t.date_deadline.isoformat() if t.date_deadline else None,
                "days_until": (
                    (t.date_deadline - today).days if t.date_deadline else None
                ),
                "owner": t.user_id.name if t.user_id else "Unassigned",
                "project": t.project_id.name if t.project_id else None,
            }
            for t in tasks
        ]

    @api.model
    def _get_bir_deadlines(self, limit=10):
        """Get upcoming BIR filing deadlines"""
        # Check if the finance.bir.deadline model exists
        if "finance.bir.deadline" not in self.env:
            return []

        Deadline = self.env["finance.bir.deadline"].sudo()
        today = date.today()
        next_month = today + timedelta(days=30)

        try:
            deadlines = Deadline.search(
                [
                    ("deadline_date", ">=", today.isoformat()),
                    ("deadline_date", "<=", next_month.isoformat()),
                ],
                limit=limit,
                order="deadline_date asc",
            )

            return [
                {
                    "form": d.name if hasattr(d, "name") else str(d),
                    "deadline": (
                        d.deadline_date.isoformat()
                        if hasattr(d, "deadline_date")
                        else None
                    ),
                    "description": d.description if hasattr(d, "description") else None,
                }
                for d in deadlines
            ]
        except Exception as e:
            _logger.warning("Could not retrieve BIR deadlines: %s", str(e))
            return []

    @api.model
    def _get_expense_summary(self):
        """Get expense summary statistics"""
        Expense = self.env["hr.expense"].sudo()
        today = date.today()
        month_start = today.replace(day=1)

        try:
            # Get counts by state
            pending = Expense.search_count(
                [("state", "=", "draft"), ("date", ">=", month_start.isoformat())]
            )
            submitted = Expense.search_count(
                [("state", "=", "reported"), ("date", ">=", month_start.isoformat())]
            )
            approved = Expense.search_count(
                [("state", "=", "approved"), ("date", ">=", month_start.isoformat())]
            )

            # Get OCR status if module is installed
            needs_review = 0
            if "digitization_status" in Expense._fields:
                needs_review = Expense.search_count([("needs_review", "=", True)])

            return {
                "month": today.strftime("%B %Y"),
                "pending": pending,
                "submitted": submitted,
                "approved": approved,
                "needs_ocr_review": needs_review,
            }
        except Exception as e:
            _logger.warning("Could not retrieve expense summary: %s", str(e))
            return {}

    @api.model
    def _get_finance_kpis(self, project_id=None):
        """Get finance KPIs for the current period"""
        Task = self.env["project.task"].sudo()
        today = date.today()

        domain = [("is_finance_ppm", "=", True)]
        if project_id:
            domain.append(("project_id", "=", project_id))

        total = Task.search_count(domain)
        completed = Task.search_count(domain + [("finance_state", "=", "done")])
        overdue = Task.search_count(
            domain
            + [
                ("date_deadline", "<", today.isoformat()),
                ("finance_state", "!=", "done"),
            ]
        )

        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total_tasks": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round(completion_rate, 1),
            "in_progress": Task.search_count(
                domain + [("finance_state", "=", "active")]
            ),
            "under_review": Task.search_count(
                domain + [("finance_state", "=", "review")]
            ),
        }

    @api.model
    def format_context_for_prompt(self, context):
        """
        Format retrieved context into a prompt-ready string.

        Args:
            context: Dict from retrieve_context()

        Returns:
            str: Formatted context for LLM prompt
        """
        parts = []

        parts.append(f"Today's Date: {context.get('today', 'Unknown')}")
        parts.append(f"User: {context.get('user_name', 'Unknown')}")
        parts.append("")

        # Blocking tasks
        if context.get("blocking_tasks"):
            bt = context["blocking_tasks"]
            parts.append(f"## Blocking Tasks ({bt.get('total', 0)} total)")
            for owner, tasks in bt.get("by_owner", {}).items():
                parts.append(f"### {owner} ({len(tasks)} tasks)")
                for t in tasks:
                    parts.append(
                        f"- {t['name']} (due: {t['deadline']}, {t['days_overdue']} days overdue)"
                    )
            parts.append("")

        # Upcoming deadlines
        if context.get("upcoming_deadlines"):
            parts.append("## Upcoming Deadlines")
            for d in context["upcoming_deadlines"]:
                parts.append(
                    f"- {d['name']} - Due: {d['deadline']} ({d['days_until']} days) - {d['owner']}"
                )
            parts.append("")

        # BIR deadlines
        if context.get("bir_deadlines"):
            parts.append("## BIR Tax Deadlines")
            for b in context["bir_deadlines"]:
                parts.append(f"- {b['form']}: {b['deadline']}")
            parts.append("")

        # Expense summary
        if context.get("expense_summary"):
            es = context["expense_summary"]
            parts.append(f"## Expense Summary ({es.get('month', 'Current Month')})")
            parts.append(f"- Pending: {es.get('pending', 0)}")
            parts.append(f"- Submitted: {es.get('submitted', 0)}")
            parts.append(f"- Approved: {es.get('approved', 0)}")
            if es.get("needs_ocr_review"):
                parts.append(f"- Needs OCR Review: {es['needs_ocr_review']}")
            parts.append("")

        # Finance KPIs
        if context.get("finance_kpis"):
            kpi = context["finance_kpis"]
            parts.append("## Finance Task KPIs")
            parts.append(f"- Total Tasks: {kpi.get('total_tasks', 0)}")
            parts.append(f"- Completed: {kpi.get('completed', 0)}")
            parts.append(f"- Completion Rate: {kpi.get('completion_rate', 0)}%")
            parts.append(f"- Overdue: {kpi.get('overdue', 0)}")
            parts.append(f"- In Progress: {kpi.get('in_progress', 0)}")
            parts.append(f"- Under Review: {kpi.get('under_review', 0)}")

        return "\n".join(parts)
