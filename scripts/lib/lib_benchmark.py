#!/usr/bin/env python3
"""
LIB Performance Benchmark Script

Tests LIB performance across core operations:
- Database initialization
- File scanning (1K, 5K, 10K files)
- Metadata search queries
- FTS5 content search
- Concurrent access patterns

Usage:
    python3 lib_benchmark.py --db-path .lib/bench.db --scan-root /path/to/test/files

Requirements:
    - Python 3.12+
    - aiosqlite
    - Test directory with files for scanning
"""

import asyncio
import time
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Any
import aiosqlite

# Add lib modules to path
sys.path.insert(0, str(Path(__file__).parent))

from lib_db import init_database, search_files, fts_search, get_file_by_path
from lib_scan import scan_repository


class BenchmarkResults:
    """Store and format benchmark results"""

    def __init__(self):
        self.results: Dict[str, Any] = {}

    def add(self, name: str, duration: float, operations: int = 1, metadata: Dict = None):
        """Add benchmark result"""
        ops_per_sec = operations / duration if duration > 0 else 0
        self.results[name] = {
            "duration_sec": round(duration, 3),
            "operations": operations,
            "ops_per_sec": round(ops_per_sec, 1),
            "metadata": metadata or {}
        }

    def print_summary(self):
        """Print formatted benchmark summary"""
        print("\n" + "=" * 80)
        print("LIB PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)

        for name, data in self.results.items():
            print(f"\n{name}:")
            print(f"  Duration:     {data['duration_sec']}s")
            print(f"  Operations:   {data['operations']}")
            print(f"  Throughput:   {data['ops_per_sec']} ops/sec")

            if data['metadata']:
                print("  Metadata:")
                for k, v in data['metadata'].items():
                    print(f"    {k}: {v}")

        print("\n" + "=" * 80)


async def benchmark_init(db_path: Path, results: BenchmarkResults):
    """Benchmark database initialization"""
    print("⏱️  Benchmarking database initialization...")

    # Clean up existing database
    if db_path.exists():
        db_path.unlink()

    start = time.time()
    await init_database(db_path)
    duration = time.time() - start

    results.add("Database Initialization", duration)


async def benchmark_scan(db_path: Path, scan_root: Path, results: BenchmarkResults):
    """Benchmark filesystem scanning"""
    print(f"⏱️  Benchmarking filesystem scan: {scan_root}")

    start = time.time()
    stats = await scan_repository([scan_root], db_path, verbose=False)
    duration = time.time() - start

    results.add(
        f"Filesystem Scan ({stats['scanned']} files)",
        duration,
        operations=stats['scanned'],
        metadata={
            "files_new": stats['new'],
            "files_updated": stats['updated'],
            "files_deleted": stats['deleted']
        }
    )


async def benchmark_metadata_search(db_path: Path, results: BenchmarkResults):
    """Benchmark metadata search queries"""
    print("⏱️  Benchmarking metadata search...")

    async with aiosqlite.connect(str(db_path)) as db:
        # Test 1: Extension filter
        start = time.time()
        py_files = await search_files(db, ext=".py", limit=1000)
        duration1 = time.time() - start

        # Test 2: Path pattern
        start = time.time()
        lib_files = await search_files(db, query="lib", limit=1000)
        duration2 = time.time() - start

        # Test 3: MIME type
        start = time.time()
        text_files = await search_files(db, mime="text/plain", limit=1000)
        duration3 = time.time() - start

        avg_duration = statistics.mean([duration1, duration2, duration3])

        results.add(
            "Metadata Search (3 queries avg)",
            avg_duration,
            operations=3,
            metadata={
                "ext_filter_ms": round(duration1 * 1000, 1),
                "path_pattern_ms": round(duration2 * 1000, 1),
                "mime_filter_ms": round(duration3 * 1000, 1),
                "results": {
                    "py_files": len(py_files),
                    "lib_files": len(lib_files),
                    "text_files": len(text_files)
                }
            }
        )


async def benchmark_fts_search(db_path: Path, results: BenchmarkResults):
    """Benchmark FTS5 full-text search"""
    print("⏱️  Benchmarking FTS5 search...")

    async with aiosqlite.connect(str(db_path)) as db:
        # Test queries
        queries = [
            "def scan_repository",
            "async def",
            "import",
            "return",
            "class"
        ]

        durations = []
        result_counts = []

        for query in queries:
            start = time.time()
            results_list = await fts_search(db, query, limit=100)
            duration = time.time() - start
            durations.append(duration)
            result_counts.append(len(results_list))

        avg_duration = statistics.mean(durations)

        results.add(
            f"FTS5 Search ({len(queries)} queries avg)",
            avg_duration,
            operations=len(queries),
            metadata={
                "avg_latency_ms": round(avg_duration * 1000, 1),
                "min_latency_ms": round(min(durations) * 1000, 1),
                "max_latency_ms": round(max(durations) * 1000, 1),
                "avg_results": round(statistics.mean(result_counts), 1)
            }
        )


async def benchmark_concurrent_access(db_path: Path, results: BenchmarkResults):
    """Benchmark concurrent database access (WAL mode benefit)"""
    print("⏱️  Benchmarking concurrent access...")

    async def concurrent_reader(db: aiosqlite.Connection, query_id: int):
        """Concurrent read operation"""
        for _ in range(10):
            await search_files(db, ext=".py", limit=100)

    async with aiosqlite.connect(str(db_path)) as db:
        start = time.time()

        # Run 5 concurrent readers
        tasks = [concurrent_reader(db, i) for i in range(5)]
        await asyncio.gather(*tasks)

        duration = time.time() - start

        results.add(
            "Concurrent Access (5 readers × 10 ops)",
            duration,
            operations=50,
            metadata={
                "avg_latency_ms": round(duration * 1000 / 50, 1),
                "concurrency_level": 5
            }
        )


async def benchmark_get_file_by_path(db_path: Path, results: BenchmarkResults):
    """Benchmark single file lookup performance"""
    print("⏱️  Benchmarking file lookup by path...")

    async with aiosqlite.connect(str(db_path)) as db:
        # Get first file path for testing
        cursor = await db.execute("SELECT path FROM lib_files WHERE deleted_at IS NULL LIMIT 1")
        row = await cursor.fetchone()

        if not row:
            print("  ⚠️  No files in database, skipping...")
            return

        test_path = row[0]

        # Run 1000 lookups
        start = time.time()
        for _ in range(1000):
            await get_file_by_path(db, test_path)
        duration = time.time() - start

        results.add(
            "File Lookup by Path (1000 ops)",
            duration,
            operations=1000,
            metadata={
                "avg_latency_ms": round(duration * 1000 / 1000, 2)
            }
        )


async def main():
    """Run all benchmarks"""
    import argparse

    parser = argparse.ArgumentParser(description="LIB Performance Benchmark")
    parser.add_argument("--db-path", type=Path, default=Path(".lib/bench.db"),
                       help="Path to benchmark database (will be recreated)")
    parser.add_argument("--scan-root", type=Path, required=True,
                       help="Root directory for scanning benchmark")
    args = parser.parse_args()

    if not args.scan_root.exists():
        print(f"❌ Error: Scan root does not exist: {args.scan_root}")
        sys.exit(1)

    results = BenchmarkResults()

    print(f"\n🚀 Starting LIB Performance Benchmark")
    print(f"   Database: {args.db_path}")
    print(f"   Scan root: {args.scan_root}\n")

    try:
        # Run benchmarks
        await benchmark_init(args.db_path, results)
        await benchmark_scan(args.db_path, args.scan_root, results)
        await benchmark_metadata_search(args.db_path, results)
        await benchmark_fts_search(args.db_path, results)
        await benchmark_get_file_by_path(args.db_path, results)
        await benchmark_concurrent_access(args.db_path, results)

        # Print summary
        results.print_summary()

        print("\n✅ Benchmark complete!")
        print(f"   Database: {args.db_path}")
        print(f"   Size: {args.db_path.stat().st_size / 1024:.1f} KB\n")

    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
