#!/usr/bin/env python3
"""Smoke test for rag.hybrid_search_rrf and rag.fts_search RPCs.

Runs test queries against Supabase to verify the hybrid search pipeline works.
Falls back to fts_search if no embeddings are available.

Usage:
    python scripts/rag/smoke_query.py                  # full smoke test
    python scripts/rag/smoke_query.py --query "copilot tools"  # single query
    python scripts/rag/smoke_query.py --fts-only       # skip vector search

Environment:
    SUPABASE_URL              - Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key
    RAG_TENANT_ID             - (optional) Tenant UUID

Exit codes:
    0 = all smoke queries returned results
    1 = one or more queries returned no results or error
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

DEFAULT_TENANT_ID = os.environ.get(
    "RAG_TENANT_ID", "00000000-0000-0000-0000-000000000001"
)

SMOKE_QUERIES = [
    {
        "id": "SMOKE-001",
        "query": "AI copilot non-negotiable rules",
        "expected_corpus": "spec_bundles",
        "min_results": 1,
    },
    {
        "id": "SMOKE-002",
        "query": "tool permissions contract",
        "expected_corpus": "docs_contracts",
        "min_results": 1,
    },
    {
        "id": "SMOKE-003",
        "query": "Gemini provider Odoo AI",
        "expected_corpus": "ssot_yaml",
        "min_results": 1,
    },
    {
        "id": "SMOKE-004",
        "query": "release contract gates passed",
        "expected_corpus": "ssot_yaml",
        "min_results": 1,
    },
    {
        "id": "SMOKE-005",
        "query": "IPAI module naming convention",
        "expected_corpus": "docs_ai",
        "min_results": 1,
    },
]


def rpc_call(
    function_name: str,
    params: dict,
    *,
    supabase_url: str,
    service_key: str,
) -> dict:
    """Call a Supabase RPC function."""
    url = f"{supabase_url}/rest/v1/rpc/{function_name}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    body = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return {"status": "ok", "results": data}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"status": "error", "code": e.code, "error": error_body}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_fts_query(
    query: str,
    *,
    supabase_url: str,
    service_key: str,
    corpus_id: str | None = None,
) -> dict:
    """Run a full-text search query via rag.fts_search RPC."""
    params = {
        "p_query": query,
        "p_top_k": 5,
    }
    if corpus_id:
        params["p_corpus_id"] = corpus_id

    return rpc_call(
        "fts_search",
        params,
        supabase_url=supabase_url,
        service_key=service_key,
    )


def run_smoke_test(
    queries: list[dict],
    *,
    supabase_url: str,
    service_key: str,
    fts_only: bool = True,
) -> list[dict]:
    """Run all smoke queries and collect results."""
    results = []

    for q in queries:
        qid = q["id"]
        query = q["query"]
        min_results = q.get("min_results", 1)
        expected_corpus = q.get("expected_corpus")

        print(f"\n  {qid}: \"{query}\"")

        resp = run_fts_query(
            query,
            supabase_url=supabase_url,
            service_key=service_key,
        )

        if resp["status"] == "error":
            print(f"    ERROR: {resp.get('error', 'unknown')[:200]}")
            results.append({
                "id": qid,
                "query": query,
                "status": "ERROR",
                "error": resp.get("error", "unknown")[:200],
            })
            continue

        hits = resp.get("results", [])
        hit_count = len(hits)
        passed = hit_count >= min_results

        # Check if expected corpus is in results
        corpus_match = False
        if expected_corpus and hits:
            corpus_match = any(
                h.get("corpus_id") == expected_corpus for h in hits
            )

        status = "PASS" if passed else "FAIL"
        print(f"    {status}: {hit_count} results (min={min_results})")
        if hits:
            for h in hits[:3]:
                path = h.get("repo_path", h.get("section_path", "?"))
                score = h.get("ts_score", 0)
                print(f"    - [{score:.4f}] {path}")

        results.append({
            "id": qid,
            "query": query,
            "status": status,
            "hit_count": hit_count,
            "min_required": min_results,
            "corpus_match": corpus_match,
            "top_hits": [
                {
                    "repo_path": h.get("repo_path"),
                    "corpus_id": h.get("corpus_id"),
                    "score": h.get("ts_score", 0),
                    "content_preview": h.get("content", "")[:100],
                }
                for h in (hits or [])[:3]
            ],
        })

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test RAG hybrid search RPCs")
    parser.add_argument("--query", type=str, help="Run a single custom query")
    parser.add_argument(
        "--fts-only",
        action="store_true",
        default=True,
        help="Use FTS search only (default, no embeddings needed)",
    )
    parser.add_argument("--output", type=str, help="Write results JSON to this path")
    args = parser.parse_args()

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        print("Set these environment variables and re-run.")
        return 1

    if args.query:
        queries = [
            {
                "id": "CUSTOM-001",
                "query": args.query,
                "min_results": 1,
            }
        ]
    else:
        queries = SMOKE_QUERIES

    print(f"Running {len(queries)} smoke queries against {supabase_url}...")
    results = run_smoke_test(
        queries,
        supabase_url=supabase_url,
        service_key=service_key,
        fts_only=args.fts_only,
    )

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n{'='*60}")
    print(f"Smoke Test: {passed}/{len(results)} PASS, {failed} FAIL, {errors} ERROR")

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "supabase_url": supabase_url.split(".")[0].replace("https://", "***"),
                    "total_queries": len(results),
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "results": results,
                },
                f,
                indent=2,
            )
        print(f"Results written to: {args.output}")

    return 0 if (failed + errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
