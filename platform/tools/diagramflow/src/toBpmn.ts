/**
 * BPMN 2.0 XML Generator
 *
 * Converts MermaidModel to BPMN 2.0 XML format compatible with:
 * - SAP Signavio
 * - Camunda Modeler
 * - bpmn.io
 *
 * Includes BPMN DI (Diagram Interchange) for visual positioning.
 */

import type { MermaidModel, MermaidNode, MermaidEdge, NodeKind } from "./parseMermaid.js";

export interface BpmnOptions {
  /** Process ID (default: auto-generated) */
  processId?: string;
  /** Collaboration ID for multi-pool diagrams */
  collaborationId?: string;
  /** Target namespace */
  targetNamespace?: string;
  /** Include DI (diagram interchange) for visual positioning */
  includeDI?: boolean;
  /** Base X position for layout */
  baseX?: number;
  /** Base Y position for layout */
  baseY?: number;
  /** Horizontal spacing between nodes */
  nodeSpacingX?: number;
  /** Vertical spacing between lanes */
  laneSpacingY?: number;
}

const NS = {
  bpmn: "http://www.omg.org/spec/BPMN/20100524/MODEL",
  bpmndi: "http://www.omg.org/spec/BPMN/20100524/DI",
  dc: "http://www.omg.org/spec/DD/20100524/DC",
  di: "http://www.omg.org/spec/DD/20100524/DI",
  xsi: "http://www.w3.org/2001/XMLSchema-instance",
};

