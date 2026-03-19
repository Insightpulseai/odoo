#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagramflow CLI.

Convert Mermaid diagrams to BPMN and draw.io formats.
"""
import argparse
import sys
from pathlib import Path

from .parser import MermaidParser
from .bpmn import BPMNGenerator
from .drawio import DrawIOGenerator


def main():
    """Main CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Convert Mermaid diagrams to BPMN/draw.io",
        prog="diagramflow",
    )
    ap.add_argument(
        "input",
        type=Path,
        help="Input Mermaid file (.mmd)",
    )
    ap.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (default: input with new extension)",
    )
    ap.add_argument(
        "-f", "--format",
        choices=["bpmn", "drawio", "both"],
        default="both",
        help="Output format (default: both)",
    )
    ap.add_argument(
        "-d", "--output-dir",
        type=Path,
        help="Output directory (default: same as input)",
    )
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Parse Mermaid
    source = args.input.read_text("utf-8")
    parser = MermaidParser()
    chart = parser.parse(source)

    # Determine output directory
    output_dir = args.output_dir or args.input.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = args.input.stem

    # Generate outputs
    if args.format in ("bpmn", "both"):
        bpmn_path = output_dir / f"{stem}.bpmn"
        bpmn_gen = BPMNGenerator()
        bpmn_gen.save(chart, str(bpmn_path))
        print(f"Generated: {bpmn_path}")

    if args.format in ("drawio", "both"):
        drawio_path = output_dir / f"{stem}.drawio"
        drawio_gen = DrawIOGenerator()
        drawio_gen.save(chart, str(drawio_path))
        print(f"Generated: {drawio_path}")


def mermaid_to_bpmn():
    """Convert Mermaid to BPMN only."""
    ap = argparse.ArgumentParser(
        description="Convert Mermaid to BPMN 2.0 XML",
        prog="mermaid2bpmn",
    )
    ap.add_argument("input", type=Path, help="Input Mermaid file")
    ap.add_argument("-o", "--output", type=Path, help="Output BPMN file")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    source = args.input.read_text("utf-8")
    parser = MermaidParser()
    chart = parser.parse(source)

    output = args.output or args.input.with_suffix(".bpmn")
    BPMNGenerator().save(chart, str(output))
    print(f"Generated: {output}")


def mermaid_to_drawio():
    """Convert Mermaid to draw.io only."""
    ap = argparse.ArgumentParser(
        description="Convert Mermaid to draw.io XML",
        prog="mermaid2drawio",
    )
    ap.add_argument("input", type=Path, help="Input Mermaid file")
    ap.add_argument("-o", "--output", type=Path, help="Output draw.io file")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    source = args.input.read_text("utf-8")
    parser = MermaidParser()
    chart = parser.parse(source)

    output = args.output or args.input.with_suffix(".drawio")
    DrawIOGenerator().save(chart, str(output))
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
