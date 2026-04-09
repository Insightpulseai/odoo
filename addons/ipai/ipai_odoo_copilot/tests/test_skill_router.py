# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase


class TestSkillRouter(TransactionCase):
    """Deterministic classification tests for the Pulser skill router.

    Tests cover:
      - priority collisions (higher-priority skill wins)
      - finance-record context boost
      - low-confidence fallback to 'general'
      - read vs write lane routing
      - tax/docs/ops disambiguation
      - all 12 skills have at least one matching input
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.router = cls.env["ipai.copilot.skill.router"]

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _classify(self, message, context_envelope=None):
        return self.router.classify_intent(message, context_envelope)

    # ------------------------------------------------------------------
    # Finance skills
    # ------------------------------------------------------------------

    def test_reconciliation_detected(self):
        result = self._classify("Help me reconcile this bank statement")
        self.assertEqual(result["skill_id"], "reconciliation_assist")
        self.assertEqual(result["confidence"], "high")

    def test_collections_detected(self):
        result = self._classify("Show me overdue invoices for follow-up")
        self.assertEqual(result["skill_id"], "collections_assist")
        self.assertEqual(result["confidence"], "high")

    def test_variance_analysis_detected(self):
        result = self._classify("What is the budget vs actual variance?")
        self.assertEqual(result["skill_id"], "variance_analysis")
        self.assertEqual(result["confidence"], "high")

    def test_finance_qa_detected(self):
        result = self._classify("Show me the invoice details")
        self.assertEqual(result["skill_id"], "finance_qa")

    def test_finance_qa_tax(self):
        """Tax queries route to finance_qa, not odoo_docs."""
        result = self._classify("What is the tax rate for this invoice?")
        self.assertEqual(result["skill_id"], "finance_qa")

    # ------------------------------------------------------------------
    # Finance context boost
    # ------------------------------------------------------------------

    def test_context_boost_finance_record(self):
        """Viewing an account.move record should boost finance skills."""
        context = {"record_model": "account.move", "surface": "erp"}
        result = self._classify("Tell me about this", context)
        # Without context boost, "tell me about" could be general.
        # With context boost on account.move, finance gets +20 priority.
        self.assertTrue(result["context_boost"])

    def test_context_boost_analytics_surface(self):
        """Analytics surface should trigger context boost."""
        context = {"surface": "analytics"}
        result = self._classify("What are the monthly metrics?", context)
        self.assertTrue(result["context_boost"])

    def test_no_context_boost_generic(self):
        """No boost without finance record context."""
        context = {"record_model": "res.partner", "surface": "erp"}
        result = self._classify("Tell me about this partner", context)
        self.assertFalse(result["context_boost"])

    # ------------------------------------------------------------------
    # Odoo framework skills
    # ------------------------------------------------------------------

    def test_upgrade_advisor_detected(self):
        result = self._classify("How do I migrate this module to 19?")
        self.assertEqual(result["skill_id"], "odoo_upgrade_advisor")
        self.assertEqual(result["confidence"], "high")

    def test_module_scaffolder_detected(self):
        result = self._classify("Create a new Odoo module for HR")
        self.assertEqual(result["skill_id"], "odoo_module_scaffolder")
        self.assertEqual(result["confidence"], "high")

    def test_docs_explainer_detected(self):
        result = self._classify("How does the ORM handle computed fields?")
        self.assertEqual(result["skill_id"], "odoo_docs_explainer")

    def test_docs_explainer_what_is(self):
        result = self._classify("What is an Owl component?")
        self.assertEqual(result["skill_id"], "odoo_docs_explainer")

    # ------------------------------------------------------------------
    # Data / analytics
    # ------------------------------------------------------------------

    def test_fabric_data_query_detected(self):
        result = self._classify("Show me the monthly KPI dashboard")
        self.assertEqual(result["skill_id"], "fabric_data_query")

    def test_fabric_revenue_trend(self):
        result = self._classify("What is the revenue trend this quarter?")
        self.assertEqual(result["skill_id"], "fabric_data_query")

    # ------------------------------------------------------------------
    # Write lane
    # ------------------------------------------------------------------

    def test_propose_write_create(self):
        result = self._classify("Create a new sales order for partner ABC")
        self.assertEqual(result["skill_id"], "propose_write")

    def test_propose_write_update(self):
        result = self._classify("Update the payment terms on this invoice")
        self.assertEqual(result["skill_id"], "propose_write")

    def test_propose_write_confirm(self):
        result = self._classify("Confirm this purchase order")
        self.assertEqual(result["skill_id"], "propose_write")

    # ------------------------------------------------------------------
    # General search / read
    # ------------------------------------------------------------------

    def test_search_docs_detected(self):
        result = self._classify("Search the architecture docs for MCP")
        self.assertEqual(result["skill_id"], "search_docs")

    def test_record_reader_detected(self):
        result = self._classify("Show me the partner record details")
        self.assertEqual(result["skill_id"], "record_reader")

    # ------------------------------------------------------------------
    # Priority collision tests
    # ------------------------------------------------------------------

    def test_reconciliation_beats_finance_qa(self):
        """'reconcile bank statement' should match reconciliation (90)
        not finance_qa (80) even though 'bank' matches finance patterns."""
        result = self._classify("Reconcile the bank statement for January")
        self.assertEqual(result["skill_id"], "reconciliation_assist")

    def test_upgrade_beats_docs(self):
        """'migrate module' should match upgrade_advisor (85)
        not docs_explainer (70)."""
        result = self._classify("How to migrate this module for the upgrade?")
        self.assertEqual(result["skill_id"], "odoo_upgrade_advisor")

    def test_scaffold_beats_docs(self):
        """'scaffold new module' should match scaffolder (85)
        not docs_explainer (70)."""
        result = self._classify("Scaffold a new addon for warehouse")
        self.assertEqual(result["skill_id"], "odoo_module_scaffolder")

    def test_variance_beats_fabric(self):
        """'budget variance' should match variance_analysis (90)
        not fabric_data_query (75)."""
        result = self._classify("Show me the budget variance report")
        self.assertEqual(result["skill_id"], "variance_analysis")

    # ------------------------------------------------------------------
    # Low-confidence fallback
    # ------------------------------------------------------------------

    def test_empty_message_fallback(self):
        result = self._classify("")
        self.assertEqual(result["skill_id"], "general")
        self.assertEqual(result["confidence"], "low")

    def test_unrelated_message_fallback(self):
        result = self._classify("What is the weather today?")
        self.assertEqual(result["skill_id"], "general")
        self.assertEqual(result["confidence"], "low")

    def test_greeting_fallback(self):
        result = self._classify("Hello, good morning!")
        self.assertEqual(result["skill_id"], "general")
        self.assertEqual(result["confidence"], "low")

    # ------------------------------------------------------------------
    # Disambiguation tests
    # ------------------------------------------------------------------

    def test_tax_routes_to_finance_not_docs(self):
        """Tax is a finance domain term, not a documentation query."""
        result = self._classify("Check the fiscal position for tax")
        self.assertEqual(result["skill_id"], "finance_qa")

    def test_deprecation_routes_to_upgrade(self):
        """'deprecated' should trigger upgrade_advisor."""
        result = self._classify("This API is deprecated in 19")
        self.assertEqual(result["skill_id"], "odoo_upgrade_advisor")

    def test_aging_routes_to_collections(self):
        """'aging' is a collections/AR term."""
        result = self._classify("What does the aging report say?")
        self.assertEqual(result["skill_id"], "collections_assist")

    # ------------------------------------------------------------------
    # Skill instructions
    # ------------------------------------------------------------------

    def test_all_skills_have_instructions(self):
        """Every skill ID from INTENT_RULES should have instructions."""
        from odoo.addons.ipai_odoo_copilot.models.skill_router import (
            INTENT_RULES,
        )
        seen_skills = {rule[0] for rule in INTENT_RULES}
        for skill_id in seen_skills:
            instructions = self.router.get_skill_instructions(skill_id)
            self.assertTrue(
                instructions,
                "Skill '%s' has no instructions" % skill_id,
            )

    def test_general_has_no_instructions(self):
        """'general' is the fallback and has no specific instructions."""
        instructions = self.router.get_skill_instructions("general")
        self.assertFalse(instructions)
