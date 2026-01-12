#!/usr/bin/env python3
"""
Generate ERD in Graphviz DOT format from Odoo models.

This script parses Odoo model definitions and generates:
- DOT format for Graphviz
- SVG/PNG via Graphviz (if installed)
- DOT file for manual rendering

Usage:
    python scripts/generate_erd_graphviz.py
    python scripts/generate_erd_graphviz.py --format svg
    python scripts/generate_erd_graphviz.py --format png --filter ipai_
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import from existing generator
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_odoo_dbml import (
    ModelDef,
    TableDef,
    build_tables,
    collect_models,
    collect_stub_tables,
)


def generate_dot(
    tables: Dict[str, TableDef],
    refs: List[Tuple[str, str]],
    models: Dict[str, ModelDef],
    *,
    filter_prefix: Optional[str] = None,
    include_columns: bool = True,
    max_columns: int = 15,
) -> str:
    """Generate Graphviz DOT format ERD."""
    lines: List[str] = []
    lines.append("digraph ERD {")
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=record, fontsize=10, fontname=\"Helvetica\"];")
    lines.append("  edge [arrowsize=0.7, fontsize=8];")
    lines.append("  splines=ortho;")
    lines.append("  nodesep=0.5;")
    lines.append("  ranksep=1.0;")
    lines.append("")

    # Filter tables if prefix specified
    filtered_tables = tables
    if filter_prefix:
        filtered_tables = {
            k: v for k, v in tables.items() if k.startswith(filter_prefix)
        }

    # Track which tables we include for edges
    included_tables: Set[str] = set(filtered_tables.keys())

    # Add related tables (targets of refs from filtered tables)
    if filter_prefix:
        for source, target_model in refs:
            source_table = source.split(".")[0]
            if source_table in included_tables:
                target_table = target_model.replace(".", "_")
                if target_model in models and models[target_model].table:
                    target_table = models[target_model].table
                if target_table in tables:
                    included_tables.add(target_table)

    # Group by module/prefix for subgraphs
    prefixes: Dict[str, List[str]] = {}
    for table_name in sorted(included_tables):
        if table_name in tables:
            # Determine prefix for clustering
            if "_" in table_name:
                prefix = table_name.split("_")[0]
            else:
                prefix = "core"
            prefixes.setdefault(prefix, []).append(table_name)

    # Generate nodes
    for prefix, table_names in sorted(prefixes.items()):
        lines.append(f"  // {prefix} tables")
        for table_name in sorted(table_names):
            table = tables[table_name]
            if include_columns:
                # Build record label with columns
                field_strs: List[str] = []
                sorted_fields = sorted(table.fields.keys())
                displayed_fields = sorted_fields[:max_columns]
                truncated = len(sorted_fields) > max_columns

                for field_name in displayed_fields:
                    field_type = table.fields[field_name]
                    pk_mark = "+" if field_name == "id" else " "
                    field_strs.append(f"{pk_mark}{field_name}: {field_type}")

                if truncated:
                    remaining = len(sorted_fields) - max_columns
                    field_strs.append(f"  ... +{remaining} more")

                fields_label = "\\l".join(field_strs) + "\\l"
                label = f"{{{table_name}|{fields_label}}}"
            else:
                label = table_name

            # Color based on prefix
            color = "#e8f4f8"  # default light blue
            if table_name.startswith("ipai_"):
                color = "#e8f8e8"  # light green for IPAI
            elif table_name.startswith("res_") or table_name.startswith("ir_"):
                color = "#f8f8e8"  # light yellow for core
            elif "_rel" in table_name:
                color = "#f0f0f0"  # light gray for relation tables

            lines.append(f'  "{table_name}" [label="{label}", fillcolor="{color}", style=filled];')
        lines.append("")

    # Generate edges
    lines.append("  // Foreign key relationships")
    for source, target_model in sorted(refs):
        source_table, source_field = source.split(".")
        if source_table not in included_tables:
            continue

        target_table = target_model.replace(".", "_")
        if target_model in models and models[target_model].table:
            target_table = models[target_model].table

        if target_table not in included_tables:
            continue

        lines.append(f'  "{source_table}" -> "{target_table}" [label="{source_field}"];')

    lines.append("}")
    return "\n".join(lines)


def render_graphviz(dot_content: str, output_path: Path, fmt: str = "svg") -> bool:
    """Render DOT content to SVG/PNG using Graphviz."""
    try:
        result = subprocess.run(
            ["dot", f"-T{fmt}"],
            input=dot_content.encode("utf-8"),
            capture_output=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"Graphviz error: {result.stderr.decode()}", file=sys.stderr)
            return False
        output_path.write_bytes(result.stdout)
        return True
    except FileNotFoundError:
        print("Graphviz not installed. Install with: apt-get install graphviz", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("Graphviz rendering timed out", file=sys.stderr)
        return False


def check_graphviz() -> bool:
    """Check if Graphviz is available."""
    try:
        result = subprocess.run(["dot", "-V"], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ERD in Graphviz format")
    parser.add_argument(
        "--format",
        "-f",
        choices=["dot", "svg", "png", "all"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter tables by prefix (e.g., ipai_)",
    )
    parser.add_argument(
        "--no-columns",
        action="store_true",
        help="Don't include column details in nodes",
    )
    parser.add_argument(
        "--max-columns",
        type=int,
        default=15,
        help="Maximum columns to show per table (default: 15)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="docs/data-model",
        help="Output directory (default: docs/data-model)",
    )
    args = parser.parse_args()

    print("Collecting Odoo models...")
    models = collect_models()
    print(f"Found {len(models)} models")

    print("Building table definitions...")
    tables, refs = build_tables(models)
    collect_stub_tables(tables, refs, models)
    print(f"Generated {len(tables)} tables, {len(refs)} relationships")

    # Generate DOT content
    print("Generating DOT graph...")
    dot_content = generate_dot(
        tables,
        refs,
        models,
        filter_prefix=args.filter,
        include_columns=not args.no_columns,
        max_columns=args.max_columns,
    )

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine output filename
    suffix = f"_{args.filter.rstrip('_')}" if args.filter else ""

    # Write DOT file
    if args.format in ("dot", "all"):
        dot_path = output_dir / f"ODOO_ERD{suffix}.dot"
        dot_path.write_text(dot_content, encoding="utf-8")
        print(f"Written: {dot_path}")

    # Render to SVG/PNG if Graphviz available
    has_graphviz = check_graphviz()

    if args.format in ("svg", "all"):
        svg_path = output_dir / f"ODOO_ERD{suffix}.svg"
        if has_graphviz:
            if render_graphviz(dot_content, svg_path, "svg"):
                print(f"Written: {svg_path}")
        else:
            print("Skipping SVG (Graphviz not installed)")

    if args.format in ("png", "all"):
        png_path = output_dir / f"ODOO_ERD{suffix}.png"
        if has_graphviz:
            if render_graphviz(dot_content, png_path, "png"):
                print(f"Written: {png_path}")
        else:
            print("Skipping PNG (Graphviz not installed)")

    # Also generate filtered IPAI ERD
    if not args.filter:
        print("\nGenerating IPAI-only ERD...")
        ipai_dot = generate_dot(
            tables,
            refs,
            models,
            filter_prefix="ipai_",
            include_columns=not args.no_columns,
            max_columns=args.max_columns,
        )

        ipai_dot_path = output_dir / "ODOO_ERD_ipai.dot"
        ipai_dot_path.write_text(ipai_dot, encoding="utf-8")
        print(f"Written: {ipai_dot_path}")

        if has_graphviz:
            ipai_svg_path = output_dir / "ODOO_ERD_ipai.svg"
            if render_graphviz(ipai_dot, ipai_svg_path, "svg"):
                print(f"Written: {ipai_svg_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
