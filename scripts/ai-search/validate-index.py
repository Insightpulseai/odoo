#!/usr/bin/env python3
"""Validate Azure AI Search index populated from the knowledge base.

Performs the following checks:
  1. Queries the index for total document count
  2. Runs a sample search per kb_scope
  3. Tests security trimming filter syntax
  4. Reports results with pass/fail status

Environment variables required:
    AZURE_SEARCH_ENDPOINT  — e.g. https://srch-ipai-dev.search.windows.net/
    AZURE_SEARCH_API_KEY   — admin or query API key

Usage:
    export AZURE_SEARCH_ENDPOINT="https://srch-ipai-dev.search.windows.net/"
    export AZURE_SEARCH_API_KEY="$(az keyvault secret show --vault-name kv-ipai-dev --name srch-ipai-dev-api-key --query value -o tsv)"
    python scripts/ai-search/validate-index.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INDEX_NAME = "ipai-knowledge-base"
API_VERSION = "2024-07-01"

# Expected knowledge base scopes
EXPECTED_SCOPES = [
    "general-kb",
    "finance-close-kb",
    "bir-compliance",
    "marketing-playbooks",
    "ops-kb",
]

# Sample search queries per scope
SAMPLE_QUERIES: dict[str, str] = {
    "general-kb": "Odoo CE modules deployment",
    "finance-close-kb": "month-end reconciliation journal entries",
    "bir-compliance": "VAT withholding BIR form 2550",
    "marketing-playbooks": "campaign lead pipeline CRM",
    "ops-kb": "deployment container health check incident",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        log.error("Missing required environment variable: %s", name)
        sys.exit(1)
    return value


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class SearchClient:
    """Minimal Azure AI Search REST client for validation."""

    def __init__(self, endpoint: str, api_key: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "api-key": api_key,
            }
        )

    def _url(self, path: str) -> str:
        return f"{self.endpoint}{path}?api-version={API_VERSION}"

    def get_index_stats(self) -> dict[str, Any] | None:
        """Get index statistics (document count, storage size)."""
        resp = self.session.get(self._url(f"/indexes/{INDEX_NAME}/stats"))
        if resp.status_code == 200:
            return resp.json()
        return None

    def count_documents(self) -> int:
        """Get total document count."""
        resp = self.session.get(self._url(f"/indexes/{INDEX_NAME}/docs/$count"))
        if resp.status_code == 200:
            try:
                return int(resp.text)
            except ValueError:
                return -1
        return -1

    def search(
        self,
        query: str,
        filter_expr: str | None = None,
        top: int = 5,
        select: str = "id,title,kb_scope,source_file,chunk_index",
    ) -> dict[str, Any]:
        """Execute a search query."""
        url = self._url(f"/indexes/{INDEX_NAME}/docs/search")
        body: dict[str, Any] = {
            "search": query,
            "top": top,
            "select": select,
            "count": True,
        }
        if filter_expr:
            body["filter"] = filter_expr

        resp = self.session.post(url, json=body)
        if resp.status_code == 200:
            return resp.json()
        return {"error": resp.status_code, "message": resp.text[:500]}

    def facet_search(self, facet_field: str) -> dict[str, int]:
        """Run a faceted search to get value distribution."""
        url = self._url(f"/indexes/{INDEX_NAME}/docs/search")
        body = {
            "search": "*",
            "top": 0,
            "facets": [f"{facet_field},count:50"],
            "count": True,
        }
        resp = self.session.post(url, json=body)
        if resp.status_code == 200:
            data = resp.json()
            facets = data.get("@search.facets", {}).get(facet_field, [])
            return {f["value"]: f["count"] for f in facets}
        return {}


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


def test_document_count(client: SearchClient) -> TestResult:
    """Test 1: Verify the index has documents."""
    count = client.count_documents()
    if count > 0:
        return TestResult(
            name="Document Count",
            passed=True,
            message=f"Index contains {count} documents.",
            details={"count": count},
        )
    elif count == 0:
        return TestResult(
            name="Document Count",
            passed=False,
            message="Index is empty. Run populate-index.py first.",
            details={"count": 0},
        )
    else:
        return TestResult(
            name="Document Count",
            passed=False,
            message="Failed to query document count. Check endpoint and API key.",
            details={"count": count},
        )


def test_scope_coverage(client: SearchClient) -> TestResult:
    """Test 2: Verify all expected kb_scopes are present."""
    facets = client.facet_search("kb_scope")
    if not facets:
        return TestResult(
            name="Scope Coverage",
            passed=False,
            message="Failed to retrieve kb_scope facets.",
            details={"facets": {}},
        )

    present = set(facets.keys())
    expected = set(EXPECTED_SCOPES)
    missing = expected - present
    extra = present - expected

    if not missing:
        return TestResult(
            name="Scope Coverage",
            passed=True,
            message=f"All {len(expected)} expected scopes present. Distribution: {facets}",
            details={"facets": facets, "missing": [], "extra": list(extra)},
        )
    else:
        return TestResult(
            name="Scope Coverage",
            passed=False,
            message=f"Missing scopes: {missing}. Present: {facets}",
            details={"facets": facets, "missing": list(missing), "extra": list(extra)},
        )


def test_sample_searches(client: SearchClient) -> list[TestResult]:
    """Test 3: Run a sample search for each kb_scope."""
    results = []
    for scope, query in SAMPLE_QUERIES.items():
        filter_expr = f"kb_scope eq '{scope}'"
        search_result = client.search(query=query, filter_expr=filter_expr, top=3)

        if "error" in search_result:
            results.append(
                TestResult(
                    name=f"Search [{scope}]",
                    passed=False,
                    message=f"Search failed: {search_result['message'][:200]}",
                    details=search_result,
                )
            )
            continue

        count = search_result.get("@odata.count", 0)
        hits = search_result.get("value", [])

        if hits:
            top_hit = hits[0]
            results.append(
                TestResult(
                    name=f"Search [{scope}]",
                    passed=True,
                    message=(
                        f"Query '{query}' returned {count} results. "
                        f"Top hit: {top_hit.get('title', 'N/A')} "
                        f"(source: {top_hit.get('source_file', 'N/A')}, "
                        f"chunk: {top_hit.get('chunk_index', 'N/A')})"
                    ),
                    details={"count": count, "top_hit": top_hit},
                )
            )
        else:
            results.append(
                TestResult(
                    name=f"Search [{scope}]",
                    passed=False,
                    message=f"Query '{query}' in scope '{scope}' returned 0 results.",
                    details={"count": 0},
                )
            )

    return results


def test_security_trimming(client: SearchClient) -> TestResult:
    """Test 4: Verify security trimming filter syntax works."""
    # Test with a placeholder group ID — should match all documents
    # that have this placeholder (which is all of them in initial setup)
    filter_expr = "group_ids/any(g: g eq 'group-guid-placeholder')"
    search_result = client.search(
        query="*",
        filter_expr=filter_expr,
        top=1,
    )

    if "error" in search_result:
        return TestResult(
            name="Security Trimming Filter",
            passed=False,
            message=f"Filter syntax error: {search_result['message'][:200]}",
            details=search_result,
        )

    count = search_result.get("@odata.count", 0)
    if count > 0:
        return TestResult(
            name="Security Trimming Filter",
            passed=True,
            message=f"group_ids filter works correctly. {count} documents matched placeholder group.",
            details={"count": count},
        )
    else:
        return TestResult(
            name="Security Trimming Filter",
            passed=False,
            message="group_ids filter returned 0 results. Documents may not have group_ids set.",
            details={"count": 0},
        )


def test_security_trimming_exclusion(client: SearchClient) -> TestResult:
    """Test 5: Verify security trimming correctly excludes with non-matching group."""
    filter_expr = "group_ids/any(g: g eq 'nonexistent-group-id-12345')"
    search_result = client.search(
        query="*",
        filter_expr=filter_expr,
        top=1,
    )

    if "error" in search_result:
        return TestResult(
            name="Security Trimming Exclusion",
            passed=False,
            message=f"Filter syntax error: {search_result['message'][:200]}",
            details=search_result,
        )

    count = search_result.get("@odata.count", 0)
    if count == 0:
        return TestResult(
            name="Security Trimming Exclusion",
            passed=True,
            message="Non-matching group correctly returned 0 results.",
            details={"count": 0},
        )
    else:
        return TestResult(
            name="Security Trimming Exclusion",
            passed=False,
            message=f"Non-matching group returned {count} results (expected 0).",
            details={"count": count},
        )


def test_index_stats(client: SearchClient) -> TestResult:
    """Test 6: Get and report index statistics."""
    stats = client.get_index_stats()
    if stats:
        doc_count = stats.get("documentCount", 0)
        storage_bytes = stats.get("storageSize", 0)
        storage_kb = storage_bytes / 1024
        storage_mb = storage_kb / 1024

        return TestResult(
            name="Index Statistics",
            passed=True,
            message=(
                f"Documents: {doc_count}, "
                f"Storage: {storage_mb:.2f} MB ({storage_kb:.0f} KB)"
            ),
            details=stats,
        )
    else:
        return TestResult(
            name="Index Statistics",
            passed=False,
            message="Failed to retrieve index statistics.",
            details={},
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    log.info("=" * 60)
    log.info("Azure AI Search — Index Validation")
    log.info("=" * 60)

    endpoint = _require_env("AZURE_SEARCH_ENDPOINT")
    api_key = _require_env("AZURE_SEARCH_API_KEY")

    log.info("Endpoint: %s", endpoint)
    log.info("Index: %s", INDEX_NAME)

    client = SearchClient(endpoint, api_key)

    # Run all tests
    all_results: list[TestResult] = []

    all_results.append(test_document_count(client))
    all_results.append(test_scope_coverage(client))
    all_results.extend(test_sample_searches(client))
    all_results.append(test_security_trimming(client))
    all_results.append(test_security_trimming_exclusion(client))
    all_results.append(test_index_stats(client))

    # Report
    log.info("")
    log.info("=" * 60)
    log.info("VALIDATION RESULTS")
    log.info("=" * 60)

    passed = 0
    failed = 0
    for result in all_results:
        status = "PASS" if result.passed else "FAIL"
        icon = "+" if result.passed else "-"
        log.info("[%s] %s: %s", status, result.name, result.message)
        if result.passed:
            passed += 1
        else:
            failed += 1

    log.info("")
    log.info("-" * 60)
    log.info("Total: %d tests | Passed: %d | Failed: %d", passed + failed, passed, failed)
    log.info("-" * 60)

    if failed > 0:
        log.error("Validation completed with %d failure(s).", failed)
        sys.exit(1)
    else:
        log.info("All validations passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
