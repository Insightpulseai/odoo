{
    "name": "IPAI PPM + OKR (CE-only)",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Project",
    "summary": "Enterprise-grade Portfolio/Program/Project Management with OKR tracking",
    "description": """
IPAI PPM + OKR System
=====================

Complete CE-only implementation of:
- Portfolio and Program governance
- Project metadata and strategic alignment
- Workstreams and Epics
- Risk, Issue, and Change Request management
- Budget tracking and resource allocation
- OKR (Objectives and Key Results) with check-ins
- Initiative tracking linked to projects/tasks

Features:
- RAG status tracking (Red/Amber/Green)
- Computed risk scores
- OKR progress calculation
- Resource allocation planning
- Budget forecasting
  """,
    "depends": [
        "project",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
