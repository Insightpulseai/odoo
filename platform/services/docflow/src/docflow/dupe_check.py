from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from .odoo_rpc import OdooRpc


@dataclass
class DupeHit:
    model: str
    record_id: int
    score: float
    reason: str
    fields: Dict[str, Any]


@dataclass
class DupeResult:
    risk: float  # 0..1
    hits: List[DupeHit]


def _cap(x: float) -> float:
    return max(0.0, min(1.0, x))


def check_invoice_duplicates(
    odoo: OdooRpc,
    partner_id: Optional[int],
    invoice_number: Optional[str],
    total: float,
    invoice_date: Optional[str],
) -> DupeResult:
    """
    Searches Odoo account.move vendor bills for likely duplicates.
    Strategy:
      - If invoice_number present: strong signal on partner_id + ref/Name + amount_total close
      - If not: partner + amount_total close + date proximity
    """
    hits: List[DupeHit] = []

    # Base domain: vendor bills only
    domain = [["move_type", "=", "in_invoice"]]

    if partner_id:
        domain.append(["partner_id", "=", int(partner_id)])

    # Strong path: invoice number
    if invoice_number:
        domain_num = domain + [["ref", "ilike", invoice_number]]
        rows = odoo.call_kw(
            "account.move",
            "search_read",
            [domain_num],
            {
                "fields": ["id", "ref", "invoice_date", "amount_total", "state", "partner_id"],
                "limit": 10,
                "order": "id desc",
            },
        )
        for r in rows:
            amt = float(r.get("amount_total") or 0.0)
            # amount closeness within 1% or 2 units
            tol = max(2.0, 0.01 * max(total, 1.0))
            if abs(amt - total) <= tol:
                hits.append(
                    DupeHit(
                        model="account.move",
                        record_id=int(r["id"]),
                        score=1.0,
                        reason="partner+ref(invoice_number)+amount_total match within tolerance",
                        fields=r,
                    )
                )
            else:
                hits.append(
                    DupeHit(
                        model="account.move",
                        record_id=int(r["id"]),
                        score=0.7,
                        reason="partner+ref(invoice_number) match but amount differs",
                        fields=r,
                    )
                )

    # Weak path: amount/date proximity
    domain_amt = domain.copy()
    rows2 = odoo.call_kw(
        "account.move",
        "search_read",
        [domain_amt],
        {
            "fields": ["id", "ref", "invoice_date", "amount_total", "state", "partner_id"],
            "limit": 50,
            "order": "id desc",
        },
    )
    for r in rows2:
        amt = float(r.get("amount_total") or 0.0)
        tol = max(2.0, 0.01 * max(total, 1.0))
        if abs(amt - total) <= tol:
            score = 0.6
            reason = "partner+amount_total match within tolerance"
            if invoice_date and r.get("invoice_date") == invoice_date:
                score = 0.85
                reason = "partner+amount_total+invoice_date exact match"
            hits.append(
                DupeHit(
                    model="account.move",
                    record_id=int(r["id"]),
                    score=score,
                    reason=reason,
                    fields=r,
                )
            )

    risk = 0.0
    if hits:
        risk = _cap(max(h.score for h in hits))

    # de-duplicate hits by record_id keeping max score
    by_id = {}
    for h in hits:
        key = (h.model, h.record_id)
        if key not in by_id or h.score > by_id[key].score:
            by_id[key] = h
    return DupeResult(risk=risk, hits=list(by_id.values()))


def check_expense_duplicates(
    odoo: OdooRpc,
    amount: float,
    date: Optional[str],
    name_hint: Optional[str],
) -> DupeResult:
    """
    Searches hr.expense for potential duplicates. Signals:
      - same total_amount within tolerance
      - same date
      - similar name (optional) is weaker and not used as hard constraint
    """
    hits: List[DupeHit] = []
    domain = []
    rows = odoo.call_kw(
        "hr.expense",
        "search_read",
        [domain],
        {
            "fields": ["id", "name", "date", "total_amount", "state"],
            "limit": 50,
            "order": "id desc",
        },
    )
    tol = max(2.0, 0.01 * max(amount, 1.0))
    for r in rows:
        amt = float(r.get("total_amount") or 0.0)
        if abs(amt - amount) <= tol:
            score = 0.5
            reason = "total_amount match within tolerance"
            if date and r.get("date") == date:
                score = 0.8
                reason = "total_amount+date match"
            hits.append(
                DupeHit(
                    model="hr.expense", record_id=int(r["id"]), score=score, reason=reason, fields=r
                )
            )

    risk = 0.0
    if hits:
        risk = _cap(max(h.score for h in hits))
    by_id = {}
    for h in hits:
        key = (h.model, h.record_id)
        if key not in by_id or h.score > by_id[key].score:
            by_id[key] = h
    return DupeResult(risk=risk, hits=list(by_id.values()))
