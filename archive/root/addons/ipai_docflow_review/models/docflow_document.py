import json
from datetime import timedelta

from odoo.exceptions import UserError

from odoo import _, api, fields, models


def _safe_json_load(s):
    if not s:
        return {}
    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except Exception:
        return {}


def _dict_diff(prev: dict, curr: dict) -> str:
    lines = []
    all_keys = sorted(set(prev.keys()) | set(curr.keys()))
    for k in all_keys:
        pv = prev.get(k)
        cv = curr.get(k)
        if pv == cv:
            continue
        if isinstance(pv, str) and len(pv) > 200:
            pv = pv[:200] + "…"
        if isinstance(cv, str) and len(cv) > 200:
            cv = cv[:200] + "…"
        lines.append(f"- {k}: {pv!r} -> {cv!r}")
    return "\n".join(lines) if lines else "No changes detected."


class DocflowDocument(models.Model):
    _name = "docflow.document"
    _description = "DocFlow Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default=lambda self: _("DocFlow Document"), tracking=True)
    document_id = fields.Char(index=True, required=True, tracking=True)
    file_hash = fields.Char(index=True)

    source = fields.Selection(
        [("viber", "Viber"), ("upload", "Upload"), ("other", "Other")],
        default="viber",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("extracted", "Extracted"),
            ("needs_review", "Needs Review"),
            ("approved", "Approved"),
            ("draft_created", "Draft Created"),
            ("rejected", "Rejected"),
            ("failed", "Failed"),
        ],
        default="new",
        tracking=True,
    )

    doc_type = fields.Selection(
        [("invoice", "Invoice"), ("expense", "Expense"), ("unknown", "Unknown")],
        default="unknown",
        tracking=True,
    )
    confidence = fields.Float(digits=(3, 2), tracking=True)
    confidence_breakdown_json = fields.Text()

    attachment_id = fields.Many2one(
        "ir.attachment", string="Source Document", ondelete="set null"
    )

    ocr_text = fields.Text()
    llm_classification_json = fields.Text()
    llm_extraction_json = fields.Text()
    validation_json = fields.Text()

    # Normalized summary fields (list view)
    vendor_or_merchant = fields.Char()
    doc_date = fields.Date()
    amount_total = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one("res.currency")

    # Structured editor (Invoice)
    vendor_name = fields.Char()
    invoice_number = fields.Char()
    invoice_date = fields.Date()
    subtotal = fields.Float()
    vat = fields.Float()
    total = fields.Float()

    # Structured editor (Expense)
    expense_description = fields.Char()
    expense_date = fields.Date()
    expense_amount = fields.Float()
    merchant = fields.Char()

    line_ids = fields.One2many(
        "docflow.document.line", "document_id", string="Line Items"
    )

    snapshot_ids = fields.One2many(
        "docflow.document.snapshot", "document_id", string="Snapshots", readonly=True
    )
    last_diff_text = fields.Text(readonly=True)

    # Vendor match + dupe detection signals (Odoo-backed)
    vendor_match_score = fields.Float(digits=(3, 2), readonly=True)
    vendor_match_method = fields.Char(readonly=True)
    vendor_match_partner_id = fields.Many2one("res.partner", readonly=True)
    dupe_risk = fields.Float(digits=(3, 2), readonly=True)
    dupe_hits_json = fields.Text(readonly=True)

    # Link to created record
    res_model = fields.Char()
    res_id = fields.Integer()

    res_ref = fields.Reference(
        selection=[("account.move", "Vendor Bill"), ("hr.expense", "Expense")],
        compute="_compute_res_ref",
        store=False,
    )

    @api.depends("res_model", "res_id")
    def _compute_res_ref(self):
        for r in self:
            r.res_ref = False
            if r.res_model and r.res_id:
                r.res_ref = f"{r.res_model},{r.res_id}"

    def _normalize_for_snapshot(self) -> dict:
        self.ensure_one()
        if self.doc_type == "invoice":
            return {
                "doc_type": "invoice",
                "vendor_name": self.vendor_name,
                "invoice_number": self.invoice_number,
                "invoice_date": str(self.invoice_date) if self.invoice_date else None,
                "currency": self.currency_id.name if self.currency_id else None,
                "subtotal": self.subtotal,
                "vat": self.vat,
                "total": self.total or self.amount_total,
                "lines": [
                    {
                        "description": l.description,
                        "quantity": l.quantity,
                        "unit_price": l.unit_price,
                        "line_total": l.line_total,
                    }
                    for l in self.line_ids
                ],
            }
        if self.doc_type == "expense":
            return {
                "doc_type": "expense",
                "description": self.expense_description,
                "date": str(self.expense_date) if self.expense_date else None,
                "amount": self.expense_amount or self.amount_total,
                "currency": self.currency_id.name if self.currency_id else None,
                "merchant": self.merchant,
            }
        return {"doc_type": "unknown"}

    def _docflow_parse_extraction_into_fields(self):
        for r in self:
            payload = _safe_json_load(r.llm_extraction_json)

            # Snapshot diff base
            prev = r.snapshot_ids[:1].payload_dict() if r.snapshot_ids else {}
            # Parse into structured editor
            if r.doc_type == "invoice":
                r.vendor_name = payload.get("vendor_name") or r.vendor_name
                r.invoice_number = payload.get("invoice_number") or r.invoice_number
                if payload.get("invoice_date"):
                    r.invoice_date = payload["invoice_date"]
                if payload.get("currency"):
                    cur = self.env["res.currency"].search(
                        [("name", "=", payload["currency"])], limit=1
                    )
                    if cur:
                        r.currency_id = cur.id
                if payload.get("subtotal") is not None:
                    r.subtotal = float(payload.get("subtotal") or 0.0)
                if payload.get("vat") is not None:
                    r.vat = float(payload.get("vat") or 0.0)
                if payload.get("total") is not None:
                    r.total = float(payload.get("total") or 0.0)
                r.amount_total = r.total or r.amount_total
                r.vendor_or_merchant = r.vendor_name or r.vendor_or_merchant
                if r.invoice_date:
                    r.doc_date = r.invoice_date

                # Replace line items if provided
                new_lines = payload.get("line_items") or []
                if new_lines:
                    r.line_ids.unlink()
                    for i, li in enumerate(new_lines):
                        r.line_ids.create(
                            {
                                "document_id": r.id,
                                "sequence": (i + 1) * 10,
                                "description": li.get("description") or "Item",
                                "quantity": float(li.get("quantity") or 1.0),
                                "unit_price": float(li.get("unit_price") or 0.0),
                            }
                        )

            elif r.doc_type == "expense":
                r.expense_description = (
                    payload.get("description") or r.expense_description or r.name
                )
                if payload.get("date"):
                    r.expense_date = payload["date"]
                if payload.get("amount") is not None:
                    r.expense_amount = float(payload.get("amount") or 0.0)
                r.merchant = payload.get("merchant") or r.merchant
                if payload.get("currency"):
                    cur = self.env["res.currency"].search(
                        [("name", "=", payload["currency"])], limit=1
                    )
                    if cur:
                        r.currency_id = cur.id
                r.amount_total = r.expense_amount or r.amount_total
                r.vendor_or_merchant = r.merchant or r.vendor_or_merchant
                if r.expense_date:
                    r.doc_date = r.expense_date

            # Snapshot + diff
            curr = r._normalize_for_snapshot()
            diff_text = _dict_diff(prev, curr)
            self.env["docflow.document.snapshot"].sudo().create(
                {
                    "document_id": r.id,
                    "source": "daemon",
                    "payload_json": json.dumps(curr, ensure_ascii=False),
                    "diff_text": diff_text,
                }
            )
            r.last_diff_text = diff_text

    def action_sync_structured_to_json(self):
        for r in self:
            if r.doc_type == "invoice":
                payload = {
                    "vendor_name": r.vendor_name,
                    "invoice_number": r.invoice_number,
                    "invoice_date": str(r.invoice_date) if r.invoice_date else None,
                    "currency": r.currency_id.name if r.currency_id else None,
                    "subtotal": r.subtotal or None,
                    "vat": r.vat or None,
                    "total": r.total or r.amount_total,
                    "line_items": [
                        {
                            "description": l.description,
                            "quantity": l.quantity,
                            "unit_price": l.unit_price,
                            "line_total": l.line_total,
                        }
                        for l in r.line_ids
                    ],
                    "confidence": r.confidence or 0.0,
                    "notes": None,
                }
            elif r.doc_type == "expense":
                payload = {
                    "description": r.expense_description,
                    "date": str(r.expense_date) if r.expense_date else None,
                    "amount": r.expense_amount or r.amount_total,
                    "currency": r.currency_id.name if r.currency_id else None,
                    "merchant": r.merchant,
                    "confidence": r.confidence or 0.0,
                }
            else:
                raise UserError(_("Set doc_type to invoice or expense first."))

            r.llm_extraction_json = json.dumps(payload, ensure_ascii=False)

    def action_compute_vendor_and_dupes(self):
        Tools = self.env["docflow.dupe.tools"]
        for r in self:
            if r.doc_type == "invoice":
                vm = Tools.vendor_fuzzy_match(
                    r.vendor_name or r.vendor_or_merchant or ""
                )
                r.vendor_match_partner_id = vm.get("partner_id") or False
                r.vendor_match_score = float(vm.get("score") or 0.0)
                r.vendor_match_method = vm.get("method") or "none"

                payload = _safe_json_load(r.llm_extraction_json)
                inv_no = payload.get("invoice_number") or r.invoice_number or ""
                total = float(payload.get("total") or r.total or r.amount_total or 0.0)
                inv_date = payload.get("invoice_date") or (
                    str(r.invoice_date) if r.invoice_date else None
                )

                dup = Tools.invoice_dupe_search(
                    partner_id=int(r.vendor_match_partner_id.id or 0),
                    invoice_number=inv_no,
                    total=total,
                    invoice_date=inv_date,
                )
                r.dupe_risk = float(dup.get("risk") or 0.0)
                r.dupe_hits_json = json.dumps(dup, ensure_ascii=False)

            elif r.doc_type == "expense":
                payload = _safe_json_load(r.llm_extraction_json)
                amount = float(
                    payload.get("amount") or r.expense_amount or r.amount_total or 0.0
                )
                dt = payload.get("date") or (
                    str(r.expense_date) if r.expense_date else None
                )

                dup = Tools.expense_dupe_search(amount=amount, date=dt)
                r.dupe_risk = float(dup.get("risk") or 0.0)
                r.dupe_hits_json = json.dumps(dup, ensure_ascii=False)

    def action_mark_needs_review(self):
        self.write({"state": "needs_review"})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_approve_create_draft(self):
        for r in self:
            if r.state not in ("needs_review", "extracted", "approved"):
                raise UserError(_("Document not in a creatable state."))

            # Ensure JSON matches structured fields
            r.action_sync_structured_to_json()
            payload = _safe_json_load(r.llm_extraction_json)

            if r.doc_type == "expense":
                rec = r._create_expense(payload)
                r.write(
                    {
                        "state": "draft_created",
                        "res_model": "hr.expense",
                        "res_id": rec.id,
                    }
                )
            elif r.doc_type == "invoice":
                rec = r._create_vendor_bill(payload)
                r.write(
                    {
                        "state": "draft_created",
                        "res_model": "account.move",
                        "res_id": rec.id,
                    }
                )
            else:
                raise UserError(_("Unknown document type."))

            if r.attachment_id and r.res_model and r.res_id:
                r.attachment_id.write({"res_model": r.res_model, "res_id": r.res_id})

            r.write({"state": "approved"})

    def _create_expense(self, payload: dict):
        amount = float(payload.get("amount") or 0)
        if amount <= 0:
            raise UserError(_("Expense amount must be > 0."))

        name = payload.get("description") or "DocFlow Expense"
        currency = payload.get("currency")
        currency_id = (
            self.env["res.currency"].search([("name", "=", currency)], limit=1).id
            if currency
            else False
        )

        vals = {"name": name, "total_amount": amount}
        if currency_id:
            vals["currency_id"] = currency_id
        if payload.get("date"):
            vals["date"] = payload["date"]

        return self.env["hr.expense"].create(vals)

    def _create_vendor_bill(self, payload: dict):
        total = float(payload.get("total") or 0)
        if total <= 0:
            raise UserError(_("Invoice total must be > 0."))

        vendor_id = False
        if self.vendor_match_partner_id:
            vendor_id = self.vendor_match_partner_id.id
        elif payload.get("vendor_name"):
            vendor_id = (
                self.env["res.partner"]
                .search([("name", "ilike", payload.get("vendor_name"))], limit=1)
                .id
            )

        if not vendor_id:
            raise UserError(_("Vendor not resolved. Set a matching vendor."))

        currency = payload.get("currency")
        currency_id = (
            self.env["res.currency"].search([("name", "=", currency)], limit=1).id
            if currency
            else False
        )

        line_items = payload.get("line_items") or []
        lines = []
        if line_items:
            for li in line_items:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "name": li.get("description") or "Item",
                            "quantity": float(li.get("quantity") or 1),
                            "price_unit": float(
                                li.get("unit_price") or li.get("line_total") or 0
                            ),
                        },
                    )
                )
        else:
            lines = [
                (
                    0,
                    0,
                    {"name": "Invoice (DocFlow)", "quantity": 1, "price_unit": total},
                )
            ]

        vals = {
            "move_type": "in_invoice",
            "partner_id": vendor_id,
            "invoice_line_ids": lines,
        }
        if currency_id:
            vals["currency_id"] = currency_id
        if payload.get("invoice_date"):
            vals["invoice_date"] = payload["invoice_date"]
        if payload.get("invoice_number"):
            vals["ref"] = payload["invoice_number"]

        return self.env["account.move"].create(vals)

    # SLA Logic
    def _sla_default_due(self):
        hours = int(
            self.env["ir.config_parameter"].sudo().get_param("docflow.sla_hours", "24")
        )
        return fields.Datetime.now() + timedelta(hours=hours)

    def action_start_sla(self):
        """Call when state -> needs_review."""
        group = self.env.ref(
            "ipai_docflow_review.group_docflow_reviewer", raise_if_not_found=False
        )
        for r in self:
            if r.sla_state in ("active", "breached"):
                continue
            r.sla_due_at = r._sla_default_due()
            r.sla_state = "active"

            # naive assignment: first reviewer (can be replaced with load balancing later)
            if group and not r.reviewer_user_id:
                user = self.env["res.users"].search(
                    [("groups_id", "in", [group.id])], limit=1
                )
                if user:
                    r.reviewer_user_id = user.id

            if r.reviewer_user_id:
                r.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=r.reviewer_user_id.id,
                    date_deadline=r.sla_due_at.date(),
                    summary=_("DocFlow review due"),
                    note=_("Review and approve/reject this document."),
                )
            self.env["docflow.sla.event"].create(
                {"document_id": r.id, "event_type": "assigned", "note": "SLA started"}
            )

    @api.model
    def cron_docflow_sla_check(self):
        """Escalate overdue reviews."""
        # TODO: SLA fields missing - temporarily disabled
        return
        # now = fields.Datetime.now()
        # docs = self.search(
        #     [
        #         ("sla_state", "=", "active"),
        #         ("sla_due_at", "!=", False),
        #         ("sla_due_at", "<", now),
        #         ("state", "in", ["needs_review", "extracted"]),
        #     ]
        # )
        for r in docs:
            r.sla_state = "breached"
            self.env["docflow.sla.event"].create(
                {"document_id": r.id, "event_type": "breach", "note": "SLA breached"}
            )

            # escalate to manager (config param)
            mgr_id = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("docflow.sla_manager_user_id", "0")
                or 0
            )
            if mgr_id:
                r.manager_user_id = mgr_id
                r.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=mgr_id,
                    date_deadline=fields.Date.today(),
                    summary=_("SLA breach: DocFlow review overdue"),
                    note=_("This DocFlow item breached SLA. Please intervene."),
                )
                self.env["docflow.sla.event"].create(
                    {
                        "document_id": r.id,
                        "event_type": "escalated",
                        "note": f"Escalated to user_id={mgr_id}",
                    }
                )

    def write(self, vals):
        res = super().write(vals)
        # Route whenever extraction/doc_type/confidence changes
        if any(
            k in vals
            for k in [
                "llm_extraction_json",
                "doc_type",
                "confidence",
                "source",
                "currency_id",
            ]
        ):
            # self.action_route() # defined in routing.py inherit
            # Since inheriting method might not be available at define time if not loaded,
            # we rely on the fact that python resolution happens at runtime.
            if hasattr(self, "action_route"):
                self.action_route()

        if "state" in vals and vals["state"] == "needs_review":
            if hasattr(self, "action_route"):
                self.action_route()
            # TODO: SLA fields missing - temporarily disabled
            # self.action_start_sla()
        return res
