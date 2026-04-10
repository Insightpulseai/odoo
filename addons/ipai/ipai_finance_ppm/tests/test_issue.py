"""Tests for ppm.issue — project issue register."""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ppm", "post_install", "-at_install")
class TestIssue(TransactionCase):
    """Test PPM issue model: lifecycle transitions, date fields, project linkage."""

    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create({
            "name": "Test PPM Issue Project",
        })
        self.Issue = self.env["ppm.issue"]

    def _make_issue(self, **kwargs):
        defaults = {
            "name": "Test Issue",
            "project_id": self.project.id,
            "priority": "1",
        }
        defaults.update(kwargs)
        return self.Issue.create(defaults)

    def test_issue_creation(self):
        """Issue record can be created with required fields."""
        issue = self._make_issue()
        self.assertTrue(issue.id)
        self.assertEqual(issue.name, "Test Issue")

    def test_issue_project_link(self):
        """Issue is linked to its project."""
        issue = self._make_issue()
        self.assertEqual(issue.project_id.id, self.project.id)

    def test_issue_default_state_is_open(self):
        """Default state is open."""
        issue = self._make_issue()
        self.assertEqual(issue.state, "open")

    def test_issue_lifecycle_open_to_investigating(self):
        """Issue can move from open to investigating."""
        issue = self._make_issue()
        issue.write({"state": "investigating"})
        self.assertEqual(issue.state, "investigating")

    def test_issue_lifecycle_escalated(self):
        """Issue can be escalated."""
        issue = self._make_issue(state="investigating")
        issue.write({"state": "escalated"})
        self.assertEqual(issue.state, "escalated")

    def test_issue_lifecycle_resolved(self):
        """Issue can be resolved with resolution text."""
        issue = self._make_issue()
        issue.write({
            "state": "resolved",
            "resolution": "Root cause fixed in sprint 3.",
            "resolved_date": "2026-02-15",
        })
        self.assertEqual(issue.state, "resolved")
        self.assertEqual(issue.resolution, "Root cause fixed in sprint 3.")
        self.assertEqual(str(issue.resolved_date), "2026-02-15")

    def test_issue_lifecycle_closed(self):
        """Issue can be closed after resolution."""
        issue = self._make_issue(state="resolved")
        issue.write({"state": "closed"})
        self.assertEqual(issue.state, "closed")

    def test_issue_raised_date_defaults_to_today(self):
        """raised_date defaults to today."""
        from odoo import fields as odoo_fields
        issue = self._make_issue()
        today = odoo_fields.Date.today()
        self.assertEqual(issue.raised_date, today)

    def test_issue_target_date_stored(self):
        """Target resolution date can be set."""
        issue = self._make_issue(target_date="2026-03-31")
        self.assertEqual(str(issue.target_date), "2026-03-31")

    def test_issue_priority_options(self):
        """All priority levels are accepted."""
        for p in ("0", "1", "2", "3"):
            issue = self._make_issue(priority=p)
            self.assertEqual(issue.priority, p)

    def test_issue_category_options(self):
        """All issue categories are accepted."""
        for cat in ("financial", "schedule", "resource", "technical", "compliance", "stakeholder"):
            issue = self._make_issue(category=cat)
            self.assertEqual(issue.category, cat)

    def test_issue_owner_assignment(self):
        """Issue owner can be assigned."""
        user = self.env.user
        issue = self._make_issue(owner_id=user.id)
        self.assertEqual(issue.owner_id, user)

    def test_issue_description_stored(self):
        """Issue description text is stored."""
        issue = self._make_issue(description="Critical vendor dependency failure.")
        self.assertEqual(issue.description, "Critical vendor dependency failure.")

    def test_issue_company_inherited_from_project(self):
        """company_id is relayed from the linked project."""
        issue = self._make_issue()
        self.assertEqual(issue.company_id, self.project.company_id)

    def test_issue_ordering_by_priority_descending(self):
        """Issues are ordered by priority descending."""
        self._make_issue(name="Low", priority="0")
        self._make_issue(name="Critical", priority="3")
        issues = self.Issue.search([("project_id", "=", self.project.id)])
        priorities = [int(i.priority) for i in issues]
        self.assertEqual(priorities, sorted(priorities, reverse=True))
