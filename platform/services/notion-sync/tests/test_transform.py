"""Tests for the transform module."""

from datetime import datetime

import pytest

from notion_sync.models import NotionPage
from notion_sync.transform import PageTransformer, PropertyExtractor


class TestPropertyExtractor:
    """Tests for PropertyExtractor."""

    def test_extract_title(self):
        prop = {"title": [{"plain_text": "Hello"}, {"plain_text": " World"}]}
        result = PropertyExtractor.extract_title(prop)
        assert result == "Hello World"

    def test_extract_title_empty(self):
        prop = {"title": []}
        result = PropertyExtractor.extract_title(prop)
        assert result is None

    def test_extract_rich_text(self):
        prop = {"rich_text": [{"plain_text": "Description text"}]}
        result = PropertyExtractor.extract_rich_text(prop)
        assert result == "Description text"

    def test_extract_number(self):
        prop = {"number": 42.5}
        result = PropertyExtractor.extract_number(prop)
        assert result == 42.5

    def test_extract_number_none(self):
        prop = {"number": None}
        result = PropertyExtractor.extract_number(prop)
        assert result is None

    def test_extract_select(self):
        prop = {"select": {"name": "In Progress"}}
        result = PropertyExtractor.extract_select(prop)
        assert result == "In Progress"

    def test_extract_select_none(self):
        prop = {"select": None}
        result = PropertyExtractor.extract_select(prop)
        assert result is None

    def test_extract_multi_select(self):
        prop = {"multi_select": [{"name": "Tag1"}, {"name": "Tag2"}]}
        result = PropertyExtractor.extract_multi_select(prop)
        assert result == ["Tag1", "Tag2"]

    def test_extract_date(self):
        prop = {"date": {"start": "2024-01-15"}}
        result = PropertyExtractor.extract_date(prop)
        assert result == datetime(2024, 1, 15, 0, 0, 0, tzinfo=None)

    def test_extract_date_with_time(self):
        prop = {"date": {"start": "2024-01-15T14:30:00Z"}}
        result = PropertyExtractor.extract_date(prop)
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_extract_person(self):
        prop = {"people": [{"name": "John Doe", "id": "user-123"}]}
        result = PropertyExtractor.extract_person(prop)
        assert result == "John Doe"

    def test_extract_person_empty(self):
        prop = {"people": []}
        result = PropertyExtractor.extract_person(prop)
        assert result is None

    def test_extract_relation(self):
        prop = {"relation": [{"id": "page-abc-123"}, {"id": "page-def-456"}]}
        result = PropertyExtractor.extract_relation(prop)
        assert result == "page-abc-123"

    def test_extract_relations(self):
        prop = {"relation": [{"id": "page-abc-123"}, {"id": "page-def-456"}]}
        result = PropertyExtractor.extract_relations(prop)
        assert result == ["page-abc-123", "page-def-456"]

    def test_extract_checkbox(self):
        prop = {"checkbox": True}
        result = PropertyExtractor.extract_checkbox(prop)
        assert result is True

    def test_extract_url(self):
        prop = {"url": "https://example.com"}
        result = PropertyExtractor.extract_url(prop)
        assert result == "https://example.com"


class TestPageTransformer:
    """Tests for PageTransformer."""

    def test_transform_page(self, sample_notion_page: NotionPage, sample_column_mappings):
        transformer = PageTransformer(sample_column_mappings)
        result = transformer.transform(sample_notion_page)

        assert result["id"] == sample_notion_page.id.replace("-", "")
        assert result["page_id"] == sample_notion_page.id
        assert result["name"] == "Test Project"
        assert result["status"] == "In Progress"
        assert result["budget_total"] == 100000
        assert result["owner"] == "John Doe"
        assert result["program_id"] == "program-abc-123"
        assert result["is_archived"] is False

    def test_transform_page_with_missing_property(self, sample_notion_page: NotionPage):
        mappings = [
            {"source": "Name", "target": "name", "type": "title"},
            {"source": "NonExistent", "target": "missing", "type": "text"},
        ]
        transformer = PageTransformer(mappings)
        result = transformer.transform(sample_notion_page)

        assert result["name"] == "Test Project"
        assert result["missing"] is None

    def test_transform_batch(self, sample_notion_page: NotionPage, sample_column_mappings):
        transformer = PageTransformer(sample_column_mappings)
        pages = [sample_notion_page, sample_notion_page]
        results = transformer.transform_batch(pages)

        assert len(results) == 2
        assert all(r["name"] == "Test Project" for r in results)
