# agents/skills/project-finance/project_finance_signals.py
"""
P2P to R2R Signal Ingestion Skill
=================================
Ingests project finance signals from Odoo (Emission) and translates
them into reasoning context for the Pulser R2R Close Workflow.

Benchmark: Patterned after Dynamics 365 Finance close readiness logic.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List

async def analyze_project_finance_signals(project_id: int) -> Dict[str, Any]:
    """
    Retrieves and analyzes P2P signals for a specific project.
    Identifies accrual candidates and billing health for the R2R cockpit.
    """
    logging.info(f"Analyzing P2P signals for project {project_id}")

    # Step 1: Retrieval via Odoo MCP
    # Call action_get_p2p_finance_signals on the project.project model
    signals = await _get_signals_from_odoo(project_id)

    # Step 2: Reasoning Logic
    # Identify high-risk gaps for Record-to-Report
    analysis = _perform_p2p_r2r_reasoning(signals)

    return {
        "project_id": project_id,
        "project_name": signals.get("name"),
        "r2r_status": "Blocker Detected" if analysis["blockers"] else "Clear for Close",
        "accrual_candidates": signals["signals"]["accrual_candidates"],
        "total_accrual_value": signals["signals"]["total_accrual_amount"],
        "billing_readiness": signals["signals"]["billing_readiness"],
        "analysis": analysis,
        "benchmark": "p2p-r2r-signal-v1"
    }

async def _get_signals_from_odoo(project_id: int) -> Dict[str, Any]:
    """Simulates odoo_execute via MCP: project.project -> action_get_p2p_finance_signals."""
    # Logic: Pulser calls Odoo to emit the contract payload
    return {
        "project_id": project_id,
        "name": "Project Alpha",
        "signals": {
            "accrual_candidates": [
                {"id": 101, "amount": 1500.0, "ref": "Unbilled Consultant Time"}
            ],
            "total_accrual_amount": 1500.0,
            "billing_readiness": 45.0, # 45% ready
            "margin_variance_signal": True, # Anomaly detected
            "target_margin": 20.0,
            "actual_margin": 5.0
        }
    }

def _perform_p2p_r2r_reasoning(signals: Dict[str, Any]) -> Dict[str, Any]:
    """Translates transactional signals into R2R governance risks."""
    blockers = []
    recommendations = []
    
    # Logic 1: Unbilled Accruals
    if signals["signals"]["total_accrual_amount"] > 1000:
        blockers.append("Material Unbilled Accruals")
        recommendations.append(f"Post AP accrual for {signals['signals']['total_accrual_amount']} or trigger billing.")

    # Logic 2: Billing Readiness Gate (Standard: 60% for close readiness)
    if signals["signals"]["billing_readiness"] < 60:
        blockers.append("Low Billing Readiness")
        recommendations.append("Ensure project milestones are signed off/invoiced before period close.")

    # Logic 3: Margin Anomaly
    if signals["signals"]["margin_variance_signal"]:
        blockers.append("Margin Variance Anomaly")
        recommendations.append("Audit project cost breakdown for margin leakage.")

    return {
        "blockers": blockers,
        "recommendations": recommendations,
        "risk_level": "High" if len(blockers) > 1 else "Medium"
    }

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(analyze_project_finance_signals(777))
    print(json.dumps(result, indent=2))
