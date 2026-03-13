#!/usr/bin/env python3
"""
Knowledge Graph Generator for Odoo Repository

Generates DOT/SVG/PNG graph from:
- docs/knowledge/graph_seed.json (318 pre-structured nodes)
- Markdown link analysis (docs/*.md, spec/*.md)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).parent.parent.parent
GRAPH_SEED = REPO_ROOT / "docs/knowledge/graph_seed.json"
DOCS_DIR = REPO_ROOT / "docs"
SPEC_DIR = REPO_ROOT / "spec"
OUTPUT_DIR = REPO_ROOT / "out/graphs/knowledge"

# Node type colors (for visual distinction)
NODE_COLORS = {
    "Repo": "#e3f2fd",
    "SpecBundle": "#fff3e0",
    "Module": "#f3e5f5",
    "Workflow": "#e8f5e9",
    "Script": "#fce4ec",
    "Doc": "#f1f8e9",
    "Service": "#e0f2f1",
    "Integration": "#fff9c4",
}


def load_graph_seed() -> Dict:
    """Load base graph structure from graph_seed.json"""
    if not GRAPH_SEED.exists():
        print(f"ERROR: Graph seed not found: {GRAPH_SEED}")
        sys.exit(1)

    with open(GRAPH_SEED) as f:
        data = json.load(f)

    print(f"Loaded {len(data.get('nodes', []))} nodes from graph seed")
    return data


def scan_markdown_links() -> Dict[str, List[str]]:
    """
    Scan all markdown files for internal links [text](path.md)
    Returns: {source_file: [target_files]}
    """
    links = {}
    markdown_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)')

    for base_dir in [DOCS_DIR, SPEC_DIR]:
        if not base_dir.exists():
            continue

        for md_file in base_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                matches = markdown_pattern.findall(content)

                if matches:
                    rel_path = str(md_file.relative_to(REPO_ROOT))
                    targets = []

                    for _, target in matches:
                        # Resolve relative paths
                        if target.startswith('http'):
                            continue  # Skip external links

                        target_path = (md_file.parent / target).resolve()
                        if target_path.exists():
                            targets.append(str(target_path.relative_to(REPO_ROOT)))

                    if targets:
                        links[rel_path] = targets

            except Exception as e:
                print(f"Warning: Error reading {md_file}: {e}")

    print(f"Found {len(links)} markdown files with internal links")
    total_links = sum(len(targets) for targets in links.values())
    print(f"Total link edges: {total_links}")

    return links


def build_dot_graph(nodes: List[Dict], links: Dict[str, List[str]]) -> str:
    """
    Generate Graphviz DOT format graph
    - Nodes from graph_seed.json
    - Edges from markdown links
    - Clustering by node type
    """
    dot_lines = [
        'digraph knowledge_graph {',
        '  graph [rankdir=LR, fontname="Arial", fontsize=10];',
        '  node [shape=box, style=filled, fontname="Arial", fontsize=9];',
        '  edge [color="#999999", penwidth=0.5];',
        ''
    ]

    # Group nodes by kind for clustering
    nodes_by_kind: Dict[str, List[Dict]] = {}
    for node in nodes:
        kind = node.get('kind', 'Unknown')
        if kind not in nodes_by_kind:
            nodes_by_kind[kind] = []
        nodes_by_kind[kind].append(node)

    # Create subgraphs (clusters) for each node type
    for kind, kind_nodes in sorted(nodes_by_kind.items()):
        color = NODE_COLORS.get(kind, "#ffffff")
        dot_lines.append(f'  subgraph cluster_{kind} {{')
        dot_lines.append(f'    label="{kind} ({len(kind_nodes)})";')
        dot_lines.append('    style=filled;')
        dot_lines.append('    color=lightgrey;')
        dot_lines.append('')

        for node in kind_nodes:
            node_id = node.get('id', '').replace('/', '_').replace('.', '_')
            label = node.get('name', node_id)

            # Escape quotes in label
            label = label.replace('"', '\\"')

            dot_lines.append(
                f'    "{node_id}" [label="{label}", fillcolor="{color}"];'
            )

        dot_lines.append('  }')
        dot_lines.append('')

    # Add edges from markdown links
    dot_lines.append('  // Edges from markdown links')
    processed_edges: Set[Tuple[str, str]] = set()

    for source, targets in links.items():
        source_id = source.replace('/', '_').replace('.', '_')

        for target in targets:
            target_id = target.replace('/', '_').replace('.', '_')
            edge = (source_id, target_id)

            if edge not in processed_edges:
                dot_lines.append(f'  "{source_id}" -> "{target_id}";')
                processed_edges.add(edge)

    dot_lines.append('}')
    return '\n'.join(dot_lines)


def render_graphviz(dot_content: str, output_path: Path, fmt: str = "svg"):
    """Render DOT to SVG/PNG using Graphviz"""
    try:
        result = subprocess.run(
            ["dot", f"-T{fmt}", "-o", str(output_path)],
            input=dot_content.encode('utf-8'),
            capture_output=True,
            check=True
        )
        print(f"Generated {fmt.upper()}: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Graphviz rendering failed")
        print(f"stderr: {e.stderr.decode()}")
        sys.exit(1)


def main():
    """Main execution"""
    print("==> Generating Knowledge Graph")
    print()

    # Check dependencies
    try:
        subprocess.run(["dot", "-V"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Graphviz 'dot' command not found")
        print("Install with: brew install graphviz")
        sys.exit(1)

    # Load base graph structure
    graph_data = load_graph_seed()
    nodes = graph_data.get('nodes', [])

    # Scan markdown for links
    print()
    print("==> Scanning markdown files for links")
    links = scan_markdown_links()

    # Build DOT graph
    print()
    print("==> Building DOT graph")
    dot_content = build_dot_graph(nodes, links)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save DOT file
    dot_path = OUTPUT_DIR / "knowledge_graph.dot"
    dot_path.write_text(dot_content, encoding='utf-8')
    print(f"Saved DOT file: {dot_path}")

    # Render to SVG and PNG
    print()
    print("==> Rendering with Graphviz")
    render_graphviz(dot_content, OUTPUT_DIR / "knowledge_graph.svg", "svg")
    render_graphviz(dot_content, OUTPUT_DIR / "knowledge_graph.png", "png")

    print()
    print("✅ Knowledge graph generated successfully!")
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"  - DOT: knowledge_graph.dot")
    print(f"  - SVG: knowledge_graph.svg")
    print(f"  - PNG: knowledge_graph.png")


if __name__ == "__main__":
    main()
