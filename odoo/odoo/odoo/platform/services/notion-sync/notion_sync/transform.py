"""Transform Notion page properties to normalized columns."""

from datetime import datetime
from typing import Any

import structlog

from .models import NotionPage

logger = structlog.get_logger()


class PropertyExtractor:
    """Extract typed values from Notion property objects."""

    @staticmethod
    def extract_title(prop: dict[str, Any]) -> str | None:
        """Extract text from title property."""
        title_list = prop.get("title", [])
        if not title_list:
            return None
        return "".join(t.get("plain_text", "") for t in title_list)

    @staticmethod
    def extract_rich_text(prop: dict[str, Any]) -> str | None:
        """Extract text from rich_text property."""
        text_list = prop.get("rich_text", [])
        if not text_list:
            return None
        return "".join(t.get("plain_text", "") for t in text_list)

    @staticmethod
    def extract_text(prop: dict[str, Any]) -> str | None:
        """Extract text from text property (alias for rich_text)."""
        return PropertyExtractor.extract_rich_text(prop)

    @staticmethod
    def extract_number(prop: dict[str, Any]) -> float | None:
        """Extract number from number property."""
        return prop.get("number")

    @staticmethod
    def extract_select(prop: dict[str, Any]) -> str | None:
        """Extract value from select property."""
        select = prop.get("select")
        if not select:
            return None
        return select.get("name")

    @staticmethod
    def extract_multi_select(prop: dict[str, Any]) -> list[str]:
        """Extract values from multi_select property."""
        selections = prop.get("multi_select", [])
        return [s.get("name") for s in selections if s.get("name")]

    @staticmethod
    def extract_date(prop: dict[str, Any]) -> datetime | None:
        """Extract date from date property."""
        date_obj = prop.get("date")
        if not date_obj:
            return None
        start = date_obj.get("start")
        if not start:
            return None
        try:
            # Handle both date and datetime formats
            if "T" in start:
                return datetime.fromisoformat(start.replace("Z", "+00:00"))
            return datetime.fromisoformat(start + "T00:00:00+00:00")
        except ValueError:
            return None

    @staticmethod
    def extract_person(prop: dict[str, Any]) -> str | None:
        """Extract name from people property."""
        people = prop.get("people", [])
        if not people:
            return None
        # Return first person's name
        first_person = people[0]
        return first_person.get("name") or first_person.get("id")

    @staticmethod
    def extract_relation(prop: dict[str, Any]) -> str | None:
        """Extract first related page ID from relation property."""
        relations = prop.get("relation", [])
        if not relations:
            return None
        return relations[0].get("id")

    @staticmethod
    def extract_relations(prop: dict[str, Any]) -> list[str]:
        """Extract all related page IDs from relation property."""
        relations = prop.get("relation", [])
        return [r.get("id") for r in relations if r.get("id")]

    @staticmethod
    def extract_checkbox(prop: dict[str, Any]) -> bool:
        """Extract boolean from checkbox property."""
        return prop.get("checkbox", False)

    @staticmethod
    def extract_url(prop: dict[str, Any]) -> str | None:
        """Extract URL from url property."""
        return prop.get("url")

    @staticmethod
    def extract_email(prop: dict[str, Any]) -> str | None:
        """Extract email from email property."""
        return prop.get("email")

    @staticmethod
    def extract_phone(prop: dict[str, Any]) -> str | None:
        """Extract phone from phone_number property."""
        return prop.get("phone_number")

    @staticmethod
    def extract(prop: dict[str, Any], prop_type: str) -> Any:
        """Extract value based on property type."""
        extractors = {
            "title": PropertyExtractor.extract_title,
            "rich_text": PropertyExtractor.extract_rich_text,
            "text": PropertyExtractor.extract_text,
            "number": PropertyExtractor.extract_number,
            "select": PropertyExtractor.extract_select,
            "multi_select": PropertyExtractor.extract_multi_select,
            "date": PropertyExtractor.extract_date,
            "person": PropertyExtractor.extract_person,
            "relation": PropertyExtractor.extract_relation,
            "checkbox": PropertyExtractor.extract_checkbox,
            "url": PropertyExtractor.extract_url,
            "email": PropertyExtractor.extract_email,
            "phone": PropertyExtractor.extract_phone,
        }

        extractor = extractors.get(prop_type)
        if not extractor:
            logger.warning("Unknown property type", type=prop_type)
            return None

        return extractor(prop)


class PageTransformer:
    """Transform Notion pages to normalized records."""

    def __init__(self, column_mappings: list[dict[str, str]]):
        """
        Initialize transformer with column mappings.

        Args:
            column_mappings: List of dicts with 'source', 'target', 'type' keys
        """
        self.mappings = column_mappings
        self.extractor = PropertyExtractor()
        self.logger = logger.bind(service="page-transformer")

    def transform(self, page: NotionPage) -> dict[str, Any]:
        """Transform a Notion page to a normalized record."""
        record = {
            "id": page.id.replace("-", ""),
            "page_id": page.id,
            "last_edited_time": page.last_edited_time,
            "is_archived": page.archived,
        }

        for mapping in self.mappings:
            source_name = mapping["source"]
            target_name = mapping["target"]
            prop_type = mapping["type"]

            prop = page.properties.get(source_name, {})
            if not prop:
                # Try with normalized source name
                normalized = source_name.replace(" ", "_").lower()
                for key in page.properties:
                    if key.replace(" ", "_").lower() == normalized:
                        prop = page.properties[key]
                        break

            if prop:
                value = self.extractor.extract(prop, prop_type)
                record[target_name] = value
            else:
                record[target_name] = None

        return record

    def transform_batch(self, pages: list[NotionPage]) -> list[dict[str, Any]]:
        """Transform a batch of pages."""
        return [self.transform(page) for page in pages]
