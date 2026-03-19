# -*- coding: utf-8 -*-
"""
BPMN 2.0 XML generator.

Converts parsed Mermaid flowcharts to BPMN 2.0 XML format.
"""
import uuid
from xml.etree import ElementTree as ET
from typing import Dict

from .parser import FlowChart, Node, Edge


class BPMNGenerator:
    """Generate BPMN 2.0 XML from FlowChart."""

    BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
    DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
    DI_NS = "http://www.omg.org/spec/DD/20100524/DI"

    NAMESPACES = {
        "": BPMN_NS,
        "bpmndi": BPMNDI_NS,
        "dc": DC_NS,
        "di": DI_NS,
    }

    # Map Mermaid shapes to BPMN elements
    SHAPE_MAP = {
        "rect": "task",
        "diamond": "exclusiveGateway",
        "circle": "startEvent",
        "stadium": "task",
        "subroutine": "subProcess",
        "parallelogram": "dataObject",
    }

    def __init__(self):
        for prefix, uri in self.NAMESPACES.items():
            if prefix:
                ET.register_namespace(prefix, uri)
            else:
                ET.register_namespace("", uri)

    def generate(self, chart: FlowChart) -> str:
        """Generate BPMN 2.0 XML string."""
        # Create root definitions element
        definitions = ET.Element(
            "definitions",
            {
                "xmlns": self.BPMN_NS,
                "xmlns:bpmndi": self.BPMNDI_NS,
                "xmlns:dc": self.DC_NS,
                "xmlns:di": self.DI_NS,
                "id": f"Definitions_{uuid.uuid4().hex[:8]}",
                "targetNamespace": "http://ipai.dev/bpmn",
            },
        )

        # Create process
        process_id = f"Process_{uuid.uuid4().hex[:8]}"
        process = ET.SubElement(
            definitions,
            "process",
            {"id": process_id, "isExecutable": "true"},
        )

        # Track element IDs for diagram
        element_ids: Dict[str, str] = {}

        # Add start event if no circle node
        has_start = any(n.shape == "circle" for n in chart.nodes.values())
        if not has_start and chart.nodes:
            start_id = f"StartEvent_{uuid.uuid4().hex[:8]}"
            ET.SubElement(process, "startEvent", {"id": start_id, "name": "Start"})
            element_ids["__start__"] = start_id

        # Add nodes
        for node_id, node in chart.nodes.items():
            bpmn_type = self.SHAPE_MAP.get(node.shape, "task")
            elem_id = f"{bpmn_type}_{uuid.uuid4().hex[:8]}"
            element_ids[node_id] = elem_id

            elem = ET.SubElement(process, bpmn_type, {"id": elem_id, "name": node.label})

            # Add incoming/outgoing refs later
            node._bpmn_elem = elem

        # Add end event
        end_id = f"EndEvent_{uuid.uuid4().hex[:8]}"
        ET.SubElement(process, "endEvent", {"id": end_id, "name": "End"})
        element_ids["__end__"] = end_id

        # Add sequence flows
        flow_ids: Dict[str, str] = {}
        for i, edge in enumerate(chart.edges):
            flow_id = f"Flow_{uuid.uuid4().hex[:8]}"
            source_ref = element_ids.get(edge.source, element_ids.get("__start__", ""))
            target_ref = element_ids.get(edge.target, element_ids.get("__end__", ""))

            if source_ref and target_ref:
                flow_attrs = {
                    "id": flow_id,
                    "sourceRef": source_ref,
                    "targetRef": target_ref,
                }
                if edge.label:
                    flow_attrs["name"] = edge.label
                ET.SubElement(process, "sequenceFlow", flow_attrs)
                flow_ids[f"{edge.source}->{edge.target}"] = flow_id

        # Create BPMN diagram
        diagram = ET.SubElement(
            definitions,
            f"{{{self.BPMNDI_NS}}}BPMNDiagram",
            {"id": f"BPMNDiagram_{uuid.uuid4().hex[:8]}"},
        )

        plane = ET.SubElement(
            diagram,
            f"{{{self.BPMNDI_NS}}}BPMNPlane",
            {"id": f"BPMNPlane_{uuid.uuid4().hex[:8]}", "bpmnElement": process_id},
        )

        # Add shapes for nodes
        x, y = 100, 100
        x_step = 200 if chart.direction in ("LR", "RL") else 0
        y_step = 100 if chart.direction in ("TB", "BT") else 0

        for node_id, elem_id in element_ids.items():
            if node_id.startswith("__"):
                continue

            shape = ET.SubElement(
                plane,
                f"{{{self.BPMNDI_NS}}}BPMNShape",
                {"id": f"Shape_{elem_id}", "bpmnElement": elem_id},
            )

            bounds = ET.SubElement(
                shape,
                f"{{{self.DC_NS}}}Bounds",
                {"x": str(x), "y": str(y), "width": "100", "height": "80"},
            )

            x += x_step
            y += y_step

        # Convert to string
        return ET.tostring(definitions, encoding="unicode", xml_declaration=True)

    def save(self, chart: FlowChart, path: str):
        """Save BPMN XML to file."""
        xml = self.generate(chart)
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