export function toBpmnXml(model: MermaidModel, options: BpmnOptions = {}): string {
  const {
    processId = generateId("Process"),
    collaborationId = generateId("Collaboration"),
    targetNamespace = "http://example.com/ipai/bpmn",
    includeDI = true,
    baseX = 160,
    baseY = 80,
    nodeSpacingX = 180,
    laneSpacingY = 150,
  } = options;

  const nodeById = new Map(model.nodes.map((n) => [n.id, n]));
  const nodePositions = calculatePositions(model, { baseX, baseY, nodeSpacingX, laneSpacingY });

  const lines: string[] = [];

  // XML declaration
  lines.push('<?xml version="1.0" encoding="UTF-8"?>');

  // Definitions root
  lines.push(`<bpmn:definitions
  xmlns:bpmn="${NS.bpmn}"
  xmlns:bpmndi="${NS.bpmndi}"
  xmlns:dc="${NS.dc}"
  xmlns:di="${NS.di}"
  xmlns:xsi="${NS.xsi}"
  id="Definitions_1"
  targetNamespace="${targetNamespace}"
  exporter="diagramflow"
  exporterVersion="1.0.0">`);

  // If multiple pools, create collaboration
  if (model.pools.length > 1) {
    lines.push(`  <bpmn:collaboration id="${collaborationId}">`);
    for (const pool of model.pools) {
      const participantId = `Participant_${sanitizeId(pool)}`;
      const poolProcessId = `Process_${sanitizeId(pool)}`;
      lines.push(`    <bpmn:participant id="${participantId}" name="${escXml(pool)}" processRef="${poolProcessId}"/>`);
    }
    // Message flows
    for (const edge of model.edges.filter((e) => e.kind === "message")) {
      const flowId = `MessageFlow_${edge.from}_${edge.to}`;
      lines.push(`    <bpmn:messageFlow id="${flowId}" sourceRef="${refId(edge.from, nodeById)}" targetRef="${refId(edge.to, nodeById)}"/>`);
    }
    lines.push("  </bpmn:collaboration>");
    lines.push("");
  }

  // Generate process(es)
  const pools = model.pools.length > 0 ? model.pools : ["Default"];
  for (const pool of pools) {
    const poolProcessId = model.pools.length > 1 ? `Process_${sanitizeId(pool)}` : processId;
    const poolNodes = model.nodes.filter((n) => n.pool === pool || (!n.pool && pool === "Default"));
    const poolEdges = model.edges.filter((e) => {
      if (e.kind === "message") return false;
      const fromNode = nodeById.get(e.from);
      const toNode = nodeById.get(e.to);
      return fromNode?.pool === pool || toNode?.pool === pool;
    });

    lines.push(`  <bpmn:process id="${poolProcessId}" isExecutable="false">`);

    // Lane set if we have lanes
    const poolLanes = model.lanes.get(pool) || [];
    if (poolLanes.length > 0) {
      lines.push(`    <bpmn:laneSet id="LaneSet_${sanitizeId(pool)}">`);
      for (const lane of poolLanes) {
        const laneId = `Lane_${sanitizeId(pool)}_${sanitizeId(lane)}`;
        const laneNodes = poolNodes.filter((n) => n.lane === lane);
        lines.push(`      <bpmn:lane id="${laneId}" name="${escXml(lane)}">`);
        for (const node of laneNodes) {
          lines.push(`        <bpmn:flowNodeRef>${refId(node.id, nodeById)}</bpmn:flowNodeRef>`);
        }
        lines.push("      </bpmn:lane>");
      }
      lines.push("    </bpmn:laneSet>");
    }

    // Flow nodes
    for (const node of poolNodes) {
      lines.push(generateFlowNode(node, model.edges, nodeById));
    }

    // Sequence flows
    for (const edge of poolEdges) {
      const flowId = `Flow_${edge.from}_${edge.to}`;
      const sourceRef = refId(edge.from, nodeById);
      const targetRef = refId(edge.to, nodeById);
      if (edge.label) {
        lines.push(`    <bpmn:sequenceFlow id="${flowId}" name="${escXml(edge.label)}" sourceRef="${sourceRef}" targetRef="${targetRef}"/>`);
      } else {
        lines.push(`    <bpmn:sequenceFlow id="${flowId}" sourceRef="${sourceRef}" targetRef="${targetRef}"/>`);
      }
    }

    lines.push("  </bpmn:process>");
    lines.push("");
  }

  // BPMN DI section
  if (includeDI) {
    lines.push(`  <bpmndi:BPMNDiagram id="BPMNDiagram_1">`);
    lines.push(`    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="${model.pools.length > 1 ? collaborationId : processId}">`);

    // Pool shapes
    if (model.pools.length > 1) {
      let poolY = baseY;
      for (const pool of model.pools) {
        const participantId = `Participant_${sanitizeId(pool)}`;
        const poolHeight = calculatePoolHeight(model, pool, laneSpacingY);
        lines.push(`      <bpmndi:BPMNShape id="${participantId}_di" bpmnElement="${participantId}" isHorizontal="true">`);
        lines.push(`        <dc:Bounds x="${baseX - 60}" y="${poolY}" width="1200" height="${poolHeight}"/>`);
        lines.push("      </bpmndi:BPMNShape>");
        poolY += poolHeight + 40;
      }
    }

    // Lane shapes
    for (const pool of pools) {
      const poolLanes = model.lanes.get(pool) || [];
      let laneY = nodePositions.get(model.nodes.find((n) => n.pool === pool)?.id || "")?.y || baseY;
      for (const lane of poolLanes) {
        const laneId = `Lane_${sanitizeId(pool)}_${sanitizeId(lane)}`;
        lines.push(`      <bpmndi:BPMNShape id="${laneId}_di" bpmnElement="${laneId}" isHorizontal="true">`);
        lines.push(`        <dc:Bounds x="${baseX - 30}" y="${laneY - 30}" width="1170" height="${laneSpacingY}"/>`);
        lines.push("      </bpmndi:BPMNShape>");
        laneY += laneSpacingY;
      }
    }

    // Node shapes
    for (const node of model.nodes) {
      const pos = nodePositions.get(node.id) || { x: baseX, y: baseY };
      const { width, height } = getNodeDimensions(node.kind);
      const elementId = refId(node.id, nodeById);
      lines.push(`      <bpmndi:BPMNShape id="${elementId}_di" bpmnElement="${elementId}">`);
      lines.push(`        <dc:Bounds x="${pos.x}" y="${pos.y}" width="${width}" height="${height}"/>`);
      if (node.label) {
        lines.push(`        <bpmndi:BPMNLabel/>`);
      }
      lines.push("      </bpmndi:BPMNShape>");
    }

    // Edge shapes
    for (const edge of model.edges) {
      const flowId = edge.kind === "message" ? `MessageFlow_${edge.from}_${edge.to}` : `Flow_${edge.from}_${edge.to}`;
      const fromPos = nodePositions.get(edge.from);
      const toPos = nodePositions.get(edge.to);
      if (fromPos && toPos) {
        const fromDim = getNodeDimensions(nodeById.get(edge.from)?.kind || "task");
        lines.push(`      <bpmndi:BPMNEdge id="${flowId}_di" bpmnElement="${flowId}">`);
        lines.push(`        <di:waypoint x="${fromPos.x + fromDim.width}" y="${fromPos.y + fromDim.height / 2}"/>`);
        lines.push(`        <di:waypoint x="${toPos.x}" y="${toPos.y + fromDim.height / 2}"/>`);
        lines.push("      </bpmndi:BPMNEdge>");
      }
    }

    lines.push("    </bpmndi:BPMNPlane>");
    lines.push("  </bpmndi:BPMNDiagram>");
  }

  lines.push("</bpmn:definitions>");

  return lines.join("\n");
}

