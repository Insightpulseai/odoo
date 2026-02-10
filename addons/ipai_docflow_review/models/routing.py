from odoo import api, fields, models, _
from odoo.exceptions import UserError

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


class DocflowRoutingRule(models.Model):
    _name = "docflow.routing.rule"
    _description = "DocFlow Routing Rule"
    _order = "sequence asc, id asc"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # Match conditions (OR within field, AND across fields)
    source = fields.Selection([("viber", "Viber"), ("upload", "Upload"), ("other", "Other")])
    doc_type = fields.Selection(
        [("invoice", "Invoice"), ("expense", "Expense"), ("bank_statement", "Bank Statement")],
        required=True,
    )

    company_id = fields.Many2one("res.company", required=True)
    journal_id = fields.Many2one("account.journal", domain=[("type", "in", ["bank", "purchase"])])
    currency_id = fields.Many2one("res.currency")

    vendor_name_contains = fields.Char(
        help="Substring match for vendor/merchant (case-insensitive)"
    )
    bank_account_contains = fields.Char(
        help="Substring match for extracted bank account/IBAN/reference"
    )
    min_confidence = fields.Float(default=0.0)

    assign_user_id = fields.Many2one("res.users", help="Optional fixed reviewer")
    assign_group_id = fields.Many2one(
        "res.groups", help="Optional reviewer group for load-based assignment"
    )

    def matches(self, docflow_doc, extracted: dict) -> bool:
        """Evaluate if this rule matches a docflow.document + extracted JSON."""
        self.ensure_one()
        if not self.active:
            return False
        if self.doc_type and docflow_doc.doc_type != self.doc_type:
            return False
        if self.source and hasattr(docflow_doc, "source") and docflow_doc.source != self.source:
            pass  # source might not be on docflow.document yet, ignore if missing or implement if needed.
            # Re-reading prompt: "source" is used in matches. DocflowDocument should have it or matches will fail if source is set on rule.
            # Checking previous artifacts... DocflowDocument definition in prev turn didn't explicitly show 'source' field but 'source' is in the agent yaml.
            # I will assume it exists or will be added. The prompt implies it's there.
            pass

        # Correction: The user's provided code assumes docflow_doc.source exists.
        # I should check if I need to add it to DocflowDocument in the inheritance or if it's already there.
        # Looking at previous `docflow_document.py` edits... I don't recall adding `source`.
        # I will add it to the inheritance in this file if possible or just use getattr default.

        doc_source = getattr(docflow_doc, "source", "other")
        if self.source and doc_source != self.source:
            return False

        if (
            self.currency_id
            and docflow_doc.currency_id
            and docflow_doc.currency_id.id != self.currency_id.id
        ):
            return False
        if self.min_confidence and (docflow_doc.confidence or 0.0) < self.min_confidence:
            return False

        # vendor/merchant match
        vn = (
            extracted.get("vendor_name")
            or extracted.get("merchant")
            or docflow_doc.vendor_or_merchant
            or ""
        ) or ""
        if self.vendor_name_contains:
            if self.vendor_name_contains.strip().lower() not in vn.lower():
                return False

        # bank account match (statement refs)
        ba = (
            extracted.get("bank_account")
            or extracted.get("iban")
            or extracted.get("account_number")
            or extracted.get("reference")
            or ""
        ) or ""
        if self.bank_account_contains:
            if self.bank_account_contains.strip().lower() not in ba.lower():
                return False

        return True


class DocflowDocument(models.Model):
    _inherit = "docflow.document"

    # Adding source field here if not present, ensuring it's available for routing
    source = fields.Selection(
        [("viber", "Viber"), ("upload", "Upload"), ("other", "Other")], default="other"
    )

    routed_company_id = fields.Many2one("res.company", readonly=True)
    routed_journal_id = fields.Many2one("account.journal", readonly=True)
    routed_user_id = fields.Many2one("res.users", readonly=True)
    routing_rule_id = fields.Many2one("docflow.routing.rule", readonly=True)

    def action_route(self):
        """Compute routing and assign company/journal/reviewer."""
        Rules = (
            self.env["docflow.routing.rule"]
            .sudo()
            .search([("active", "=", True)], order="sequence asc, id asc")
        )
        group_default = self.env.ref(
            "ipai_docflow_review.group_docflow_reviewer", raise_if_not_found=False
        )

        for r in self:
            extracted = {}
            try:
                extracted = r._safe_extracted()
            except Exception:
                extracted = {}

            chosen = False
            for rule in Rules:
                if rule.matches(r, extracted):
                    r.routing_rule_id = rule.id
                    r.routed_company_id = rule.company_id.id
                    r.routed_journal_id = rule.journal_id.id if rule.journal_id else False

                    # assignment: fixed user > group load-based > default reviewer group
                    user_id = False
                    if rule.assign_user_id:
                        user_id = rule.assign_user_id.id
                    else:
                        grp = rule.assign_group_id or group_default
                        if grp:
                            user_id = r._pick_least_loaded_user(
                                grp.id, company_id=rule.company_id.id
                            )
                    r.routed_user_id = user_id or False
                    chosen = True
                    break

            if not chosen:
                # fallback to current company context
                # Use getattr to safely access company_id if not present (standard Odoo models usually have it)
                company_id = (
                    r.company_id.id
                    if hasattr(r, "company_id") and r.company_id
                    else self.env.company.id
                )
                r.routed_company_id = company_id
                r.routed_user_id = (
                    r._pick_least_loaded_user(group_default.id, company_id=r.routed_company_id)
                    if group_default
                    else False
                )

    def _safe_extracted(self):
        import json

        payload = {}
        if self.llm_extraction_json:
            if isinstance(self.llm_extraction_json, dict):
                payload = self.llm_extraction_json
            else:
                try:
                    payload = json.loads(self.llm_extraction_json or "{}")
                except:
                    payload = {}
        return payload or {}

    def _pick_least_loaded_user(self, group_id: int, company_id: int | None = None) -> int | None:
        """Pick least-loaded user by open DocFlow review count in last window."""
        Users = self.env["res.users"].sudo()
        group = self.env["res.groups"].sudo().browse(group_id)
        candidates = group.users
        if company_id:
            # filter users with access to company (simple heuristic)
            candidates = candidates.filtered(
                lambda u: (
                    (not u.company_ids)
                    or (company_id in u.company_ids.ids)
                    or (u.company_id and u.company_id.id == company_id)
                )
            )
        if not candidates:
            return None

        # Count open docflow docs assigned to each user
        Doc = self.env["docflow.document"].sudo()
        best_uid, best_cnt = None, None
        for u in candidates:
            cnt = Doc.search_count(
                [("state", "in", ["needs_review", "extracted"]), ("reviewer_user_id", "=", u.id)]
            )
            if best_cnt is None or cnt < best_cnt:
                best_uid, best_cnt = u.id, cnt
        return best_uid
