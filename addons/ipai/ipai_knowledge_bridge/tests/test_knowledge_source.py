from odoo.tests import tagged, TransactionCase


@tagged("-at_install", "post_install")
class TestKnowledgeSource(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source = cls.env["ipai.knowledge.source"].create({
            "name": "Test Policy KB",
            "code": "test_policy",
            "source_type": "policy",
            "azure_index_name": "idx-test-policy",
        })

    def test_create_defaults_to_draft(self):
        self.assertEqual(self.source.state, "draft")

    def test_activate_source(self):
        self.source.action_activate()
        self.assertEqual(self.source.state, "active")

    def test_pause_source(self):
        self.source.action_activate()
        self.source.action_pause()
        self.assertEqual(self.source.state, "paused")

    def test_retire_source(self):
        self.source.action_activate()
        self.source.action_retire()
        self.assertEqual(self.source.state, "retired")

    def test_confidence_defaults(self):
        self.assertAlmostEqual(self.source.confidence_threshold, 0.70)
        self.assertTrue(self.source.abstain_below_threshold)

    def test_max_results_default(self):
        self.assertEqual(self.source.max_results, 5)

    def test_query_count_zero(self):
        self.assertEqual(self.source.query_count, 0)

    def test_code_unique_constraint(self):
        with self.assertRaises(Exception):
            self.env["ipai.knowledge.source"].create({
                "name": "Duplicate",
                "code": "test_policy",
                "source_type": "faq",
                "azure_index_name": "idx-dup",
            })

    def test_view_query_logs_action(self):
        action = self.source.action_view_query_logs()
        self.assertEqual(action["res_model"], "ipai.knowledge.query.log")
        self.assertIn(("source_id", "=", self.source.id), action["domain"])
