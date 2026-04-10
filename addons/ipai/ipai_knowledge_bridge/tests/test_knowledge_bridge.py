from unittest.mock import patch, MagicMock

from odoo.tests import tagged, TransactionCase


@tagged("-at_install", "post_install")
class TestKnowledgeBridge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source = cls.env["ipai.knowledge.source"].create({
            "name": "Test Finance KB",
            "code": "test_finance",
            "source_type": "policy",
            "azure_index_name": "idx-test-finance",
            "confidence_threshold": 0.70,
            "abstain_below_threshold": True,
            "state": "active",
        })
        cls.env["ir.config_parameter"].sudo().set_param(
            "ipai_knowledge.azure_search_endpoint",
            "https://test-search.search.windows.net",
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "ipai_knowledge.azure_openai_endpoint",
            "https://test-openai.openai.azure.com",
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "ipai_knowledge.azure_openai_deployment",
            "gpt-4o",
        )

    def _mock_search_response(self, score=3.5):
        return [
            {
                "id": "doc1",
                "title": "Close Checklist",
                "content": "Step 1: Reconcile accounts.",
                "section": "Monthly Close",
                "url": "https://kb.test/close-checklist",
                "@search.rerankerScore": score,
            },
        ]

    def _mock_openai_response(self, answer="Step 1: Reconcile accounts. [1]"):
        return {
            "choices": [
                {"message": {"content": answer}},
            ],
            "model": "gpt-4o",
        }

    @patch.dict("os.environ", {"AZURE_SEARCH_API_KEY": "test-key",
                                "AZURE_OPENAI_API_KEY": "test-key"})
    @patch("requests.post")
    def test_query_returns_answer_with_citations(self, mock_post):
        mock_post.side_effect = [
            MagicMock(
                status_code=200,
                json=lambda: {"value": self._mock_search_response(3.5)},
                raise_for_status=lambda: None,
            ),
            MagicMock(
                status_code=200,
                json=lambda: self._mock_openai_response(),
                raise_for_status=lambda: None,
            ),
        ]

        bridge = self.env["ipai.knowledge.bridge"]
        result = bridge.query("test_finance", "How do I close the month?")

        self.assertFalse(result["abstained"])
        self.assertIn("Reconcile", result["answer"])
        self.assertEqual(len(result["citations"]), 1)
        self.assertTrue(result["log_id"])

    @patch.dict("os.environ", {"AZURE_SEARCH_API_KEY": "test-key"})
    @patch("requests.post")
    def test_query_abstains_below_threshold(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"value": self._mock_search_response(0.5)},
            raise_for_status=lambda: None,
        )

        bridge = self.env["ipai.knowledge.bridge"]
        result = bridge.query("test_finance", "What is the meaning of life?")

        self.assertTrue(result["abstained"])
        self.assertIn("cannot find", result["answer"])

    def test_query_no_active_source(self):
        bridge = self.env["ipai.knowledge.bridge"]
        result = bridge.query("nonexistent_code", "test question")

        self.assertTrue(result["abstained"])
        self.assertIn("No active source", result["error"])

    @patch.dict("os.environ", {"AZURE_SEARCH_API_KEY": "test-key"})
    @patch("requests.post")
    def test_bridge_logs_query(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"value": self._mock_search_response(0.5)},
            raise_for_status=lambda: None,
        )

        bridge = self.env["ipai.knowledge.bridge"]
        result = bridge.query(
            "test_finance", "Test query",
            caller_surface="unit_test",
        )

        log = self.env["ipai.knowledge.query.log"].browse(result["log_id"])
        self.assertTrue(log.exists())
        self.assertEqual(log.query_text, "Test query")
        self.assertEqual(log.caller_surface, "unit_test")

    @patch.dict("os.environ", {"AZURE_SEARCH_API_KEY": "test-key"})
    @patch("requests.post")
    def test_search_failure_returns_error(self, mock_post):
        mock_post.side_effect = Exception("Connection timeout")

        bridge = self.env["ipai.knowledge.bridge"]
        result = bridge.query("test_finance", "test")

        self.assertTrue(result["abstained"])
        self.assertIn("Connection timeout", result["error"])
        self.assertTrue(result["log_id"])

    def test_list_sources(self):
        bridge = self.env["ipai.knowledge.bridge"]
        sources = bridge.list_sources()
        codes = [s["code"] for s in sources]
        self.assertIn("test_finance", codes)

    def test_all_models_registered(self):
        for model_name in [
            "ipai.knowledge.source",
            "ipai.knowledge.query.log",
            "ipai.knowledge.citation",
            "ipai.knowledge.bridge",
        ]:
            self.assertIn(model_name, self.env)
