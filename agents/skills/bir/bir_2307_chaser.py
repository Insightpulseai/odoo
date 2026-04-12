# agents/skills/bir/bir_2307_chaser.py
"""
BIR 2307 Chaser (Reasoning Plane)
=================================
Proactively identifies missing client withholding tax certificates (Form 2307)
for paid invoices and drafts chaser notifications.

Grounded in Odoo l10n_ph primitives.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List

async def detect_missing_2307s() -> Dict[str, Any]:
    """
    Main entry point for the 2307 chaser logic.
    
    1. Query Odoo for paid invoices missing certificates via MCP.
    2. Analyze aging and priority.
    3. Draft chaser notifications.
    """
    logging.info("Starting BIR 2307 chaser detection run.")

    # Step 1: Data Retrieval (Mocked Odoo MCP search_read)
    invoices = await _get_paid_invoices_missing_certificates()
    
    if not invoices:
        return {"status": "Clean", "count": 0, "chasers": []}

    chasers = []
    total_wht_value = 0.0

    for inv in invoices:
        wht_amount = inv.get("l10n_ph_withholding_tax_amount", 0.0)
        total_wht_value += wht_amount
        
        # Step 2: Aging Analysis
        # Simulating invoice payment date
        payment_date = inv.get("payment_date", "2026-03-01")
        days_uncollected = (datetime.now() - datetime.strptime(payment_date, "%Y-%m-%d")).days
        
        # Step 3: Notification Drafting
        chasers.append({
            "invoice_id": inv["id"],
            "invoice_no": inv["name"],
            "customer": inv["partner_id"][1],
            "wht_amount": wht_amount,
            "days_uncollected": days_uncollected,
            "priority": "HIGH" if days_uncollected > 30 or wht_amount > 5000 else "LOW",
            "draft_notification": _draft_chaser_message(inv, days_uncollected)
        })

    return {
        "status": "Incomplete Certificates Found",
        "count": len(chasers),
        "total_uncollected_wht": round(total_wht_value, 2),
        "chasers": chasers,
        "benchmark": "bir-2307-chaser-v1"
    }

def _draft_chaser_message(inv: Dict[str, Any], days: int) -> str:
    """Drafts a high-fidelity chaser message."""
    customer = inv["partner_id"][1]
    inv_no = inv["name"]
    wht = inv["l10n_ph_withholding_tax_amount"]
    
    msg = (
        f"Subject: Follow-up on Withholding Tax Certificate (Form 2307) - {inv_no}\n"
        f"Dear {customer},\n\n"
        f"Our records show that Invoice {inv_no} has been settled, with a withholding tax "
        f"deduction of ₱{wht:,.2f}. However, we have not yet received the corresponding "
        f"BIR Form 2307 for this transaction.\n\n"
        f"As this payment was received {days} days ago, we kindly request the certificate "
        f"to ensure timely BIR compliance filing.\n\n"
        f"Please reply with the attached certificate or let us know if you need assistance."
    )
    return msg

async def _get_paid_invoices_missing_certificates() -> List[Dict[str, Any]]:
    """Simulates odoo_search_read for missing certificates via MCP."""
    # Mock data for local testing
    return [
        {
            "id": 1001,
            "name": "INV/2026/03/001",
            "partner_id": [501, "Acme Corp PH"],
            "l10n_ph_withholding_tax_amount": 12500.0,
            "payment_date": "2026-03-05"
        },
        {
            "id": 1002,
            "name": "INV/2026/03/045",
            "partner_id": [502, "Global Tech Systems"],
            "l10n_ph_withholding_tax_amount": 450.0,
            "payment_date": "2026-04-01"
        }
    ]

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(detect_missing_2307s())
    print(json.dumps(result, indent=2))
