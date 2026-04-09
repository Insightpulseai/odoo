# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTimelineFix(TransactionCase):
    """Verify that timeline view type is stripped from project actions."""

    # XML IDs of project actions that project_timeline modifies
    ACTION_XMLIDS = [
        "project.open_view_project_all",
        "project.open_view_project_all_group_stage",
        "project.action_view_task",
        "project.action_view_all_task",
        "project.project_task_action_from_partner",
        "project.act_project_project_2_project_task_all",
        "project.action_view_task_overpassed_draft",
        "project.dblc_proj",
        "project.action_project_task_user_tree",
    ]

    def test_no_timeline_in_project_actions(self):
        """No project action should contain timeline in view_mode."""
        for xmlid in self.ACTION_XMLIDS:
            action = self.env.ref(xmlid, raise_if_not_found=False)
            if not action:
                continue
            self.assertNotIn(
                "timeline",
                action.view_mode,
                "Action %s still contains timeline in view_mode: %s"
                % (xmlid, action.view_mode),
            )

    def test_project_actions_have_valid_view_modes(self):
        """All project actions should only contain CE-supported view types."""
        ce_valid = {
            "list", "form", "kanban", "calendar",
            "pivot", "graph", "activity",
        }
        for xmlid in self.ACTION_XMLIDS:
            action = self.env.ref(xmlid, raise_if_not_found=False)
            if not action:
                continue
            modes = set(action.view_mode.split(","))
            invalid = modes - ce_valid
            self.assertFalse(
                invalid,
                "Action %s has unsupported view types: %s"
                % (xmlid, invalid),
            )
