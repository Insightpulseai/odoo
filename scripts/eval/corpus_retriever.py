#!/usr/bin/env python3
"""Corpus retriever for SSOT document search.

Reads ssot/knowledge/corpus_registry.yaml, scans matching files in the repo,
and returns citations with file paths and content snippets.

This is a batch/eval retriever (local filesystem search), not a production
vector search.  Production RAG uses Supabase pgvector via the IPAI bridge.

Scoring: BM25 with IDF + path/filename boost + exact phrase matching.

Usage (standalone):
    python scripts/eval/corpus_retriever.py "What are the copilot rules?"

Usage (library):
    from scripts.eval.corpus_retriever import retrieve
    results = retrieve("What are the copilot rules?", top_k=5)
"""
from __future__ import annotations

import fnmatch
import glob
import math
import os
import re
import sys
from collections import Counter
from typing import NamedTuple

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # scripts/eval/ -> repo root
REGISTRY_PATH = os.path.join(REPO_ROOT, "ssot", "knowledge", "corpus_registry.yaml")


class Citation(NamedTuple):
    """A single citation result from corpus retrieval."""
    path: str          # repo-relative file path
    score: float       # relevance score
    snippet: str       # content excerpt
    line_start: int    # first line of snippet (1-based)
    line_end: int      # last line of snippet (1-based)
    corpus_id: str     # which corpus this came from


def _load_corpora(registry_path: str = REGISTRY_PATH) -> list[dict]:
    """Load corpus definitions from the registry YAML."""
    with open(registry_path) as f:
        data = yaml.safe_load(f)
    return data.get("corpora", [])


def _glob_corpus_files(corpus: dict) -> list[str]:
    """Glob files for a single corpus entry. Returns repo-relative paths."""
    include = corpus.get("include_patterns", [])
    exclude = corpus.get("exclude_patterns", [])
    path_glob = corpus["path"]

    patterns = include if include else [path_glob]
    matched: set[str] = set()

    for pattern in patterns:
        full_pattern = os.path.join(REPO_ROOT, pattern)
        for fpath in glob.glob(full_pattern, recursive=True):
            if os.path.isfile(fpath):
                rel = os.path.relpath(fpath, REPO_ROOT)
                excluded = any(fnmatch.fnmatch(rel, exc) for exc in exclude)
                if not excluded:
                    matched.add(rel)

    return sorted(matched)


def _tokenize(text: str) -> list[str]:
    """Extract lowercase alpha tokens from text."""
    return [w.lower() for w in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text) if len(w) > 2]


def _compute_idf(all_files_tokens: list[set[str]]) -> dict[str, float]:
    """Compute IDF for each token across all corpus files."""
    n = len(all_files_tokens)
    if n == 0:
        return {}

    doc_freq: Counter = Counter()
    for tokens in all_files_tokens:
        for t in tokens:
            doc_freq[t] += 1

    idf: dict[str, float] = {}
    for term, df in doc_freq.items():
        # BM25 IDF: log((N - df + 0.5) / (df + 0.5) + 1)
        idf[term] = math.log((n - df + 0.5) / (df + 0.5) + 1.0)

    return idf


def _score_file_bm25(
    query_tokens: list[str],
    doc_tokens: list[str],
    idf: dict[str, float],
    avg_dl: float,
) -> float:
    """Score a file's relevance using BM25 with IDF."""
    if not query_tokens or not doc_tokens:
        return 0.0

    doc_freq = Counter(doc_tokens)
    doc_len = len(doc_tokens)

    k1 = 1.5
    b = 0.75

    score = 0.0
    for qt in set(query_tokens):
        tf = doc_freq.get(qt, 0)
        if tf == 0:
            continue
        term_idf = idf.get(qt, 0.5)  # default low IDF for unseen terms
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * doc_len / avg_dl)
        score += term_idf * (numerator / denominator)

    return score


def _path_boost(query_tokens: list[str], rel_path: str) -> float:
    """Compute a boost score based on query token matches in the file path.

    Path matching is critical: if query says "release contract" and the file
    is ssot/runtime/release_contract.yaml, that's a strong signal.
    """
    # Tokenize the path (split on / _ - .)
    path_parts = re.findall(r"[a-zA-Z][a-zA-Z0-9]*", rel_path.lower())
    if not path_parts:
        return 0.0

    path_set = set(path_parts)
    query_set = set(query_tokens)

    # Count overlapping tokens between query and path
    overlap = path_set & query_set
    if not overlap:
        return 0.0

    # More overlap = stronger boost; normalize by query token count.
    # Path matching is a very strong signal — multiplier must dominate
    # over content-only BM25 scores (typically 8-20).
    return len(overlap) / len(query_set) * 15.0


