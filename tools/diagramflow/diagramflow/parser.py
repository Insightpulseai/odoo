# -*- coding: utf-8 -*-
"""
Mermaid flowchart parser.

Parses Mermaid flowchart syntax into an intermediate representation
that can be converted to BPMN or draw.io format.
"""
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    """A node in the flowchart."""
    id: str
    label: str
    shape: str = "rect"  # rect, diamond, circle, stadium, subroutine
    style: Optional[str] = None


@dataclass
class Edge:
    """An edge connecting two nodes."""
    source: str
    target: str
    label: Optional[str] = None
    style: str = "solid"  # solid, dotted


@dataclass
class Subgraph:
    """A subgraph container."""
    id: str
    label: str
    nodes: list = field(default_factory=list)


@dataclass
class FlowChart:
    """Parsed flowchart structure."""
    direction: str = "TB"  # TB, BT, LR, RL
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    subgraphs: list = field(default_factory=list)


class MermaidParser:
    """Parse Mermaid flowchart syntax."""

    # Node shape patterns
    SHAPE_PATTERNS = [
        (r"\[\[(.+?)\]\]", "subroutine"),    # [[text]]
        (r"\[/(.+?)/\]", "parallelogram"),   # [/text/]
        (r"\(\((.+?)\)\)", "circle"),        # ((text))
        (r"\((.+?)\)", "stadium"),           # (text)
        (r"\{(.+?)\}", "diamond"),           # {text}
        (r"\[(.+?)\]", "rect"),              # [text]
    ]

    # Edge patterns
    EDGE_PATTERNS = [
        (r"-->\|(.+?)\|", "solid", True),     # -->|label|
        (r"-\.->", "dotted", False),          # -.->
        (r"-->", "solid", False),             # -->
        (r"---", "line", False),              # ---
    ]

    def __init__(self):
        self.chart = FlowChart()

    def parse(self, source: str) -> FlowChart:
        """Parse Mermaid source into FlowChart structure."""
        self.chart = FlowChart()
        lines = source.strip().split("\n")

        current_subgraph = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith("%%"):
                continue

            # Direction
            if line.startswith("flowchart") or line.startswith("graph"):
                parts = line.split()
                if len(parts) > 1:
                    self.chart.direction = parts[1]
                continue

            # Subgraph start
            if line.startswith("subgraph"):
                match = re.match(r"subgraph\s+(\w+)\s*\[?(.+?)?\]?$", line)
                if match:
                    sg_id = match.group(1)
                    sg_label = match.group(2) or sg_id
                    current_subgraph = Subgraph(id=sg_id, label=sg_label)
                continue

            # Subgraph end
            if line == "end":
                if current_subgraph:
                    self.chart.subgraphs.append(current_subgraph)
                    current_subgraph = None
                continue

            # Style
            if line.startswith("style"):
                self._parse_style(line)
                continue

            # Class definition
            if line.startswith("classDef"):
                continue

            # Class assignment
            if line.startswith("class"):
                continue

            # Parse edge or node
            self._parse_line(line, current_subgraph)

        return self.chart

    def _parse_line(self, line: str, subgraph: Optional[Subgraph] = None):
        """Parse a line that may contain nodes and edges."""
        # Find edge pattern
        edge_match = None
        edge_style = "solid"
        has_label = False
        edge_label = None

        for pattern, style, labeled in self.EDGE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                edge_match = match
                edge_style = style
                has_label = labeled
                if has_label:
                    edge_label = match.group(1)
                break

        if edge_match:
            # Split into source and target
            parts = re.split(r"--[>.\-]|\|.+?\|", line, maxsplit=1)
            if len(parts) >= 2:
                source_part = parts[0].strip()
                # Handle chained edges
                remaining = line[edge_match.end():].strip()
                target_parts = re.split(r"-->|-.->|---", remaining, maxsplit=1)
                target_part = target_parts[0].strip()

                source_node = self._parse_node(source_part)
                target_node = self._parse_node(target_part)

                if source_node and target_node:
                    self.chart.nodes[source_node.id] = source_node
                    self.chart.nodes[target_node.id] = target_node

                    if subgraph:
                        if source_node.id not in subgraph.nodes:
                            subgraph.nodes.append(source_node.id)
                        if target_node.id not in subgraph.nodes:
                            subgraph.nodes.append(target_node.id)

                    edge = Edge(
                        source=source_node.id,
                        target=target_node.id,
                        label=edge_label,
                        style=edge_style
                    )
                    self.chart.edges.append(edge)
        else:
            # Standalone node definition
            node = self._parse_node(line)
            if node:
                self.chart.nodes[node.id] = node
                if subgraph and node.id not in subgraph.nodes:
                    subgraph.nodes.append(node.id)

    def _parse_node(self, text: str) -> Optional[Node]:
        """Parse a node definition."""
        text = text.strip()
        if not text:
            return None

        # Extract ID and shape/label
        for pattern, shape in self.SHAPE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                label = match.group(1)
                # ID is everything before the shape
                id_part = text[:match.start()].strip()
                if not id_part:
                    id_part = re.sub(r"[^a-zA-Z0-9_]", "_", label)[:20]
                return Node(id=id_part, label=label, shape=shape)

        # No shape, just ID
        node_id = re.sub(r"[^a-zA-Z0-9_]", "_", text)
        return Node(id=node_id, label=text, shape="rect")

    def _parse_style(self, line: str):
        """Parse style definition."""
        match = re.match(r"style\s+(\w+)\s+(.+)", line)
        if match:
            node_id = match.group(1)
            style = match.group(2)
            if node_id in self.chart.nodes:
                self.chart.nodes[node_id].style = style
