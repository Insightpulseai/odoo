/**
 * draw.io XML Generator
 *
 * Converts MermaidModel to draw.io XML format.
 * The generated .drawio file can be:
 * - Opened in draw.io / diagrams.net
 * - Exported to PNG/SVG via CLI
 * - Version controlled as source of truth
 */

import type { MermaidModel, MermaidNode, MermaidEdge, NodeKind } from "./parseMermaid.js";

export interface DrawioOptions {
  /** Diagram name */
  diagramName?: string;
  /** Base X position */
  baseX?: number;
  /** Base Y position */
  baseY?: number;
  /** Horizontal spacing between nodes */
  nodeSpacingX?: number;
  /** Vertical spacing between lanes */
  laneSpacingY?: number;
  /** Use swimlane style for lanes */
  useSwimlanes?: boolean;
  /** Theme: light or dark */
  theme?: "light" | "dark";
}

interface Position {
  x: number;
  y: number;
}

interface NodeStyle {
  style: string;
  width: number;
  height: number;
}

// BPMN-style shapes for draw.io
const NODE_STYLES: Record<NodeKind, NodeStyle> = {
  start: {
    style: "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#d5e8d4;strokeColor=#82b366;",
    width: 40,
    height: 40,
  },
  end: {
    style: "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#f8cecc;strokeColor=#b85450;strokeWidth=3;",
    width: 40,
    height: 40,
  },
  task: {
    style: "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;",
    width: 120,
    height: 60,
  },
  gateway: {
    style: "rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;",
    width: 50,
    height: 50,
  },
  service: {
    style: "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;",
    width: 120,
    height: 60,
  },
  user: {
    style: "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;",
    width: 120,
    height: 60,
  },
  timer: {
    style: "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#f5f5f5;strokeColor=#666666;",
    width: 40,
    height: 40,
  },
};

const EDGE_STYLES = {
  sequence: "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;",
  message: "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;dashPattern=8 8;endArrow=open;endFill=0;",
};

const SWIMLANE_STYLE = "swimlane;horizontal=0;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;rounded=1;";