function generateFlowNode(
  node: MermaidNode,
  edges: MermaidEdge[],
  nodeById: Map<string, MermaidNode>
): string {
  const elementId = refId(node.id, nodeById);
  const label = escXml(node.label);
  const incoming = edges.filter((e) => e.to === node.id && e.kind === "sequence");
  const outgoing = edges.filter((e) => e.from === node.id && e.kind === "sequence");

  const incomingRefs = incoming.map((e) => `      <bpmn:incoming>Flow_${e.from}_${e.to}</bpmn:incoming>`).join("\n");
  const outgoingRefs = outgoing.map((e) => `      <bpmn:outgoing>Flow_${e.from}_${e.to}</bpmn:outgoing>`).join("\n");
  const flowRefs = [incomingRefs, outgoingRefs].filter(Boolean).join("\n");

  switch (node.kind) {
    case "start":
      return flowRefs
        ? `    <bpmn:startEvent id="${elementId}" name="${label}">\n${flowRefs}\n    </bpmn:startEvent>`
        : `    <bpmn:startEvent id="${elementId}" name="${label}"/>`;

    case "end":
      return flowRefs
        ? `    <bpmn:endEvent id="${elementId}" name="${label}">\n${flowRefs}\n    </bpmn:endEvent>`
        : `    <bpmn:endEvent id="${elementId}" name="${label}"/>`;

    case "gateway":
      return flowRefs
        ? `    <bpmn:exclusiveGateway id="${elementId}" name="${label}">\n${flowRefs}\n    </bpmn:exclusiveGateway>`
        : `    <bpmn:exclusiveGateway id="${elementId}" name="${label}"/>`;

    case "timer":
      return flowRefs
        ? `    <bpmn:intermediateCatchEvent id="${elementId}" name="${label}">\n${flowRefs}\n      <bpmn:timerEventDefinition/>\n    </bpmn:intermediateCatchEvent>`
        : `    <bpmn:intermediateCatchEvent id="${elementId}" name="${label}">\n      <bpmn:timerEventDefinition/>\n    </bpmn:intermediateCatchEvent>`;

    case "service":
      return flowRefs
        ? `    <bpmn:serviceTask id="${elementId}" name="${label}">\n${flowRefs}\n    </bpmn:serviceTask>`
        : `    <bpmn:serviceTask id="${elementId}" name="${label}"/>`;

    case "user":
      return flowRefs
        ? `    <bpmn:userTask id="${elementId}" name="${label}">\n${flowRefs}\n    </bpmn:userTask>`
        : `    <bpmn:userTask id="${elementId}" name="${label}"/>`;

    case "task":
    default:
      return flowRefs
        ? `    <bpmn:task id="${elementId}" name="${label}">\n${flowRefs}\n    </bpmn:task>`
        : `    <bpmn:task id="${elementId}" name="${label}"/>`;
  }
}

