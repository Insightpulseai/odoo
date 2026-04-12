{
    "name": "Finance PPM Seed Data",
    "version": "18.0.1.0.0",
    "summary": "OKR project structure, stages, and tags for Finance PPM",
    "description": """
        Seed data for Finance PPM using CE + OCA native features.

        Creates:
        - Canonical Finance PPM project
        - OKR milestones (O1-O6)
        - KR tasks with progress tracking
        - Finance-specific task stages
        - OKR/lane tags

        No custom models. Uses only CE project + OCA modules.
        See docs/architecture/PPM_DASHBOARD_DECOMPOSITION.md
    """,
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": [
        "project",
    ],
    "data": [
        "data/project_tags.xml",
        "data/project_stages.xml",
        "data/project_ppm.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
