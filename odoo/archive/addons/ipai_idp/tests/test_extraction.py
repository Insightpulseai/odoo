# -*- coding: utf-8 -*-
"""
Unit Tests for IDP Extraction.

Tests LLM extraction including:
- Model version management
- Extraction creation
- Response parsing
"""
import json

from odoo.tests.common import TransactionCase


class TestIdpModelVersion(TransactionCase):
    """Test cases for idp.model.version."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.ModelVersion = cls.env["idp.model.version"]

    def test_create_model_version(self):
        """Test creating a model version."""
        version = self.ModelVersion.create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "active": True,
            }
        )

        self.assertTrue(version.exists())
        self.assertEqual(version.name, "Test Version")
        self.assertEqual(version.doc_type, "invoice")
        self.assertIsNotNone(version.version_code)

    def test_version_code_generation(self):
        """Test version code is generated from content hash."""
        version = self.ModelVersion.create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "system_prompt": "Test prompt",
                "extraction_schema": '{"field": "value"}',
            }
        )

        # Version code should include doc_type
        self.assertTrue(version.version_code.startswith("invoice-"))

    def test_get_default_version(self):
        """Test getting default version for document type."""
        # Create a default version
        version = self.ModelVersion.create(
            {
                "name": "Default Invoice",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "active": True,
                "is_default": True,
            }
        )

        result = self.ModelVersion.get_default_version("invoice")
        self.assertEqual(result.id, version.id)

    def test_get_default_version_fallback_to_all(self):
        """Test fallback to 'all' doc_type when specific not found."""
        # Create a default version for 'all'
        version = self.ModelVersion.create(
            {
                "name": "Default All",
                "doc_type": "all",
                "llm_model": "claude-3-sonnet",
                "active": True,
                "is_default": True,
            }
        )

        result = self.ModelVersion.get_default_version("delivery_note")
        self.assertEqual(result.id, version.id)

    def test_render_prompt(self):
        """Test rendering prompt with OCR text."""
        version = self.ModelVersion.create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "extraction_prompt_template": "OCR: {{OCR_TEXT}}\nSchema: {{SCHEMA_JSON}}",
                "extraction_schema": '{"field": "value"}',
            }
        )

        result = version.render_prompt("Test OCR text")

        self.assertIn("Test OCR text", result)
        self.assertIn('{"field": "value"}', result)

    def test_set_as_default(self):
        """Test setting a version as default."""
        version1 = self.ModelVersion.create(
            {
                "name": "Version 1",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "is_default": True,
            }
        )

        version2 = self.ModelVersion.create(
            {
                "name": "Version 2",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "is_default": False,
            }
        )

        version2.action_set_as_default()

        version1.refresh()
        version2.refresh()

        self.assertFalse(version1.is_default)
        self.assertTrue(version2.is_default)

    def test_get_schema_dict(self):
        """Test parsing schema JSON."""
        version = self.ModelVersion.create(
            {
                "name": "Test Version",
                "doc_type": "invoice",
                "llm_model": "claude-3-sonnet",
                "extraction_schema": '{"vendor_name": "string", "total": "number"}',
            }
        )

        schema = version.get_schema_dict()

        self.assertIsInstance(schema, dict)
        self.assertIn("vendor_name", schema)
        self.assertIn("total", schema)


class TestIdpExtraction(TransactionCase):
    """Test cases for idp.extraction."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.Document = cls.env["idp.document"]
        cls.Extraction = cls.env["idp.extraction"]
        cls.ModelVersion = cls.env["idp.model.version"]

    def _create_test_document(self):
        """Create a test document."""
        return self.Document.create(
            {
                "name": "Test Document",
                "doc_type": "invoice",
                "source": "api",
                "status": "queued",
            }
        )

    def test_create_extraction(self):
        """Test creating an extraction record."""
        document = self._create_test_document()

        extraction = self.Extraction.create(
            {
                "document_id": document.id,
                "extracted_json": json.dumps(
                    {
                        "vendor_name": "Test Vendor",
                        "total": 100.00,
                        "currency": "PHP",
                    }
                ),
                "confidence": 0.95,
            }
        )

        self.assertTrue(extraction.exists())
        self.assertEqual(extraction.vendor_name, "Test Vendor")
        self.assertEqual(extraction.total_amount, 100.00)
        self.assertEqual(extraction.currency, "PHP")

    def test_get_extracted_data(self):
        """Test getting extracted data as dict."""
        document = self._create_test_document()

        extraction = self.Extraction.create(
            {
                "document_id": document.id,
                "extracted_json": json.dumps(
                    {
                        "vendor_name": "Test Vendor",
                        "line_items": [
                            {"description": "Item 1", "amount": 50},
                            {"description": "Item 2", "amount": 50},
                        ],
                        "total": 100.00,
                    }
                ),
                "confidence": 0.95,
            }
        )

        data = extraction.get_extracted_data()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["vendor_name"], "Test Vendor")
        self.assertEqual(len(data["line_items"]), 2)

    def test_get_line_items(self):
        """Test extracting line items."""
        document = self._create_test_document()

        extraction = self.Extraction.create(
            {
                "document_id": document.id,
                "extracted_json": json.dumps(
                    {
                        "line_items": [
                            {"description": "Item 1", "amount": 50},
                            {"description": "Item 2", "amount": 50},
                        ],
                    }
                ),
                "confidence": 0.95,
            }
        )

        items = extraction.get_line_items()

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["description"], "Item 1")

    def test_computed_fields_from_json(self):
        """Test that computed fields are populated from JSON."""
        document = self._create_test_document()

        extraction = self.Extraction.create(
            {
                "document_id": document.id,
                "extracted_json": json.dumps(
                    {
                        "vendor_name": "ABC Company",
                        "invoice_number": "INV-001",
                        "invoice_date": "2024-12-06",
                        "total": 1234.50,
                        "currency": "USD",
                    }
                ),
                "confidence": 0.90,
            }
        )

        self.assertEqual(extraction.vendor_name, "ABC Company")
        self.assertEqual(extraction.invoice_number, "INV-001")
        self.assertEqual(extraction.total_amount, 1234.50)
        self.assertEqual(extraction.currency, "USD")

    def test_merchant_name_fallback(self):
        """Test vendor_name computed from merchant_name."""
        document = self._create_test_document()
        document.doc_type = "receipt"

        extraction = self.Extraction.create(
            {
                "document_id": document.id,
                "extracted_json": json.dumps(
                    {
                        "merchant_name": "Coffee Shop",
                        "total": 5.00,
                    }
                ),
                "confidence": 0.85,
            }
        )

        # Should use merchant_name as vendor_name
        self.assertEqual(extraction.vendor_name, "Coffee Shop")


