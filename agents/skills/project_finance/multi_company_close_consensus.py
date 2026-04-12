# agents/skills/project_finance/multi_company_close_consensus.py
"""
Multi-company Close Consensus (Reasoning Plane)
==============================================
Aggregates financial signals across all Odoo legal entities and detects
intercompany gaps within the reasoning plane.

Consolidation without parallel ledgers.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List

async def calculate_global_consensus(company_ids: List[int]) -> Dict[str, Any]:
    """
    Orchestrates the multi-company consensus check.
    
    1. Query project signals for each company via Odoo MCP.
    2. Summatize total accrual candidates and billing readiness.
    3. Detect intercompany mismatches.
    """
    logging.info(f"Orchestrating Consensus for companies: {company_ids}")

    results_by_company = {}
    total_accruals = 0.0
    global_billing_readiness = 0.0
    intercompany_gaps = []

    # Step 1 & 2: Aggregation
    for cid in company_ids:
        # Simulate cross-company query via MCP [('company_id', '=', cid)]
        company_signals = await _get_company_signals_from_odoo(cid)
        results_by_company[cid] = company_signals
        total_accruals += company_signals.get("total_accruals", 0.0)
        global_billing_readiness += company_signals.get("billing_readiness", 0.0)

    # Calculate average global readiness
    if company_ids:
        global_billing_readiness /= len(company_ids)

    # Step 3: Intercompany Gap Detection (Heuristic)
    # Mapping Company A 'Intercompany Cost' to Company B 'Intercompany Income'
    intercompany_gaps = _detect_intercompany_gaps(results_by_company)

    status = "READY" if not intercompany_gaps and global_billing_readiness > 80 else "BLOCKER DETECTED"
    risk_level = "HIGH" if intercompany_gaps else "LOW"

    return {
        "global_status": status,
        "risk_level": risk_level,
        "global_readiness": round(global_billing_readiness, 2),
        "total_accrual_value": round(total_accruals, 2),
        "entity_breakdown": results_by_company,
        "intercompany_gaps": intercompany_gaps,
        "benchmark": "r2r-multi-company-v1"
    }

def _detect_intercompany_gaps(data: Dict[int, Any]) -> List[Dict[str, Any]]:
    """
    Heuristic: Compares 'Intercompany' signals between entities.
    Example: If Company 1 has $1000 Intercompany Cost, Company 2 should have matching Intercompany Revenue.
    """
    gaps = []
    # Simplified mock matching logic
    # In practice, this would query account.move.line where intercompany_partner_id is set.
    for cid, signals in data.items():
        if signals.get("untracked_intercompany_costs", 0) > 0:
            gaps.append({
                "source_company_id": cid,
                "type": "Unmatched Intercompany Cost",
                "value": signals["untracked_intercompany_costs"],
                "note": f"Company {cid} has delivery costs without matched income in Parent."
            })
    return gaps

async def _get_company_signals_from_odoo(company_id: int) -> Dict[str, Any]:
    """Simulates multi-company Odoo MCP signal ingestion."""
    # Mock data for local testing
    if company_id == 1: # Subsidiary A
        return {
            "name": "SalmonTree Sub-A",
            "total_accruals": 15000.0,
            "billing_readiness": 75.0,
            "untracked_intercompany_costs": 5000.0
        }
    else: # Parent
        return {
            "name": "InsightPulseAI Parent",
            "total_accruals": 45000.0,
            "billing_readiness": 90.0,
            "untracked_intercompany_costs": 0.0
        }

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    consensus_result = asyncio.run(calculate_global_consensus([1, 2]))
    print(json.dumps(consensus_result, indent=2))
