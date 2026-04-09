{
    "name": "IPAI Timesheet Leaderboard",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Timesheets",
    "summary": "Billable hours leaderboard with pivot and graph views",
    "author": "InsightPulse AI, Odoo Community Association (OCA)",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "hr_timesheet",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_timesheet_leaderboard_views.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Beta",
}
