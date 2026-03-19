# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestIpaiWorkspaceCore(TransactionCase):
    """Tests for the ipai_workspace_core module.

    Covers:
    - Workspace creation with owner and visibility defaults
    - Member add/remove actions
    - Nested page creation (parent/child hierarchy)
    - Self-parent SQL constraint enforcement
    - Visibility field defaults
    - Page content_json storage
    - Explicit membership model with role and uniqueness
    - Page last_modified_by auto-tracking
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_demo = cls.env["res.users"].create({
            "name": "Demo WS User",
            "login": "demo_ws_user@test.ipai",
        })
        cls.user_editor = cls.env["res.users"].create({
            "name": "Editor WS User",
            "login": "editor_ws_user@test.ipai",
        })

    def _create_workspace(self, **kwargs):
        """Helper to create a workspace with sensible defaults."""
        vals = {
            "name": "Test Workspace",
            "code": "TEST",
            "owner_id": self.user_admin.id,
        }
        vals.update(kwargs)
        return self.env["ipai.workspace"].create(vals)

    # ------------------------------------------------------------------
    # Workspace creation and defaults
    # ------------------------------------------------------------------

    def test_workspace_creation_with_owner(self):
        """Workspace is created with explicit owner and correct defaults."""
        ws = self._create_workspace()
        self.assertEqual(ws.name, "Test Workspace")
        self.assertEqual(ws.owner_id, self.user_admin)
        self.assertTrue(ws.active)
        self.assertEqual(ws.visibility, "team")
        self.assertEqual(ws.color, 0)

    def test_workspace_default_owner_is_current_user(self):
        """When no owner is specified, defaults to self.env.user."""
        ws = self.env["ipai.workspace"].create({
            "name": "Auto Owner WS",
            "code": "AUTO",
        })
        self.assertEqual(ws.owner_id, self.env.user)

    def test_workspace_visibility_values(self):
        """All three visibility options are valid."""
        for vis in ("private", "team", "public"):
            ws = self._create_workspace(
                name=f"WS {vis}",
                code=f"VIS_{vis.upper()}",
                visibility=vis,
            )
            self.assertEqual(ws.visibility, vis)

    # ------------------------------------------------------------------
    # Member management
    # ------------------------------------------------------------------

    def test_action_add_member(self):
        """action_add_member adds a user to member_ids."""
        ws = self._create_workspace()
        self.assertNotIn(self.user_demo, ws.member_ids)
        ws.action_add_member(self.user_demo.id)
        self.assertIn(self.user_demo, ws.member_ids)

    def test_action_add_member_idempotent(self):
        """Adding the same member twice does not create duplicates."""
        ws = self._create_workspace()
        ws.action_add_member(self.user_demo.id)
        ws.action_add_member(self.user_demo.id)
        self.assertEqual(
            len(ws.member_ids.filtered(lambda u: u == self.user_demo)),
            1,
        )

    def test_action_remove_member(self):
        """action_remove_member removes a user from member_ids."""
        ws = self._create_workspace(member_ids=[(4, self.user_demo.id)])
        self.assertIn(self.user_demo, ws.member_ids)
        ws.action_remove_member(self.user_demo.id)
        self.assertNotIn(self.user_demo, ws.member_ids)

    # ------------------------------------------------------------------
    # Workspace pages: creation and nesting
    # ------------------------------------------------------------------

    def test_create_page(self):
        """A basic page is created under a workspace."""
        ws = self._create_workspace()
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Getting Started",
        })
        self.assertEqual(page.title, "Getting Started")
        self.assertEqual(page.workspace_id, ws)
        self.assertEqual(page.content_json, "{}")
        self.assertFalse(page.is_template)
        self.assertIn(page, ws.page_ids)

    def test_nested_pages(self):
        """Pages support parent/child hierarchy."""
        ws = self._create_workspace()
        parent_page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Parent Page",
        })
        child_page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Child Page",
            "parent_id": parent_page.id,
        })
        self.assertEqual(child_page.parent_id, parent_page)
        self.assertIn(child_page, parent_page.child_ids)

    def test_self_parent_constraint(self):
        """A page cannot reference itself as parent (SQL constraint)."""
        ws = self._create_workspace()
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Self Ref Page",
        })
        with self.assertRaises(Exception):
            # Depending on Odoo version, this raises IntegrityError
            # wrapped in ValidationError or a raw psycopg2 error.
            page.write({"parent_id": page.id})
            # Force flush to trigger SQL constraint
            page.flush_recordset()

    def test_page_default_title(self):
        """Page title defaults to 'Untitled'."""
        ws = self._create_workspace()
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
        })
        self.assertEqual(page.title, "Untitled")

    # ------------------------------------------------------------------
    # Page content and tracking
    # ------------------------------------------------------------------

    def test_page_content_json_storage(self):
        """content_json stores arbitrary JSON text."""
        ws = self._create_workspace()
        content = '{"blocks": [{"type": "heading", "text": "Hello"}]}'
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "JSON Page",
            "content_json": content,
        })
        self.assertEqual(page.content_json, content)

    def test_page_last_modified_by_auto_tracked(self):
        """Writing to a page auto-sets last_modified_by."""
        ws = self._create_workspace()
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Tracked Page",
        })
        page.write({"title": "Updated Title"})
        self.assertEqual(page.last_modified_by, self.env.user)

    def test_page_template_flag(self):
        """Pages can be marked as templates."""
        ws = self._create_workspace()
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Template Page",
            "is_template": True,
        })
        self.assertTrue(page.is_template)

    # ------------------------------------------------------------------
    # Explicit membership model
    # ------------------------------------------------------------------

    def test_create_workspace_member(self):
        """Explicit membership record with role is created."""
        ws = self._create_workspace()
        member = self.env["ipai.workspace.member"].create({
            "workspace_id": ws.id,
            "user_id": self.user_demo.id,
            "role": "editor",
        })
        self.assertEqual(member.role, "editor")
        self.assertEqual(member.workspace_id, ws)
        self.assertIn(member, ws.workspace_member_ids)

    def test_member_default_role_is_editor(self):
        """Default role for a new membership is 'editor'."""
        ws = self._create_workspace()
        member = self.env["ipai.workspace.member"].create({
            "workspace_id": ws.id,
            "user_id": self.user_demo.id,
        })
        self.assertEqual(member.role, "editor")

    def test_member_role_viewer(self):
        """Viewer role is assignable."""
        ws = self._create_workspace()
        member = self.env["ipai.workspace.member"].create({
            "workspace_id": ws.id,
            "user_id": self.user_demo.id,
            "role": "viewer",
        })
        self.assertEqual(member.role, "viewer")

    def test_member_role_admin(self):
        """Admin role is assignable."""
        ws = self._create_workspace()
        member = self.env["ipai.workspace.member"].create({
            "workspace_id": ws.id,
            "user_id": self.user_demo.id,
            "role": "admin",
        })
        self.assertEqual(member.role, "admin")

    def test_duplicate_membership_raises(self):
        """Same user cannot have two memberships in the same workspace."""
        ws = self._create_workspace()
        self.env["ipai.workspace.member"].create({
            "workspace_id": ws.id,
            "user_id": self.user_demo.id,
            "role": "editor",
        })
        with self.assertRaises(Exception):
            self.env["ipai.workspace.member"].create({
                "workspace_id": ws.id,
                "user_id": self.user_demo.id,
                "role": "admin",
            })
            self.env["ipai.workspace.member"].flush_recordset()

    # ------------------------------------------------------------------
    # Cascade delete
    # ------------------------------------------------------------------

    def test_workspace_delete_cascades_pages(self):
        """Deleting a workspace cascades to its pages."""
        ws = self._create_workspace(code="CASCADE")
        page = self.env["ipai.workspace.page"].create({
            "workspace_id": ws.id,
            "title": "Will be deleted",
        })
        page_id = page.id
        ws.unlink()
        self.assertFalse(
            self.env["ipai.workspace.page"].search([("id", "=", page_id)])
        )

    def test_workspace_delete_cascades_members(self):
        """Deleting a workspace cascades to its membership records."""
        ws = self._create_workspace(code="CASCADE_M")
        member = self.env["ipai.workspace.member"].create({
            "workspace_id": ws.id,
            "user_id": self.user_demo.id,
        })
        member_id = member.id
        ws.unlink()
        self.assertFalse(
            self.env["ipai.workspace.member"].search([("id", "=", member_id)])
        )
