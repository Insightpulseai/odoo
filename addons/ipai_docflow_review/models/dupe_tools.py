from odoo import models
from rapidfuzz import fuzz, process


class DocflowDupeTools(models.AbstractModel):
    _name = "docflow.dupe.tools"
    _description = "DocFlow Duplicate + Vendor Match Tools"

    def vendor_fuzzy_match(self, vendor_name: str, min_score: float = 0.85, limit: int = 500):
        if not vendor_name:
            return {"partner_id": False, "score": 0.0, "method": "none"}

        vn = " ".join(vendor_name.strip().split())
        partners = self.env["res.partner"].search_read(
            [("supplier_rank", ">", 0), ("active", "=", True)],
            ["id", "name"],
            limit=limit,
        )
        if not partners:
            partners = self.env["res.partner"].search_read(
                [("active", "=", True)],
                ["id", "name"],
                limit=limit,
            )

        names = [p["name"] for p in partners if p.get("name")]
        if not names:
            return {"partner_id": False, "score": 0.0, "method": "none"}

        m = process.extractOne(vn, names, scorer=fuzz.token_set_ratio)
        if not m:
            return {"partner_id": False, "score": 0.0, "method": "none"}

        name, score, idx = m
        sf = score / 100.0
        if sf >= min_score:
            return {"partner_id": partners[idx]["id"], "score": sf, "method": "fuzzy", "name": name}
        return {"partner_id": False, "score": sf, "method": "none"}

    def invoice_dupe_search(
        self, partner_id: int, invoice_number: str, total: float, invoice_date: str | None
    ):
        domain = [("move_type", "=", "in_invoice")]
        if partner_id:
            domain.append(("partner_id", "=", partner_id))

        hits = []

        if invoice_number:
            rows = self.env["account.move"].search_read(
                domain + [("ref", "ilike", invoice_number)],
                ["id", "ref", "invoice_date", "amount_total", "state"],
                limit=10,
                order="id desc",
            )
            for r in rows:
                hits.append({"id": r["id"], "score": 1.0, "reason": "partner+ref match", "row": r})

        rows2 = self.env["account.move"].search_read(
            domain,
            ["id", "ref", "invoice_date", "amount_total", "state"],
            limit=50,
            order="id desc",
        )

        tol = max(2.0, 0.01 * max(total, 1.0))
        for r in rows2:
            if abs((r.get("amount_total") or 0.0) - total) <= tol:
                score = 0.6
                reason = "partner+amount_total match"
                if invoice_date and r.get("invoice_date") == invoice_date:
                    score = 0.85
                    reason = "partner+amount_total+date match"
                hits.append({"id": r["id"], "score": score, "reason": reason, "row": r})

        risk = max([h["score"] for h in hits], default=0.0)
        by = {}
        for h in hits:
            rid = h["id"]
            if rid not in by or h["score"] > by[rid]["score"]:
                by[rid] = h
        return {"risk": risk, "hits": list(by.values())}

    def expense_dupe_search(self, amount: float, date: str | None):
        rows = self.env["hr.expense"].search_read(
            [],
            ["id", "name", "date", "total_amount", "state"],
            limit=50,
            order="id desc",
        )
        hits = []
        tol = max(2.0, 0.01 * max(amount, 1.0))
        for r in rows:
            if abs((r.get("total_amount") or 0.0) - amount) <= tol:
                score = 0.5
                reason = "amount match"
                if date and r.get("date") == date:
                    score = 0.8
                    reason = "amount+date match"
                hits.append({"id": r["id"], "score": score, "reason": reason, "row": r})

        risk = max([h["score"] for h in hits], default=0.0)
        by = {}
        for h in hits:
            rid = h["id"]
            if rid not in by or h["score"] > by[rid]["score"]:
                by[rid] = h
        return {"risk": risk, "hits": list(by.values())}
