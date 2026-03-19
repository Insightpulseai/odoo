"""
CLI for org docs ingestion pipeline.

Usage:
    python -m packages.odoo_docs_kb.cli ingest --repo-root . --index org-docs
    python -m packages.odoo_docs_kb.cli ingest --incremental --since HEAD~5
    python -m packages.odoo_docs_kb.cli manifest --index org-docs
    python -m packages.odoo_docs_kb.cli discover --repo-root .
"""

import argparse
import json
import logging
import sys

from .ingest import OrgDocsIngestor
from .repo_loader import RepoDocsLoader
from .spec_loader import SpecBundleLoader


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_ingest(args):
    """Run ingestion pipeline."""
    config = {
        "index_name": args.index,
        "chunk_size_target": args.chunk_size,
        "chunk_overlap": args.chunk_overlap,
        "min_chunk_tokens": args.min_chunk,
    }

    ingestor = OrgDocsIngestor(repo_root=args.repo_root, config=config)

    stats = ingestor.ingest_all(
        incremental=args.incremental,
        since_commit=args.since,
        dry_run=args.dry_run,
    )

    print(json.dumps(stats, indent=2))
    return 0


def cmd_manifest(args):
    """Show current manifest."""
    ingestor = OrgDocsIngestor(repo_root=args.repo_root, config={"index_name": args.index})
    manifest = ingestor.get_manifest()
    print(json.dumps(manifest, indent=2))
    return 0


def cmd_discover(args):
    """Discover documentation files without ingesting."""
    loader = RepoDocsLoader(repo_root=args.repo_root)
    docs = loader.discover()

    spec_loader = SpecBundleLoader(repo_root=args.repo_root)
    bundles = spec_loader.discover()
    spec_docs = spec_loader.load_all()

    summary = {
        "repo_docs": {
            "count": len(docs),
            "files": [{"path": d.path, "type": d.doc_type, "hash": d.file_hash} for d in docs],
        },
        "spec_bundles": {
            "bundle_count": len(bundles),
            "doc_count": len(spec_docs),
            "bundles": [
                {"name": b["bundle_name"], "files": b["files"]}
                for b in bundles
            ],
        },
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Repo docs: {len(docs)} files")
        for doc in docs:
            print(f"  {doc.path} ({doc.doc_type}, {doc.file_hash[:8]})")
        print(f"\nSpec bundles: {len(bundles)} bundles, {len(spec_docs)} docs")
        for bundle in bundles:
            print(f"  {bundle['bundle_name']}/: {', '.join(bundle['files'])}")

    return 0


def cmd_eval(args):
    """Run retrieval evaluation on the org docs index."""
    try:
        from .eval import RetrievalEvaluator
    except ImportError:
        print("Error: eval module requires azure-search-documents", file=sys.stderr)
        return 1

    evaluator = RetrievalEvaluator(index_name=args.index, top_k=args.top_k)
    results = evaluator.run_eval()
    summary = evaluator.summary(results)
    print(json.dumps(summary, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="odoo-docs-kb",
        description="Org documentation ingestion and indexing pipeline",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest command
    p_ingest = subparsers.add_parser("ingest", help="Run ingestion pipeline")
    p_ingest.add_argument("--repo-root", default=".", help="Path to repo root")
    p_ingest.add_argument("--index", default="org-docs", help="Target index name")
    p_ingest.add_argument(
        "--incremental", action="store_true", default=True,
        help="Only process changed files (default)",
    )
    p_ingest.add_argument(
        "--full", action="store_true",
        help="Force full re-ingestion",
    )
    p_ingest.add_argument("--since", default=None, help="Git ref for incremental (e.g., HEAD~5)")
    p_ingest.add_argument("--dry-run", action="store_true", help="Chunk but don't embed/index")
    p_ingest.add_argument("--chunk-size", type=int, default=1500, help="Target chunk size in tokens")
    p_ingest.add_argument("--chunk-overlap", type=int, default=200, help="Overlap tokens")
    p_ingest.add_argument("--min-chunk", type=int, default=50, help="Minimum chunk tokens")
    p_ingest.set_defaults(func=cmd_ingest)

    # manifest command
    p_manifest = subparsers.add_parser("manifest", help="Show current manifest")
    p_manifest.add_argument("--repo-root", default=".", help="Path to repo root")
    p_manifest.add_argument("--index", default="org-docs", help="Index name")
    p_manifest.set_defaults(func=cmd_manifest)

    # discover command
    p_discover = subparsers.add_parser("discover", help="Discover docs without ingesting")
    p_discover.add_argument("--repo-root", default=".", help="Path to repo root")
    p_discover.add_argument("--json", action="store_true", help="Output as JSON")
    p_discover.set_defaults(func=cmd_discover)

    # eval command
    p_eval = subparsers.add_parser("eval", help="Run retrieval evaluation")
    p_eval.add_argument("--index", default="org-docs", help="Index name")
    p_eval.add_argument("--top-k", type=int, default=8, help="Top-K results")
    p_eval.set_defaults(func=cmd_eval)

    args = parser.parse_args()

    # Handle --full flag for ingest
    if args.command == "ingest" and args.full:
        args.incremental = False

    setup_logging(args.verbose)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
