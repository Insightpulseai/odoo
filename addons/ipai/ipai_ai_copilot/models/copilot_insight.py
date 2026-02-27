"""
ipai.copilot.insight — Proactive business insights.

Populated by cron job (daily at 06:00 UTC). Displayed in copilot sidebar "Insights" tab.
Insights are targeted to specific users or broadcast to all users (user_id = False).
"""
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class IpaiCopilotInsight(models.Model):
    _name = "ipai.copilot.insight"
    _description = "IPAI Copilot Proactive Insight"
    _order = "priority desc, date desc"

    title = fields.Char(required=True)
    body = fields.Text()
    category = fields.Selection(
        [
            ("finance", "Finance"),
            ("sales", "Sales"),
            ("inventory", "Inventory"),
            ("hr", "HR"),
            ("system", "System"),
        ],
        default="system",
    )
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important"), ("2", "Critical")],
        default="0",
    )
    date = fields.Datetime(default=fields.Datetime.now)
    user_id = fields.Many2one(
        "res.users",
        help="Target user. Leave empty to show to all users.",
    )
    action_model = fields.Char(help="Model to navigate to when user acts on this insight.")
    action_domain = fields.Char(help="Domain filter for the action model.")
    dismissed = fields.Boolean(default=False)

    def _to_dict(self):
        """Return JSON-serializable dict for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body or "",
            "category": self.category,
            "priority": self.priority,
            "date": self.date.isoformat() if self.date else None,
            "action_model": self.action_model or "",
            "action_domain": self.action_domain or "",
        }

    @api.model
    def _run_proactive_insights(self):
        """
        Scheduled method: generate proactive insights from Odoo data.
        Called by ir.cron daily at 06:00 UTC.
        Creates or updates insight records; avoids duplicates by checking title.
        """
        import datetime

        today = datetime.date.today()
        week_ahead = today + datetime.timedelta(days=7)
        created = 0

        # Rule 1: Overdue invoices
        try:
            overdue_invoices = self.env["account.move"].search(
                [
                    ("move_type", "in", ["out_invoice", "out_refund"]),
                    ("state", "=", "posted"),
                    ("payment_state", "not in", ["paid", "reversed"]),
                    ("invoice_date_due", "<", today),
                ]
            )
            if overdue_invoices:
                self._upsert_insight(
                    title=f"{len(overdue_invoices)} overdue invoice(s)",
                    body=f"You have {len(overdue_invoices)} customer invoice(s) past due. "
                    f"Total outstanding: review in Accounting.",
                    category="finance",
                    priority="1" if len(overdue_invoices) >= 5 else "0",
                    action_model="account.move",
                    action_domain=str(
                        [
                            ("move_type", "in", ["out_invoice", "out_refund"]),
                            ("payment_state", "not in", ["paid", "reversed"]),
                            ("invoice_date_due", "<", today.isoformat()),
                        ]
                    ),
                )
                created += 1
        except Exception as exc:
            _logger.warning("Copilot insight: overdue invoices rule failed: %s", exc)

        # Rule 2: Deals closing this week
        try:
            closing_leads = self.env["crm.lead"].search(
                [
                    ("type", "=", "opportunity"),
                    ("active", "=", True),
                    ("date_deadline", ">=", today),
                    ("date_deadline", "<=", week_ahead),
                    ("probability", "<", 100),
                ]
            )
            if closing_leads:
                self._upsert_insight(
                    title=f"{len(closing_leads)} deal(s) closing this week",
                    body=f"{len(closing_leads)} opportunity/ies have deadlines in the next 7 days.",
                    category="sales",
                    priority="1",
                    action_model="crm.lead",
                    action_domain=str(
                        [
                            ("date_deadline", ">=", today.isoformat()),
                            ("date_deadline", "<=", week_ahead.isoformat()),
                        ]
                    ),
                )
                created += 1
        except Exception as exc:
            _logger.warning("Copilot insight: deals closing rule failed: %s", exc)

        # Rule 3: Low stock (qty_available < 5 for storable products)
        try:
            low_stock = self.env["product.product"].search(
                [
                    ("type", "=", "product"),
                    ("qty_available", "<", 5),
                    ("active", "=", True),
                ]
            )
            if low_stock:
                self._upsert_insight(
                    title=f"{len(low_stock)} product(s) low on stock",
                    body=f"{len(low_stock)} storable product(s) have fewer than 5 units on hand.",
                    category="inventory",
                    priority="1" if len(low_stock) >= 3 else "0",
                    action_model="product.product",
                    action_domain=str([("qty_available", "<", 5), ("type", "=", "product")]),
                )
                created += 1
        except Exception as exc:
            _logger.warning("Copilot insight: low stock rule failed: %s", exc)

        # Rule 4: Pending leave approvals
        try:
            pending_leaves = self.env["hr.leave"].search(
                [("state", "=", "validate1")]
            )
            if pending_leaves:
                self._upsert_insight(
                    title=f"{len(pending_leaves)} leave request(s) pending approval",
                    body=f"{len(pending_leaves)} employee leave request(s) are waiting for second approval.",
                    category="hr",
                    priority="1",
                    action_model="hr.leave",
                    action_domain=str([("state", "=", "validate1")]),
                )
                created += 1
        except Exception as exc:
            _logger.warning("Copilot insight: pending leaves rule failed: %s", exc)

        _logger.info("IPAI Copilot: generated %d insights", created)

    def _upsert_insight(self, title, body, category, priority, action_model="", action_domain=""):
        """Create or update an insight, avoiding duplicates by title."""
        existing = self.search([("title", "=", title), ("dismissed", "=", False)], limit=1)
        vals = {
            "title": title,
            "body": body,
            "category": category,
            "priority": priority,
            "action_model": action_model,
            "action_domain": action_domain,
            "date": fields.Datetime.now(),
            "dismissed": False,
        }
        if existing:
            existing.write(vals)
        else:
            self.create(vals)
