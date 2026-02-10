from odoo import fields, models, api, _
import json

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


class DocflowReconSession(models.Model):
    _name = "docflow.recon.session"
    _description = "DocFlow Reconciliation Session"
    _order = "create_date desc"

    name = fields.Char(required=True)
    statement_id = fields.Many2one("docflow.bank.statement", required=True, ondelete="cascade")
    document_id = fields.Many2one(related="statement_id.document_id", store=True, readonly=True)

    state = fields.Selection(
        [("new", "New"), ("in_progress", "In Progress"), ("done", "Done")], default="new"
    )
    candidate_ids = fields.One2many("docflow.recon.candidate", "session_id")

    auto_threshold = fields.Float(default=0.90)
    date_window_days = fields.Integer(default=7)

    def action_generate_candidates(self):
        """Server-side candidate generation (fast, auditable)."""
        for s in self:
            s.candidate_ids.unlink()
            lines = s.statement_id.line_ids
            for line in lines:
                # Search payments around date +/- window and amount tolerance
                # NOTE: domains can be tuned per your accounting conventions.
                candidates = []

                # 1) account.payment candidates
                pay_domain = [
                    ("state", "in", ["posted"]),
                    ("amount", ">", 0),
                ]
                payments = self.env["account.payment"].search(
                    pay_domain, limit=200, order="date desc"
                )

                for p in payments:
                    score = _score_match(
                        line,
                        p.amount,
                        str(p.date),
                        p.ref or p.name or "",
                        getattr(p.partner_id, "name", "") or "",
                        s.date_window_days,
                    )
                    if score >= 0.60:
                        candidates.append(
                            ("account.payment", p.id, score, f"payment ref={p.ref or p.name}")
                        )

                # 2) account.move (vendor/customer invoices) candidates
                move_domain = [
                    ("state", "=", "posted"),
                    ("move_type", "in", ["in_invoice", "out_invoice"]),
                ]
                moves = self.env["account.move"].search(
                    move_domain, limit=200, order="invoice_date desc"
                )
                for m in moves:
                    amt = abs(m.amount_total_signed)
                    score = _score_match(
                        line,
                        amt,
                        str(m.invoice_date or m.date),
                        m.ref or m.name or "",
                        getattr(m.partner_id, "name", "") or "",
                        s.date_window_days,
                    )
                    if score >= 0.60:
                        candidates.append(
                            ("account.move", m.id, score, f"move ref={m.ref or m.name}")
                        )

                candidates.sort(key=lambda x: x[2], reverse=True)
                for model, rid, score, reason in candidates[:10]:
                    self.env["docflow.recon.candidate"].create(
                        {
                            "session_id": s.id,
                            "statement_line_id": line.id,
                            "candidate_model": model,
                            "candidate_id": rid,
                            "score": score,
                            "reason": reason,
                        }
                    )

                # Auto-accept top candidate if above threshold
                if candidates and candidates[0][2] >= s.auto_threshold:
                    model, rid, score, reason = candidates[0]
                    line.write(
                        {
                            "matched_model": model,
                            "matched_id": rid,
                            "match_score": score,
                            "match_reason": reason,
                            "match_state": "suggested",
                        }
                    )


def _score_match(
    line, candidate_amount, candidate_date_str, candidate_ref, candidate_partner, date_window_days
):
    # amount score (tight)
    tol = max(2.0, 0.01 * max(abs(line.amount), 1.0))
    amount_score = 1.0 if abs(abs(candidate_amount) - abs(line.amount)) <= tol else 0.0

    # date score (soft)
    date_score = 0.5
    if line.date and candidate_date_str:
        # naive: exact match boosts (Odoo date string 'YYYY-MM-DD')
        date_score = 1.0 if str(line.date) == candidate_date_str else 0.6

    # reference similarity
    ref_score = 0.0
    if line.reference and candidate_ref and fuzz:
        ref_score = fuzz.token_set_ratio(line.reference, candidate_ref) / 100.0

    # counterparty similarity
    party_score = 0.0
    if line.counterparty and candidate_partner and fuzz:
        party_score = fuzz.token_set_ratio(line.counterparty, candidate_partner) / 100.0

    # weighted
    return round(0.55 * amount_score + 0.20 * date_score + 0.15 * ref_score + 0.10 * party_score, 2)


class DocflowReconCandidate(models.Model):
    _name = "docflow.recon.candidate"
    _description = "DocFlow Reconciliation Candidate"
    _order = "score desc, id desc"

    session_id = fields.Many2one("docflow.recon.session", required=True, ondelete="cascade")
    statement_line_id = fields.Many2one(
        "docflow.bank.statement.line", required=True, ondelete="cascade"
    )

    candidate_model = fields.Selection(
        [("account.payment", "Payment"), ("account.move", "Invoice")], required=True
    )
    candidate_id = fields.Integer(required=True)

    score = fields.Float(digits=(3, 2), required=True)
    reason = fields.Char()

    def action_apply_to_line(self):
        self.ensure_one()
        self.statement_line_id.write(
            {
                "matched_model": self.candidate_model,
                "matched_id": self.candidate_id,
                "match_score": self.score,
                "match_reason": self.reason,
                "match_state": "suggested",
            }
        )