function refId(nodeId: string, nodeById: Map<string, MermaidNode>): string {
  const node = nodeById.get(nodeId);
  if (!node) return `Task_${nodeId}`;

  switch (node.kind) {
    case "start":
      return `StartEvent_${nodeId}`;
    case "end":
      return `EndEvent_${nodeId}`;
    case "gateway":
      return `Gateway_${nodeId}`;
    case "timer":
      return `TimerEvent_${nodeId}`;
    case "service":
      return `ServiceTask_${nodeId}`;
    case "user":
      return `UserTask_${nodeId}`;
    default:
      return `Task_${nodeId}`;
  }
}

function getNodeDimensions(kind: NodeKind): { width: number; height: number } {
  switch (kind) {
    case "start":
    case "end":
    case "timer":
      return { width: 36, height: 36 };
    case "gateway":
      return { width: 50, height: 50 };
    default:
      return { width: 100, height: 80 };
  }
}

interface Position {
  x: number;
  y: number;
}

function calculatePositions(
  model: MermaidModel,
  opts: { baseX: number; baseY: number; nodeSpacingX: number; laneSpacingY: number }
): Map<string, Position> {
  const positions = new Map<string, Position>();
  const { baseX, baseY, nodeSpacingX, laneSpacingY } = opts;

  // Group nodes by lane
  const laneNodes = new Map<string, MermaidNode[]>();
  for (const node of model.nodes) {
    const lane = node.lane || "Default";
    const existing = laneNodes.get(lane) || [];
    existing.push(node);
    laneNodes.set(lane, existing);
  }

  // Calculate positions per lane
  let laneY = baseY;
  for (const [lane, nodes] of laneNodes) {
    // Sort nodes by appearance in edges (topological-ish)
    const sortedNodes = sortNodesByFlow(nodes, model.edges);
    let nodeX = baseX;

    for (const node of sortedNodes) {
      const { width, height } = getNodeDimensions(node.kind);
      positions.set(node.id, {
        x: nodeX,
        y: laneY + (laneSpacingY - height) / 2,
      });
      nodeX += nodeSpacingX;
    }

    laneY += laneSpacingY;
  }

  return positions;
}

function sortNodesByFlow(nodes: MermaidNode[], edges: MermaidEdge[]): MermaidNode[] {
  const nodeIds = new Set(nodes.map((n) => n.id));
  const inDegree = new Map<string, number>();
  const adjacency = new Map<string, string[]>();

  for (const node of nodes) {
    inDegree.set(node.id, 0);
    adjacency.set(node.id, []);
  }

  for (const edge of edges) {
    if (nodeIds.has(edge.from) && nodeIds.has(edge.to)) {
      adjacency.get(edge.from)?.push(edge.to);
      inDegree.set(edge.to, (inDegree.get(edge.to) || 0) + 1);
    }
  }

  // Topological sort using Kahn's algorithm
  const queue: string[] = [];
  for (const [id, deg] of inDegree) {
    if (deg === 0) queue.push(id);
  }

  const sorted: MermaidNode[] = [];
  const nodeById = new Map(nodes.map((n) => [n.id, n]));

  while (queue.length > 0) {
    const id = queue.shift()!;
    const node = nodeById.get(id);
    if (node) sorted.push(node);

    for (const next of adjacency.get(id) || []) {
      const newDeg = (inDegree.get(next) || 0) - 1;
      inDegree.set(next, newDeg);
      if (newDeg === 0) queue.push(next);
    }
  }

  // Add any nodes not in the sorted result (cycles or disconnected)
  for (const node of nodes) {
    if (!sorted.includes(node)) {
      sorted.push(node);
    }
  }

  return sorted;
}

function calculatePoolHeight(model: MermaidModel, pool: string, laneSpacingY: number): number {
  const poolLanes = model.lanes.get(pool) || [];
  return Math.max(poolLanes.length * laneSpacingY, laneSpacingY);
}

function sanitizeId(str: string): string {
  return str.replace(/[^A-Za-z0-9_]/g, "_");
}

function escXml(str: string): string {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

let idCounter = 0;
function generateId(prefix: string): string {
  return `${prefix}_${++idCounter}`;
}
