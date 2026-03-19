# -*- coding: utf-8 -*-
"""
Security Tests for IDP Module.

Tests access rights and record rules including:
- Group-based access control
- Multi-company record isolation
- Reviewer permissions
"""
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestIdpSecurity(TransactionCase):
    """Test cases for IDP security (groups, access rights, record rules)."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()

        # Get groups
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_idp_user = cls.env.ref("ipai_idp.group_idp_user")
        cls.group_idp_reviewer = cls.env.ref("ipai_idp.group_idp_reviewer")
        cls.group_idp_manager = cls.env.ref("ipai_idp.group_idp_manager")
        cls.group_idp_admin = cls.env.ref("ipai_idp.group_idp_admin")

        # Create test companies
        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})

        # Create test users with different roles
        cls.user_basic = cls.env["res.users"].create(
            {
                "name": "Basic User",
                "login": "idp_basic",
                "groups_id": [(6, 0, [cls.group_user.id, cls.group_idp_user.id])],
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, [cls.company_a.id])],
            }
        )

        cls.user_reviewer = cls.env["res.users"].create(
            {
                "name": "Reviewer User",
                "login": "idp_reviewer",
                "groups_id": [(6, 0, [cls.group_user.id, cls.group_idp_reviewer.id])],
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, [cls.company_a.id])],
            }
        )

        cls.user_manager = cls.env["res.users"].create(
            {
                "name": "Manager User",
                "login": "idp_manager",
                "groups_id": [(6, 0, [cls.group_user.id, cls.group_idp_manager.id])],
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, [cls.company_a.id])],
            }
        )

        cls.user_admin = cls.env["res.users"].create(
            {
                "name": "Admin User",
                "login": "idp_admin",
                "groups_id": [(6, 0, [cls.group_user.id, cls.group_idp_admin.id])],
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, [cls.company_a.id, cls.company_b.id])],
            }
        )

        cls.user_company_b = cls.env["res.users"].create(
            {
                "name": "Company B User",
                "login": "idp_company_b",
                "groups_id": [(6, 0, [cls.group_user.id, cls.group_idp_user.id])],
                "company_id": cls.company_b.id,
                "company_ids": [(6, 0, [cls.company_b.id])],
            }
        )

    def setUp(self):
        """Set up per-test fixtures."""
        super().setUp()
        # Create a test document in Company A
        self.doc_company_a = self.env["idp.document"].create(
            {
                "name": "Test Doc A",
                "company_id": self.company_a.id,
                "source": "api",
            }
        )
        # Create a test document in Company B
        self.doc_company_b = self.env["idp.document"].create(
            {
                "name": "Test Doc B",
                "company_id": self.company_b.id,
                "source": "api",
            }
        )

    # ==================== Company Isolation Tests ====================

    def test_user_can_see_own_company_docs(self):
        """Test that users can see documents in their company."""
        docs = (
            self.env["idp.document"]
            .with_user(self.user_basic)
            .search([("id", "=", self.doc_company_a.id)])
        )
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs.id, self.doc_company_a.id)

    def test_user_cannot_see_other_company_docs(self):
        """Test that users cannot see documents in other companies."""
        docs = (
            self.env["idp.document"]
            .with_user(self.user_basic)
            .search([("id", "=", self.doc_company_b.id)])
        )
        self.assertEqual(len(docs), 0)

    def test_multi_company_user_can_see_all(self):
        """Test that multi-company users can see docs from all their companies."""
        docs = self.env["idp.document"].with_user(self.user_admin).search([])
        doc_ids = docs.ids
        self.assertIn(self.doc_company_a.id, doc_ids)
        self.assertIn(self.doc_company_b.id, doc_ids)

    def test_company_b_user_only_sees_company_b(self):
        """Test Company B user isolation."""
        docs = self.env["idp.document"].with_user(self.user_company_b).search([])
        doc_ids = docs.ids
        self.assertNotIn(self.doc_company_a.id, doc_ids)
        self.assertIn(self.doc_company_b.id, doc_ids)

    # ==================== Access Rights Tests ====================

    def test_basic_user_cannot_create_document(self):
        """Test that basic IDP users cannot create documents."""
        with self.assertRaises(AccessError):
            self.env["idp.document"].with_user(self.user_basic).create(
                {
                    "name": "New Doc",
                    "company_id": self.company_a.id,
                    "source": "api",
                }
            )

    def test_basic_user_cannot_write_document(self):
        """Test that basic IDP users cannot modify documents."""
        with self.assertRaises(AccessError):
            self.doc_company_a.with_user(self.user_basic).write({"name": "Modified"})

    def test_manager_can_create_document(self):
        """Test that managers can create documents."""
        doc = (
            self.env["idp.document"]
            .with_user(self.user_manager)
            .create(
                {
                    "name": "Manager Doc",
                    "company_id": self.company_a.id,
                    "source": "api",
                }
            )
        )
        self.assertTrue(doc.exists())

    def test_manager_can_write_document(self):
        """Test that managers can modify documents."""
        self.doc_company_a.with_user(self.user_manager).write(
            {"name": "Manager Modified"}
        )
        self.assertEqual(self.doc_company_a.name, "Manager Modified")

    def test_manager_cannot_delete_document(self):
        """Test that managers cannot delete documents."""
        with self.assertRaises(AccessError):
            self.doc_company_a.with_user(self.user_manager).unlink()

    def test_admin_can_delete_document(self):
        """Test that admins can delete documents."""
        doc_id = self.doc_company_a.id
        self.doc_company_a.with_user(self.user_admin).unlink()
        self.assertFalse(self.env["idp.document"].browse(doc_id).exists())

    # ==================== Model Version Access Tests ====================

    def test_basic_user_can_read_model_version(self):
        """Test that basic users can read model versions."""
        version = self.env["idp.model.version"].create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
            }
        )
        # Should be readable
        version_read = (
            self.env["idp.model.version"]
            .with_user(self.user_basic)
            .search([("id", "=", version.id)])
        )
        self.assertEqual(len(version_read), 1)

    def test_basic_user_cannot_write_model_version(self):
        """Test that basic users cannot modify model versions."""
        version = self.env["idp.model.version"].create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
            }
        )
        with self.assertRaises(AccessError):
            version.with_user(self.user_basic).write({"name": "Modified"})

    def test_admin_can_write_model_version(self):
        """Test that admins can modify model versions."""
        version = self.env["idp.model.version"].create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
            }
        )
        version.with_user(self.user_admin).write({"name": "Admin Modified"})
        self.assertEqual(version.name, "Admin Modified")

    # ==================== Review Access Tests ====================

    def test_reviewer_can_create_review(self):
        """Test that reviewers can create reviews."""
        review = (
            self.env["idp.review"]
            .with_user(self.user_reviewer)
            .create(
                {
                    "document_id": self.doc_company_a.id,
                    "corrected_json": "{}",
                }
            )
        )
        self.assertTrue(review.exists())

    def test_reviewer_can_edit_pending_review(self):
        """Test that reviewers can edit pending reviews."""
        review = self.env["idp.review"].create(
            {
                "document_id": self.doc_company_a.id,
                "corrected_json": "{}",
                "status": "pending",
            }
        )
        review.with_user(self.user_reviewer).write({"corrected_json": '{"test": 1}'})
        self.assertEqual(review.corrected_json, '{"test": 1}')

    def test_basic_user_cannot_create_review(self):
        """Test that basic users cannot create reviews."""
        with self.assertRaises(AccessError):
            self.env["idp.review"].with_user(self.user_basic).create(
                {
                    "document_id": self.doc_company_a.id,
                    "corrected_json": "{}",
                }
            )

    # ==================== Validation Rule Access Tests ====================

    def test_basic_user_can_read_validation_rules(self):
        """Test that basic users can read validation rules."""
        rule = self.env["idp.validation.rule"].create(
            {
                "name": "Test Rule",
                "rule_type": "required",
                "field_name": "vendor_name",
            }
        )
        rule_read = (
            self.env["idp.validation.rule"]
            .with_user(self.user_basic)
            .search([("id", "=", rule.id)])
        )
        self.assertEqual(len(rule_read), 1)

    def test_basic_user_cannot_create_validation_rule(self):
        """Test that basic users cannot create validation rules."""
        with self.assertRaises(AccessError):
            self.env["idp.validation.rule"].with_user(self.user_basic).create(
                {
                    "name": "New Rule",
                    "rule_type": "required",
                    "field_name": "total",
                }
            )

    def test_admin_can_create_validation_rule(self):
        """Test that admins can create validation rules."""
        rule = (
            self.env["idp.validation.rule"]
            .with_user(self.user_admin)
            .create(
                {
                    "name": "Admin Rule",
                    "rule_type": "required",
                    "field_name": "total",
                }
            )
        )
        self.assertTrue(rule.exists())


class TestIdpGroupHierarchy(TransactionCase):
    """Test IDP group inheritance hierarchy."""

    def test_reviewer_implies_user(self):
        """Test that reviewer group implies user group."""
        reviewer_group = self.env.ref("ipai_idp.group_idp_reviewer")
        user_group = self.env.ref("ipai_idp.group_idp_user")
        self.assertIn(user_group, reviewer_group.implied_ids)

    def test_manager_implies_reviewer(self):
        """Test that manager group implies reviewer group."""
        manager_group = self.env.ref("ipai_idp.group_idp_manager")
        reviewer_group = self.env.ref("ipai_idp.group_idp_reviewer")
        self.assertIn(reviewer_group, manager_group.implied_ids)

    def test_admin_implies_manager(self):
        """Test that admin group implies manager group."""
        admin_group = self.env.ref("ipai_idp.group_idp_admin")
        manager_group = self.env.ref("ipai_idp.group_idp_manager")
        self.assertIn(manager_group, admin_group.implied_ids)
