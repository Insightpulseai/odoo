# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "IPAI Company Scope — OMC",
    "version": "19.0.1.0.0",
    "summary": (
        "Deterministic server-side enforcement: users whose login ends with "
        "@omc.com can only ever belong to the TBWA\\SMP company. "
        "Enforced on create and write; backed by a record rule so non-sudo "
        "searches on res.company return only TBWA\\SMP for OMC-restricted users."
    ),
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Hidden",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/company_marker.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
