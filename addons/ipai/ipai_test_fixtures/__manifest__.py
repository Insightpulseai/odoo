# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
{
    "name": "IPAI Test Fixtures",
    "version": "18.0.1.0.0",
    "category": "Hidden/Tools",
    "summary": "Shared test fixtures and factory methods for IPAI modules",
    "description": """
        Provides reusable test fixtures and factory methods for IPAI module testing.

        Features:
        - Factory methods for common models (users, employees, projects, tasks)
        - Finance-specific fixtures (BIR schedules, logframes)
        - Test data generators with sensible defaults
        - Utilities for test data cleanup
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": [
        "base",
        "hr",
        "project",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
