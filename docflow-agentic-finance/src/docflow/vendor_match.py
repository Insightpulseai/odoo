from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, List

# rapidfuzz is optional-dependency but required for this feature
try:
    from rapidfuzz import fuzz, process
except ImportError:
    fuzz = None
    process = None

from .odoo_rpc import OdooRpc


@dataclass
class VendorMatch:
    partner_id: Optional[int]
    partner_name: Optional[str]
    score: float
    method: str  # exact | fuzzy | fallback | none


def _normalize_name(s: str) -> str:
    return " ".join((s or "").strip().split()).lower()


def resolve_vendor_partner_id(
    odoo: OdooRpc,
    vendor_name: Optional[str],
) -> VendorMatch:
    """
    Resolve vendor partner_id using:
      1) exact-ish ilike search
      2) fuzzy match over top-N partners (supplier_rank > 0 preferred)
      3) fallback env var ODOO_DEFAULT_VENDOR_PARTNER_ID
    """
    fallback = int(os.getenv("ODOO_DEFAULT_VENDOR_PARTNER_ID", "0")) or None

    if not vendor_name or not vendor_name.strip():
        return VendorMatch(
            partner_id=fallback,
            partner_name=None,
            score=0.0,
            method="fallback" if fallback else "none",
        )

    vn = vendor_name.strip()

    # 1) Exact-ish: ilike
    exact = odoo.call_kw(
        "res.partner",
        "search_read",
        [[["name", "ilike", vn]]],
        {"fields": ["id", "name"], "limit": 5},
    )
    # If using rapidfuzz, refine match
    if exact and fuzz:
        # Pick best by fuzz ratio to reduce false positives
        best = None
        best_score = -1
        for c in exact:
            sc = fuzz.token_set_ratio(_normalize_name(vn), _normalize_name(c["name"]))
            if sc > best_score:
                best_score = sc
                best = c
        if best and best_score >= float(os.getenv("VENDOR_MATCH_EXACT_MIN", "95")):
            return VendorMatch(
                partner_id=int(best["id"]),
                partner_name=best["name"],
                score=best_score / 100.0,
                method="exact",
            )
    elif exact:
        # simple first match if no fuzz
        best = exact[0]
        return VendorMatch(
            partner_id=int(best["id"]), partner_name=best["name"], score=1.0, method="exact"
        )

    if not fuzz:
        # Cannot proceed with fuzzy strategies without rapidfuzz
        return VendorMatch(
            partner_id=fallback,
            partner_name=None,
            score=0.0,
            method="fallback" if fallback else "none",
        )

    # 2) Fuzzy over supplier-like partners first
    limit = int(os.getenv("VENDOR_MATCH_CANDIDATE_LIMIT", "500"))
    candidates = odoo.call_kw(
        "res.partner",
        "search_read",
        [[["supplier_rank", ">", 0], ["active", "=", True]]],
        {"fields": ["id", "name"], "limit": limit},
    )

    # Fallback pool if none
    if not candidates:
        candidates = odoo.call_kw(
            "res.partner",
            "search_read",
            [[["active", "=", True]]],
            {"fields": ["id", "name"], "limit": limit},
        )

    names: List[str] = [c["name"] for c in candidates if c.get("name")]
    if not names:
        return VendorMatch(
            partner_id=fallback,
            partner_name=None,
            score=0.0,
            method="fallback" if fallback else "none",
        )

    # rapidfuzz best match
    match = process.extractOne(
        query=vn,
        choices=names,
        scorer=fuzz.token_set_ratio,
    )
    if not match:
        return VendorMatch(
            partner_id=fallback,
            partner_name=None,
            score=0.0,
            method="fallback" if fallback else "none",
        )

    matched_name, score, idx = match
    score_f = score / 100.0
    min_score = float(os.getenv("VENDOR_MATCH_FUZZY_MIN", "0.85"))

    if score_f >= min_score:
        partner_id = int(candidates[idx]["id"])
        return VendorMatch(
            partner_id=partner_id, partner_name=matched_name, score=score_f, method="fuzzy"
        )

    return VendorMatch(
        partner_id=fallback,
        partner_name=None,
        score=score_f,
        method="fallback" if fallback else "none",
    )
