# agents/skills/project-finance/wbs_scorer.py
"""
WBS Quality Scorer (Reasoning Plane)
====================================
Performs metric-driven quality scoring (0-100) on Odoo Project WBS.
Relocated from Transaction layer to Reasoning layer.

Gating Rule: Score >= 60 required to clear 'Initiate' phase.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List

async def calculate_wbs_score(project_id: int) -> Dict[str, Any]:
    """
    Calculates the WBS Quality Score by querying Odoo CE/OCA primitives.
    
    1. Retrieve project tasks via Odoo MCP.
    2. Apply 5-gate scoring logic (Owners, Estimates, Deadlines, Milestones, Depth).
    """
    logging.info(f"Calculating WBS score for project {project_id}")

    # Step 1: Data Retrieval
    # Simulates odoo_search_read via MCP for project.task
    tasks = await _get_project_tasks_from_odoo(project_id)
    
    if not tasks:
        return {"project_id": project_id, "score": 0, "status": "No Tasks Found"}

    score = 0
    breakdown = {}

    # Helper to get ID from many2one (which can be [id, name] or just id)
    def _get_id(val):
        if isinstance(val, list) and val:
            return val[0]
        return val

    # Gate 1: Owners at Level 1 (+20)
    level_1_tasks = [t for t in tasks if not t.get("parent_id")]
    if level_1_tasks and all(t.get("user_ids") for t in level_1_tasks):
        score += 20
        breakdown["owners"] = "PASS"
    else:
        breakdown["owners"] = "FAIL (Missing Owners on Level 1)"

    # Gate 2: Task Estimates (+20)
    # Leaf tasks = tasks not appearing as parent_id in any other task
    parent_ids = {_get_id(t["parent_id"]) for t in tasks if t.get("parent_id")}
    leaf_tasks = [t for t in tasks if t["id"] not in parent_ids]
    if leaf_tasks and all(t.get("planned_hours", 0) > 0 for t in leaf_tasks):
        score += 20
        breakdown["estimates"] = "PASS"
    else:
        breakdown["estimates"] = "FAIL (Missing Estimates on Leaf Tasks)"

    # Gate 3: Task Deadlines (+20)
    if leaf_tasks and all(t.get("date_deadline") for t in leaf_tasks):
        score += 20
        breakdown["deadlines"] = "PASS"
    else:
        breakdown["deadlines"] = "FAIL (Missing Deadlines on Leaf Tasks)"

    # Gate 4: Milestones (+20)
    # Check for 'milestone' in Name or Tags
    has_milestones = any(
        "milestone" in t["name"].lower() or 
        any("milestone" in tag.lower() for tag in t.get("tag_names", []))
        for t in tasks
    )
    if has_milestones:
        score += 20
        breakdown["milestones"] = "PASS"
    else:
        breakdown["milestones"] = "FAIL (No Milestones Found)"

    # Gate 5: Structure Depth (+20)
    if any(t.get("parent_id") for t in tasks):
        score += 20
        breakdown["depth"] = "PASS"
    else:
        breakdown["depth"] = "FAIL (Flat structure detected)"

    return {
        "project_id": project_id,
        "score": score,
        "gate_cleared": score >= 60,
        "breakdown": breakdown,
        "benchmark": "p2p-wbs-v1-relocated"
    }

async def _get_project_tasks_from_odoo(project_id: int) -> List[Dict[str, Any]]:
    """Simulates odoo_search_read [('project_id', '=', project_id)] via MCP."""
    # Mock data matching real Odoo many2one format [id, name]
    return [
        {"id": 1, "name": "Work Package 1", "parent_id": False, "user_ids": [1], "planned_hours": 0},
        {"id": 2, "name": "Milestone: Delivery", "parent_id": [1, "Work Package 1"], "user_ids": [1], "planned_hours": 10, "date_deadline": "2026-05-01", "tag_names": ["milestone"]},
        {"id": 3, "name": "Subtask A", "parent_id": [1, "Work Package 1"], "user_ids": [1], "planned_hours": 5, "date_deadline": "2026-05-01"}
    ]

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(calculate_wbs_score(123))
    print(json.dumps(result, indent=2))