class TestIdpDocument(TransactionCase):
    """Test cases for idp.document."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.Document = cls.env["idp.document"]

    def test_create_document(self):
        """Test creating a document."""
        document = self.Document.create(
            {
                "name": "Test Invoice.pdf",
                "doc_type": "invoice",
                "source": "upload",
            }
        )

        self.assertTrue(document.exists())
        self.assertEqual(document.status, "queued")

    def test_compute_file_hash(self):
        """Test computing file hash."""
        content = b"Test file content"
        hash_result = self.Document.compute_file_hash(content)

        self.assertIsNotNone(hash_result)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex digest

    def test_find_duplicate(self):
        """Test finding duplicate by hash."""
        test_hash = "abc123def456"

        # Create a document with the hash
        document = self.Document.create(
            {
                "name": "Original",
                "file_hash": test_hash,
                "source": "upload",
            }
        )

        # Find by hash
        duplicate = self.Document.find_duplicate(test_hash)
        self.assertEqual(duplicate.id, document.id)

        # No duplicate for different hash
        no_duplicate = self.Document.find_duplicate("xyz789")
        self.assertFalse(no_duplicate)

    def test_latest_extraction(self):
        """Test getting latest extraction."""
        document = self.Document.create(
            {
                "name": "Test",
                "source": "api",
            }
        )

        # Create two extractions
        ext1 = self.env["idp.extraction"].create(
            {
                "document_id": document.id,
                "extracted_json": "{}",
                "confidence": 0.5,
            }
        )
        ext2 = self.env["idp.extraction"].create(
            {
                "document_id": document.id,
                "extracted_json": "{}",
                "confidence": 0.9,
            }
        )

        # Latest should be ext2
        self.assertEqual(document.latest_extraction_id.id, ext2.id)
