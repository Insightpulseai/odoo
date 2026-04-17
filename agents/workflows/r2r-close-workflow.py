# agents/workflows/r2r-close-workflow.py
"""
R2R Period Close Workflow (Reasoning Plane)
===========================================
Orchestrates the multi-entity financial close process.
Uses Consensus Reasoning to detect intercompany gaps.

Benchmark: Dynamics 365 Finance — Close Workflow.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List

async def r2r_close_workflow(company_ids: List[int]) -> Dict[str, Any]:
    """
    Executes the R2R Period Close Workflow across multiple entities.
    """
    logging.info(f"Orchestrating Global Close for Companies {company_ids}")

    # Step 1: Grounded Consensus Analysis
    from agents.skills.project_finance.multi_company_close_consensus import calculate_global_consensus
    consensus = await calculate_global_consensus(company_ids)
    
    # Step 2: Adaptive Card Projection (Logic only)
    # Map consensus result to the 'r2r-close-readiness-card' blueprint
    card_data = {
        "title": "Global Period Close Cockpit",
        "status": consensus["global_status"],
        "readiness_score": consensus["global_readiness"],
        "accrual_value": consensus["total_accrual_value"],
        "margin_risk": consensus.get("global_margin_variance", 0.0),
        "billing_latency": consensus.get("global_readiness", 0.0),
        "alert": "Intercompany Gaps Found" if consensus["intercompany_gaps"] else None,
        "actions": [
            {"title": "Review Multi-company Gaps", "id": "action_review_gaps"},
            {"title": "Post Accruals", "id": "action_post_accruals"}
        ]
    }

    return {
        "workflow": "r2r-close-v2",
        "result": consensus,
        "m365_projection": {
            "card_id": "r2r-close-readiness-card",
            "data": card_data
        }
    }

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(r2r_close_workflow([1, 2]))
    print(json.dumps(result, indent=2))
