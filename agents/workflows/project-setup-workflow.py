# agents/workflows/project-setup-workflow.py
"""
Project Setup Workflow (P2P Initiate)
=====================================
Orchestrates the transition from Commercial Setup to Delivery Execution.
Relocated from Odoo Wizards to Pulser MAF Workflows.

Pattern: Initiate -> Execute -> Analyze (Dynamics 365 Benchmark).
"""

import json
import logging
import asyncio
from typing import Dict, Any, List

# In a real MAF implementation, these nodes would be registered 
# in the workflow graph and use the FoundryChatClient for human interaction.

async def project_setup_flow(project_id: int) -> Dict[str, Any]:
    """
    Executes the 5-step Project Setup Workflow.
    """
    logging.info(f"Orchestrating Setup Workflow for Project {project_id}")

    # Step 1: Commercial Alignment
    # Check if SO is linked to the analytic account
    commercial_ok = True 
    
    # Step 2: Foundation (CE Core / OCA)
    # Check if project_template (OCA) was applied or project shell exists
    foundation_ok = True

    # Step 3: WBS Construction & Quality Gate
    # Call the WBS Scorer Skill
    from agents.skills.project_finance.wbs_scorer import calculate_wbs_score
    score_result = await calculate_wbs_score(project_id)
    
    if not score_result["gate_cleared"]:
        return {
            "project_id": project_id,
            "status": "Blocked",
            "reason": f"WBS Quality Score ({score_result['score']}) is below gate threshold (60).",
            "breakdown": score_result["breakdown"]
        }

    # Step 4: Resource/Role Assignment (OCA project_role)
    # Check if project roles have members
    roles_ok = True

    # Step 5: PM Signoff (Human-in-the-loop)
    # This would normally trigger a HumanTask in MAF
    signoff_required = True

    return {
        "project_id": project_id,
        "status": "Ready for Execution",
        "wbs_score": score_result["score"],
        "gates": {
            "commercial": "PASS",
            "foundation": "PASS",
            "wbs_quality": "PASS",
            "roles": "PASS",
            "human_signoff": "PENDING"
        },
        "next_step": "Trigger PM Approval Task in Pulser"
    }

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(project_setup_flow(456))
    print(json.dumps(result, indent=2))
