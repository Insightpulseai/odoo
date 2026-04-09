"""
Odoo 18 Documentation Retrieval Evaluator

Seeded evaluation queries to validate retrieval quality.
Run after indexing to ensure chunks are discoverable and relevant.
"""

import logging
import os
from dataclasses import dataclass

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

logger = logging.getLogger(__name__)


@dataclass
class EvalResult:
    """Result of a single evaluation query."""

    query: str
    expected_path_prefix: str
    top_k: int
    hits: list[dict]
    path_hit: bool  # Did any result match expected path?
    mrr: float  # Mean reciprocal rank for path match


# Seeded evaluation queries — known answers in the Odoo 18 docs
EVAL_QUERIES = [
    {
        "query": "How to configure fiscal positions in Odoo accounting",
        "expected_path_prefix": "content/applications/finance/accounting",
        "description": "Accounting fiscal positions",
    },
    {
        "query": "Create a sales order with multiple lines",
        "expected_path_prefix": "content/applications/sales",
        "description": "Sales order creation",
    },
    {
        "query": "Configure SMTP outgoing mail server",
        "expected_path_prefix": "content/applications/general",
        "description": "Email configuration",
    },
    {
        "query": "Install and configure inventory module",
        "expected_path_prefix": "content/applications/inventory",
        "description": "Inventory setup",
    },
    {
        "query": "How to create a custom Odoo module",
        "expected_path_prefix": "content/developer",
        "description": "Module development tutorial",
    },
    {
        "query": "User access rights and groups",
        "expected_path_prefix": "content/applications/general",
        "description": "Access control",
    },
    {
        "query": "ORM API recordset methods",
        "expected_path_prefix": "content/developer/reference",
        "description": "ORM reference",
    },
    {
        "query": "QWeb template engine syntax",
        "expected_path_prefix": "content/developer",
        "description": "QWeb reference",
    },
    {
        "query": "Bank reconciliation process",
        "expected_path_prefix": "content/applications/finance",
        "description": "Bank reconciliation",
    },
    {
        "query": "Website builder and page editor",
        "expected_path_prefix": "content/applications/websites",
        "description": "Website editor",
    },
]


class RetrievalEvaluator:
    """Evaluate retrieval quality against seeded queries."""

    def __init__(
        self,
        index_name: str = "odoo18-docs",
        top_k: int = 8,
    ):
        endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
        key = os.environ["AZURE_SEARCH_API_KEY"]
        self.client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key),
        )
        self.top_k = top_k

    def run_eval(
        self, queries: list[dict] | None = None
    ) -> list[EvalResult]:
        """Run evaluation queries and measure retrieval quality."""
        if queries is None:
            queries = EVAL_QUERIES

        results = []
        for q in queries:
            result = self._eval_single(
                query=q["query"],
                expected_path_prefix=q["expected_path_prefix"],
            )
            results.append(result)

            status = "HIT" if result.path_hit else "MISS"
            logger.info(
                "[%s] %s (MRR=%.2f) — %s",
                status,
                q.get("description", q["query"][:40]),
                result.mrr,
                q["query"],
            )

        return results

    def _eval_single(
        self, query: str, expected_path_prefix: str
    ) -> EvalResult:
        """Evaluate a single query."""
        response = self.client.search(
            search_text=query,
            select=["chunk_id", "path", "heading_chain", "content"],
            top=self.top_k,
        )

        hits = []
        path_hit = False
        mrr = 0.0

        for rank, result in enumerate(response, start=1):
            hit = {
                "rank": rank,
                "chunk_id": result["chunk_id"],
                "path": result["path"],
                "heading_chain": result.get("heading_chain", ""),
                "content_preview": result["content"][:200],
            }
            hits.append(hit)

            if (
                not path_hit
                and result["path"].startswith(expected_path_prefix)
            ):
                path_hit = True
                mrr = 1.0 / rank

        return EvalResult(
            query=query,
            expected_path_prefix=expected_path_prefix,
            top_k=self.top_k,
            hits=hits,
            path_hit=path_hit,
            mrr=mrr,
        )

    def summary(self, results: list[EvalResult]) -> dict:
        """Compute aggregate eval metrics."""
        total = len(results)
        hits = sum(1 for r in results if r.path_hit)
        avg_mrr = sum(r.mrr for r in results) / total if total else 0

        summary = {
            "total_queries": total,
            "path_hits": hits,
            "path_hit_rate": hits / total if total else 0,
            "mean_reciprocal_rank": avg_mrr,
            "per_query": [
                {
                    "query": r.query,
                    "path_hit": r.path_hit,
                    "mrr": r.mrr,
                    "top_result_path": r.hits[0]["path"] if r.hits else None,
                }
                for r in results
            ],
        }

        logger.info(
            "Eval summary: %d/%d hits (%.0f%%), MRR=%.3f",
            hits,
            total,
            summary["path_hit_rate"] * 100,
            avg_mrr,
        )

        return summary
