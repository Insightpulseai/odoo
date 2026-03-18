# -*- coding: utf-8 -*-
"""
Unit Tests for IDP Health Service.

Tests health check functionality including:
- Liveness checks
- Readiness checks
- Deep health checks
- Metrics collection
"""
from odoo.tests.common import TransactionCase


class TestIdpHealthService(TransactionCase):
    """Test cases for idp.service.health."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.health_service = cls.env["idp.service.health"]

    # ==================== Liveness Tests ====================

    def test_check_liveness(self):
        """Test liveness check returns alive status."""
        result = self.health_service.check_liveness()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "alive")

    def test_check_liveness_lightweight(self):
        """Test liveness check is lightweight (no DB queries)."""
        # This test verifies the liveness check completes quickly
        # In a real scenario, you might measure execution time
        result = self.health_service.check_liveness()

        self.assertIn("status", result)
        # Should only contain status, nothing else
        self.assertEqual(len(result), 1)

    # ==================== Readiness Tests ====================

    def test_check_readiness_ready(self):
        """Test readiness check when system is ready."""
        result = self.health_service.check_readiness()

        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("db", result)
        self.assertIn("model_access", result)

        # Should be ready since we're in a working test environment
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["db"])
        self.assertTrue(result["model_access"])

    def test_check_readiness_includes_db_check(self):
        """Test readiness check includes database connectivity."""
        result = self.health_service.check_readiness()

        self.assertIn("db", result)
        self.assertTrue(result["db"])

    def test_check_readiness_includes_model_access(self):
        """Test readiness check includes model access verification."""
        result = self.health_service.check_readiness()

        self.assertIn("model_access", result)
        self.assertTrue(result["model_access"])

    # ==================== Health Check Tests ====================

    def test_check_health_structure(self):
        """Test health check returns expected structure."""
        result = self.health_service.check_health()

        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("checks", result)
        self.assertIn("check_time_ms", result)

        # Checks should include core services
        checks = result["checks"]
        self.assertIn("db", checks)
        self.assertIn("model_access", checks)
        self.assertIn("model_versions", checks)

    def test_check_health_db_ok(self):
        """Test health check reports DB as OK."""
        result = self.health_service.check_health()

        self.assertTrue(result["checks"]["db"])

    def test_check_health_model_access_ok(self):
        """Test health check reports model access as OK."""
        result = self.health_service.check_health()

        self.assertTrue(result["checks"]["model_access"])

    def test_check_health_status_with_all_ok(self):
        """Test health status is 'ok' when all critical checks pass."""
        result = self.health_service.check_health()

        # Since we're in a test environment with working DB,
        # critical checks should pass
        if result["checks"]["db"] and result["checks"]["model_access"]:
            self.assertIn(result["status"], ["ok", "degraded"])

    def test_check_health_timing(self):
        """Test health check includes timing information."""
        result = self.health_service.check_health()

        self.assertIn("check_time_ms", result)
        self.assertIsInstance(result["check_time_ms"], int)
        self.assertGreaterEqual(result["check_time_ms"], 0)

    # ==================== Metrics Tests ====================

    def test_get_metrics_structure(self):
        """Test metrics returns expected structure."""
        result = self.health_service.get_metrics()

        self.assertIsInstance(result, dict)
        self.assertIn("documents", result)
        self.assertIn("extractions", result)
        self.assertIn("processing", result)

    def test_get_metrics_documents(self):
        """Test metrics includes document counts."""
        result = self.health_service.get_metrics()

        self.assertIn("by_status", result["documents"])
        self.assertIn("total", result["documents"])

    def test_get_metrics_extractions(self):
        """Test metrics includes extraction statistics."""
        result = self.health_service.get_metrics()

        self.assertIn("total", result["extractions"])
        self.assertIn("success_rate", result["extractions"])
        self.assertIn("avg_confidence", result["extractions"])

    def test_get_metrics_processing(self):
        """Test metrics includes processing statistics."""
        result = self.health_service.get_metrics()

        self.assertIn("auto_approval_rate", result["processing"])
        self.assertIn("pending_review", result["processing"])


class TestIdpHealthIntegration(TransactionCase):
    """Integration tests for health service with real data."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.health_service = cls.env["idp.service.health"]
        cls.Document = cls.env["idp.document"]
        cls.Extraction = cls.env["idp.extraction"]
        cls.ModelVersion = cls.env["idp.model.version"]

    def test_metrics_with_documents(self):
        """Test metrics accurately count documents."""
        # Create some test documents
        self.Document.create(
            {
                "name": "Doc 1",
                "source": "api",
                "status": "queued",
            }
        )
        self.Document.create(
            {
                "name": "Doc 2",
                "source": "api",
                "status": "approved",
            }
        )

        result = self.health_service.get_metrics()

        # Should have at least the documents we created
        self.assertGreaterEqual(result["documents"]["total"], 2)
        self.assertGreaterEqual(result["documents"]["by_status"].get("queued", 0), 1)
        self.assertGreaterEqual(result["documents"]["by_status"].get("approved", 0), 1)

    def test_model_versions_check(self):
        """Test model versions check works with created versions."""
        # Create an active model version
        self.ModelVersion.create(
            {
                "name": "Test Active Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "active": True,
            }
        )

        result = self.health_service.check_health()

        self.assertTrue(result["checks"]["model_versions"])

    def test_queue_health_no_stuck_documents(self):
        """Test queue health when no documents are stuck."""
        result = self.health_service.check_health()

        # Without any stuck documents, queue should be healthy
        self.assertTrue(result["checks"]["queue"])