export function toDrawioXml(model: MermaidModel, options: DrawioOptions = {}): string {
  const {
    diagramName = "Diagram",
    baseX = 160,
    baseY = 80,
    nodeSpacingX = 180,
    laneSpacingY = 160,
    useSwimlanes = true,
  } = options;

  const cells: string[] = [];
  let idSeq = 2; // 0 and 1 are reserved

  const nodePositions = calculatePositions(model, { baseX, baseY, nodeSpacingX, laneSpacingY });
  const nodeCellIds = new Map<string, number>();
  const laneCellIds = new Map<string, number>();

  // Root cells (always required)
  cells.push(`    <mxCell id="0"/>`);
  cells.push(`    <mxCell id="1" parent="0"/>`);

  // Build lane structure
  const pools = model.pools.length > 0 ? model.pools : ["Default"];

  for (const pool of pools) {
    const poolLanes = model.lanes.get(pool) || [];
    const lanes = poolLanes.length > 0 ? poolLanes : [pool];

    let poolY = baseY - 40;

    for (let laneIdx = 0; laneIdx < lanes.length; laneIdx++) {
      const lane = lanes[laneIdx];
      const laneId = idSeq++;
      laneCellIds.set(`${pool}:${lane}`, laneId);

      const laneY = poolY + laneIdx * laneSpacingY;
      const laneNodes = model.nodes.filter(
        (n) => (n.pool === pool || (!n.pool && pool === "Default")) && (n.lane === lane || (!n.lane && laneIdx === 0))
      );

      // Calculate lane width based on number of nodes
      const laneWidth = Math.max(laneNodes.length * nodeSpacingX + 100, 800);

      if (useSwimlanes) {
        cells.push(`    <mxCell id="${laneId}" value="${escXml(lane)}" style="${SWIMLANE_STYLE}" vertex="1" parent="1">`);
        cells.push(`      <mxGeometry x="${baseX - 80}" y="${laneY}" width="${laneWidth}" height="${laneSpacingY - 20}" as="geometry"/>`);
        cells.push(`    </mxCell>`);
      }
    }
  }

  // Add nodes
  for (const node of model.nodes) {
    const nodeId = idSeq++;
    nodeCellIds.set(node.id, nodeId);

    const pos = nodePositions.get(node.id) || { x: baseX, y: baseY };
    const { style, width, height } = NODE_STYLES[node.kind] || NODE_STYLES.task;

    // Find parent lane
    const laneKey = `${node.pool || "Default"}:${node.lane || node.pool || "Default"}`;
    const parentId = laneCellIds.get(laneKey) || 1;

    // Adjust position relative to parent if using swimlanes
    const relX = useSwimlanes ? pos.x - (baseX - 80) + 40 : pos.x;
    const relY = useSwimlanes ? 40 : pos.y;

    cells.push(`    <mxCell id="${nodeId}" value="${escXml(node.label)}" style="${style}" vertex="1" parent="${parentId}">`);
    cells.push(`      <mxGeometry x="${relX}" y="${relY}" width="${width}" height="${height}" as="geometry"/>`);
    cells.push(`    </mxCell>`);
  }

  // Add edges
  for (const edge of model.edges) {
    const edgeId = idSeq++;
    const sourceId = nodeCellIds.get(edge.from);
    const targetId = nodeCellIds.get(edge.to);

    if (!sourceId || !targetId) continue;

    const style = EDGE_STYLES[edge.kind] || EDGE_STYLES.sequence;
    const label = edge.label ? `value="${escXml(edge.label)}"` : 'value=""';

    cells.push(`    <mxCell id="${edgeId}" ${label} style="${style}" edge="1" parent="1" source="${sourceId}" target="${targetId}">`);
    cells.push(`      <mxGeometry relative="1" as="geometry"/>`);
    cells.push(`    </mxCell>`);
  }

  // Build the complete XML
  const timestamp = new Date().toISOString();
  const gridSize = 10;
  const pageWidth = Math.max(model.nodes.length * nodeSpacingX + 400, 1600);
  const pageHeight = Math.max((model.lanes.size || 1) * laneSpacingY + 200, 900);

  return `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="${timestamp}" agent="diagramflow/1.0.0" version="24.7.17" type="device">
  <diagram id="${sanitizeId(diagramName)}" name="${escXml(diagramName)}">
    <mxGraphModel dx="${Math.round(pageWidth * 0.8)}" dy="${Math.round(pageHeight * 0.8)}" grid="1" gridSize="${gridSize}" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="${pageWidth}" pageHeight="${pageHeight}" math="0" shadow="0">
      <root>
${cells.join("\n")}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`;
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
    const laneKey = `${node.pool || "Default"}:${node.lane || node.pool || "Default"}`;
    const existing = laneNodes.get(laneKey) || [];
    existing.push(node);
    laneNodes.set(laneKey, existing);
  }

  // Calculate positions per lane
  let laneY = baseY;
  const sortedLaneKeys = Array.from(laneNodes.keys()).sort();

  for (const laneKey of sortedLaneKeys) {
    const nodes = laneNodes.get(laneKey) || [];
    const sortedNodes = sortNodesByFlow(nodes, model.edges);
    let nodeX = baseX;

    for (const node of sortedNodes) {
      const { width, height } = NODE_STYLES[node.kind] || NODE_STYLES.task;
      positions.set(node.id, {
        x: nodeX,
        y: laneY + (laneSpacingY - height) / 2 - 20,
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

  // Topological sort (Kahn's algorithm)
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

  // Add remaining nodes
  for (const node of nodes) {
    if (!sorted.includes(node)) {
      sorted.push(node);
    }
  }

  return sorted;
}

function sanitizeId(str: string): string {
  return str.replace(/[^A-Za-z0-9_-]/g, "_");
}

function escXml(str: string): string {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