def _exact_phrase_boost(query: str, content: str) -> float:
    """Boost for exact multi-word phrases from the query appearing in content.

    Extract 2-3 word phrases from query and check for exact substring matches.
    """
    query_lower = query.lower()
    content_lower = content.lower()

    words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", query_lower)
    if len(words) < 2:
        return 0.0

    boost = 0.0
    # Check bigrams
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        # Also check underscore variant (e.g., "release_contract")
        underscore = f"{words[i]}_{words[i+1]}"
        if bigram in content_lower:
            boost += 0.5
        if underscore in content_lower:
            boost += 0.5

    # Check trigrams
    for i in range(len(words) - 2):
        trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
        if trigram in content_lower:
            boost += 0.8

    return min(boost, 3.0)  # cap


def _extract_snippet(query_tokens: list[str], lines: list[str], context: int = 3) -> tuple[str, int, int]:
    """Find the best snippet window around query term matches."""
    if not lines:
        return "", 1, 1

    # Score each line
    line_scores: list[float] = []
    for line in lines:
        tokens = set(_tokenize(line.lower()))
        overlap = len(tokens & set(query_tokens))
        line_scores.append(overlap)

    # Find the best window
    best_start = 0
    best_score = 0
    window = 2 * context + 1

    for i in range(len(lines)):
        end = min(i + window, len(lines))
        window_score = sum(line_scores[i:end])
        if window_score > best_score:
            best_score = window_score
            best_start = i

    start = best_start
    end = min(best_start + window, len(lines))
    snippet = "\n".join(lines[start:end])

    # Truncate long snippets
    if len(snippet) > 500:
        snippet = snippet[:497] + "..."

    return snippet, start + 1, end


def retrieve(
    query: str,
    corpus_ids: list[str] | None = None,
    top_k: int = 5,
    registry_path: str = REGISTRY_PATH,
) -> list[Citation]:
    """
    Search registered corpora for content matching query.

    Uses BM25 with IDF + path boost + exact phrase matching for scoring.

    Args:
        query: Natural language search query
        corpus_ids: Optional filter to specific corpora (None = all)
        top_k: Maximum number of results to return
        registry_path: Path to corpus_registry.yaml

    Returns:
        List of Citation objects sorted by relevance score (descending)
    """
    corpora = _load_corpora(registry_path)
    query_tokens = _tokenize(query)

    if not query_tokens:
        return []

    # Phase 1: Load all corpus files and compute IDF
    file_records: list[dict] = []
    all_files_token_sets: list[set[str]] = []

    for corpus in corpora:
        cid = corpus["id"]
        if corpus_ids and cid not in corpus_ids:
            continue

        files = _glob_corpus_files(corpus)

        for rel_path in files:
            abs_path = os.path.join(REPO_ROOT, rel_path)
            try:
                with open(abs_path, encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue

            doc_tokens = _tokenize(content.lower())
            token_set = set(doc_tokens)
            all_files_token_sets.append(token_set)
            file_records.append({
                "path": rel_path,
                "content": content,
                "doc_tokens": doc_tokens,
                "corpus_id": cid,
            })

    if not file_records:
        return []

    # Compute IDF across all corpus files
    idf = _compute_idf(all_files_token_sets)

    # Average document length
    total_tokens = sum(len(r["doc_tokens"]) for r in file_records)
    avg_dl = total_tokens / len(file_records)

    # Phase 2: Score each file
    results: list[Citation] = []

    for rec in file_records:
        bm25_score = _score_file_bm25(query_tokens, rec["doc_tokens"], idf, avg_dl)

        # Skip very low BM25 scores early
        if bm25_score < 0.1:
            # Still check path boost — some files match purely on path
            pb = _path_boost(query_tokens, rec["path"])
            if pb < 1.0:
                continue

        # Add path and phrase boosts
        pb = _path_boost(query_tokens, rec["path"])
        phrase_boost = _exact_phrase_boost(query, rec["content"])

        # Combined score: BM25 + path boost + phrase boost
        combined = bm25_score + pb + phrase_boost

        lines = rec["content"].splitlines()
        snippet, line_start, line_end = _extract_snippet(query_tokens, lines)

        results.append(Citation(
            path=rec["path"],
            score=round(combined, 4),
            snippet=snippet,
            line_start=line_start,
            line_end=line_end,
            corpus_id=rec["corpus_id"],
        ))

    # Sort by score descending, take top_k
    results.sort(key=lambda c: c.score, reverse=True)
    return results[:top_k]


def main():
    """CLI entrypoint for ad-hoc corpus search."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/eval/corpus_retriever.py <query> [top_k]")
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    results = retrieve(query, top_k=top_k)

    if not results:
        print(f"No results for: {query!r}")
        sys.exit(0)

    print(f"Query: {query!r}")
    print(f"Results: {len(results)}")
    print()

    for i, cit in enumerate(results, 1):
        print(f"  [{i}] {cit.path} (score={cit.score}, lines {cit.line_start}-{cit.line_end})")
        print(f"      corpus: {cit.corpus_id}")
        # Show first line of snippet
        first_line = cit.snippet.split("\n")[0][:100]
        print(f"      snippet: {first_line}...")
        print()


if __name__ == "__main__":
    main()
