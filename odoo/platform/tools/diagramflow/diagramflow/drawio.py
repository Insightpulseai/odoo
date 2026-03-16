# -*- coding: utf-8 -*-
"""
draw.io XML generator.

Converts parsed Mermaid flowcharts to draw.io/diagrams.net XML format.
"""
import base64
import urllib.parse
import zlib
from xml.etree import ElementTree as ET

from .parser import FlowChart, Node


class DrawIOGenerator:
    """Generate draw.io XML from FlowChart."""

    # Map Mermaid shapes to draw.io shapes
    SHAPE_MAP = {
        "rect": "rounded=0;whiteSpace=wrap;html=1;",
        "diamond": "rhombus;whiteSpace=wrap;html=1;",
        "circle": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;",
        "stadium": "rounded=1;whiteSpace=wrap;html=1;",
        "subroutine": "rounded=0;whiteSpace=wrap;html=1;strokeWidth=2;",
        "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;",
    }

    def __init__(self):
        pass

    def generate(self, chart: FlowChart) -> str:
        """Generate draw.io XML string."""
        # Create root mxfile element
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "modified": "2024-01-01T00:00:00.000Z",
                "agent": "diagramflow",
                "version": "21.0.0",
                "type": "device",
            },
        )

        diagram = ET.SubElement(
            mxfile,
            "diagram",
            {"id": "flowchart", "name": "Flowchart"},
        )

        mxGraphModel = ET.SubElement(
            diagram,
            "mxGraphModel",
            {
                "dx": "1000",
                "dy": "600",
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": "850",
                "pageHeight": "1100",
                "math": "0",
                "shadow": "0",
            },
        )

        root = ET.SubElement(mxGraphModel, "root")

        # Add required root cells
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        # Track cell IDs
        cell_ids = {}
        cell_counter = 2

        # Calculate positions
        x, y = 100, 50
        x_step = 180 if chart.direction in ("LR", "RL") else 0
        y_step = 120 if chart.direction in ("TB", "BT") else 0

        # Add nodes
        for node_id, node in chart.nodes.items():
            cell_id = str(cell_counter)
            cell_ids[node_id] = cell_id
            cell_counter += 1

            style = self.SHAPE_MAP.get(node.shape, self.SHAPE_MAP["rect"])

            # Create cell
            cell = ET.SubElement(
                root,
                "mxCell",
                {
                    "id": cell_id,
                    "value": node.label,
                    "style": style,
                    "vertex": "1",
                    "parent": "1",
                },
            )

            # Set geometry
            width = 120 if node.shape != "circle" else 60
            height = 60 if node.shape not in ("circle", "diamond") else 60

            ET.SubElement(
                cell,
                "mxGeometry",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": str(width),
                    "height": str(height),
                    "as": "geometry",
                },
            )

            x += x_step
            y += y_step

        # Add edges
        for edge in chart.edges:
            cell_id = str(cell_counter)
            cell_counter += 1

            source_id = cell_ids.get(edge.source)
            target_id = cell_ids.get(edge.target)

            if not source_id or not target_id:
                continue

            style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
            if edge.style == "dotted":
                style += "dashed=1;"

            cell_attrs = {
                "id": cell_id,
                "style": style,
                "edge": "1",
                "parent": "1",
                "source": source_id,
                "target": target_id,
            }
            if edge.label:
                cell_attrs["value"] = edge.label

            cell = ET.SubElement(root, "mxCell", cell_attrs)

            geometry = ET.SubElement(
                cell,
                "mxGeometry",
                {"relative": "1", "as": "geometry"},
            )

        return ET.tostring(mxfile, encoding="unicode", xml_declaration=True)

    def generate_compressed(self, chart: FlowChart) -> str:
        """Generate compressed draw.io format (for embedding)."""
        xml = self.generate(chart)
        # draw.io uses deflate + base64 + url encode
        compressed = zlib.compress(xml.encode("utf-8"), level=9)
        b64 = base64.b64encode(compressed).decode("ascii")
        return urllib.parse.quote(b64, safe="")

    def save(self, chart: FlowChart, path: str):
        """Save draw.io XML to file."""
        xml = self.generate(chart)
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
