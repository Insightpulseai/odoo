/**
 * Mermaid Parser - Restricted BPMN Subset
 *
 * Parses Mermaid flowchart syntax into an intermediate model
 * suitable for BPMN 2.0 and draw.io conversion.
 *
 * Supported Mermaid conventions:
 * - subgraph → BPMN Pool/Lane (participant/lane)
 * - [Task] → BPMN task
 * - ((Start)) → BPMN startEvent
 * - (((End))) → BPMN endEvent
 * - {Gateway?} → BPMN exclusiveGateway
 * - --> → BPMN sequenceFlow
 * - -.-> → BPMN messageFlow (cross-pool only)
 */

export type NodeKind = "start" | "end" | "task" | "gateway" | "service" | "user" | "timer";

export interface MermaidNode {
  id: string;
  label: string;
  kind: NodeKind;
  lane?: string;
  pool?: string;
  metadata?: Record<string, string>;
}

export interface MermaidEdge {
  from: string;
  to: string;
  kind: "sequence" | "message";
  label?: string;
  condition?: string;
}

export interface MermaidModel {
  title?: string;
  pools: string[];
  lanes: Map<string, string[]>; // pool -> lanes
  nodes: MermaidNode[];
  edges: MermaidEdge[];
  direction: "LR" | "TB" | "RL" | "BT";
}

// Node shape patterns
const PATTERNS = {
  // ((Start)) - start event
  start: /^\(\(([^)]+)\)\)$/,
  // (((End))) - end event (triple parens)
  endTriple: /^\(\(\(([^)]+)\)\)\)$/,
  // ((End)) can also be end if context suggests
  endDouble: /^\(\(([^)]+)\)\)$/,
  // [Task] - regular task
  task: /^\[([^\]]+)\]$/,
  // {Gateway?} - gateway/decision
  gateway: /^\{([^}]+)\}$/,
  // ([Timer]) - timer event
  timer: /^\(\[([^\]]+)\]\)$/,
  // [[Service]] - service task
  service: /^\[\[([^\]]+)\]\]$/,
  // [/User/] - user task (parallelogram-ish)
  user: /^\[\/([^/]+)\/\]$/,
};

// Edge patterns
const EDGE_PATTERNS = {
  // --> sequence flow
  sequence: /^([A-Za-z0-9_]+)\s*-->\s*\|?([^|]*)\|?\s*([A-Za-z0-9_]+)$/,
  // -.-> message flow
  message: /^([A-Za-z0-9_]+)\s*-\.->\s*\|?([^|]*)\|?\s*([A-Za-z0-9_]+)$/,
  // ==> thick arrow (treat as sequence)
  thick: /^([A-Za-z0-9_]+)\s*==>\s*\|?([^|]*)\|?\s*([A-Za-z0-9_]+)$/,
};

export interface ParseOptions {
  /** Treat double-paren nodes ending with "End" as end events */
  inferEndFromLabel?: boolean;
  /** Default pool name if none specified */
  defaultPool?: string;
  /** Default lane name if none specified */
  defaultLane?: string;
}

export function parseMermaid(src: string, options: ParseOptions = {}): MermaidModel {
  const {
    inferEndFromLabel = true,
    defaultPool = "Process",
    defaultLane = "Default",
  } = options;

  const model: MermaidModel = {
    pools: [],
    lanes: new Map(),
    nodes: [],
    edges: [],
    direction: "LR",
  };

  let currentPool: string | undefined;
  let currentLane: string | undefined;
  const nodeById = new Map<string, MermaidNode>();

  const lines = src
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("%%")); // Remove empty and comments

  for (const line of lines) {
    // Skip flowchart declaration but capture direction
    if (line.startsWith("flowchart") || line.startsWith("graph")) {
      const dirMatch = line.match(/(?:flowchart|graph)\s+(LR|TB|RL|BT|TD)/i);
      if (dirMatch) {
        model.direction = dirMatch[1].toUpperCase() as MermaidModel["direction"];
      }
      continue;
    }

    // Title
    if (line.startsWith("---") || line.startsWith("title:")) {
      const titleMatch = line.match(/title:\s*(.+)/);
      if (titleMatch) {
        model.title = titleMatch[1].trim();
      }
      continue;
    }

    // Subgraph start - can be pool or lane
    // Format: subgraph Pool/Lane or subgraph PoolName[Display Name]
    if (line.startsWith("subgraph ")) {
      const subgraphContent = line.replace("subgraph", "").trim();
      const bracketMatch = subgraphContent.match(/^([A-Za-z0-9_]+)\s*\[([^\]]+)\]/);

      let name: string;
      let displayName: string;

      if (bracketMatch) {
        name = bracketMatch[1];
        displayName = bracketMatch[2];
      } else {
        name = subgraphContent;
        displayName = subgraphContent;
      }

      // Detect pool vs lane by convention: if already in a pool, this is a lane
      if (!currentPool) {
        currentPool = name;
        if (!model.pools.includes(name)) {
          model.pools.push(name);
          model.lanes.set(name, []);
        }
      } else {
        currentLane = name;
        const poolLanes = model.lanes.get(currentPool) || [];
        if (!poolLanes.includes(name)) {
          poolLanes.push(name);
          model.lanes.set(currentPool, poolLanes);
        }
      }
      continue;
    }

    // End subgraph
    if (line === "end") {
      if (currentLane) {
        currentLane = undefined;
      } else if (currentPool) {
        currentPool = undefined;
      }
      continue;
    }

    // Try to parse as edge first
    const edge = parseEdge(line);
    if (edge) {
      model.edges.push(edge);
      // Auto-create nodes referenced in edges if not defined
      for (const nodeId of [edge.from, edge.to]) {
        if (!nodeById.has(nodeId)) {
          const node: MermaidNode = {
            id: nodeId,
            label: nodeId,
            kind: "task",
            pool: currentPool || defaultPool,
            lane: currentLane || currentPool || defaultLane,
          };
          nodeById.set(nodeId, node);
          model.nodes.push(node);
        }
      }
      continue;
    }

    // Try to parse as node definition
    const node = parseNode(line, {
      currentPool: currentPool || defaultPool,
      currentLane: currentLane || currentPool || defaultLane,
      inferEndFromLabel,
    });
    if (node && !nodeById.has(node.id)) {
      nodeById.set(node.id, node);
      model.nodes.push(node);
    }
  }

  // Ensure default pool exists if we have nodes but no pools
  if (model.pools.length === 0 && model.nodes.length > 0) {
    model.pools.push(defaultPool);
    model.lanes.set(defaultPool, [defaultLane]);
    model.nodes.forEach((n) => {
      if (!n.pool) n.pool = defaultPool;
      if (!n.lane) n.lane = defaultLane;
    });
  }

  return model;
}

function parseEdge(line: string): MermaidEdge | null {
  // Check for edge patterns
  for (const [kind, pattern] of Object.entries(EDGE_PATTERNS)) {
    const match = line.match(pattern);
    if (match) {
      const [, from, label, to] = match;
      return {
        from: from.trim(),
        to: to.trim(),
        kind: kind === "message" ? "message" : "sequence",
        label: label?.trim() || undefined,
      };
    }
  }

  // Simple arrow patterns without labels
  if (line.includes("-->")) {
    const parts = line.split("-->").map((s) => s.trim());
    if (parts.length >= 2 && /^[A-Za-z0-9_]+$/.test(parts[0])) {
      // Could be chained: A --> B --> C
      const edges: MermaidEdge[] = [];
      for (let i = 0; i < parts.length - 1; i++) {
        const from = parts[i].match(/([A-Za-z0-9_]+)$/)?.[1];
        const to = parts[i + 1].match(/^([A-Za-z0-9_]+)/)?.[1];
        if (from && to) {
          return { from, to, kind: "sequence" };
        }
      }
    }
  }

  if (line.includes("-.->")) {
    const parts = line.split("-.->").map((s) => s.trim());
    if (parts.length === 2) {
      const from = parts[0].match(/([A-Za-z0-9_]+)$/)?.[1];
      const to = parts[1].match(/^([A-Za-z0-9_]+)/)?.[1];
      if (from && to) {
        return { from, to, kind: "message" };
      }
    }
  }

  return null;
}

interface NodeParseContext {
  currentPool: string;
  currentLane: string;
  inferEndFromLabel: boolean;
}

function parseNode(line: string, ctx: NodeParseContext): MermaidNode | null {
  // Pattern: ID followed by shape
  // e.g., S((Start)), T1[Do something], G{Decision?}
  const nodeMatch = line.match(/^([A-Za-z0-9_]+)\s*(.+)$/);
  if (!nodeMatch) return null;

  const id = nodeMatch[1];
  const body = nodeMatch[2].trim();

  // Skip if this looks like an edge definition we missed
  if (body.includes("-->") || body.includes("-.->")) return null;

  let kind: NodeKind = "task";
  let label = body;
  let metadata: Record<string, string> | undefined;

  // Check for metadata suffix: svc=azure.app_service
  const metaMatch = body.match(/\|?\s*svc=([a-z0-9_.-]+)\s*\|?$/i);
  if (metaMatch) {
    metadata = { svc: metaMatch[1] };
    label = body.replace(metaMatch[0], "").trim();
  }

  // Match shapes in order of specificity
  const endTriple = label.match(PATTERNS.endTriple);
  if (endTriple) {
    return { id, label: endTriple[1], kind: "end", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  const timer = label.match(PATTERNS.timer);
  if (timer) {
    return { id, label: timer[1], kind: "timer", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  const service = label.match(PATTERNS.service);
  if (service) {
    return { id, label: service[1], kind: "service", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  const user = label.match(PATTERNS.user);
  if (user) {
    return { id, label: user[1], kind: "user", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  const start = label.match(PATTERNS.start);
  if (start) {
    // Could be start or end based on label
    const labelLower = start[1].toLowerCase();
    if (ctx.inferEndFromLabel && (labelLower.includes("end") || labelLower.includes("finish"))) {
      return { id, label: start[1], kind: "end", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
    }
    return { id, label: start[1], kind: "start", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  const gateway = label.match(PATTERNS.gateway);
  if (gateway) {
    return { id, label: gateway[1], kind: "gateway", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  const task = label.match(PATTERNS.task);
  if (task) {
    return { id, label: task[1], kind: "task", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  // Default to task if we have some content
  if (body.length > 0 && !body.includes("-->")) {
    return { id, label: body, kind: "task", pool: ctx.currentPool, lane: ctx.currentLane, metadata };
  }

  return null;
}

/**
 * Validate the model for BPMN compliance
 */
export function validateModel(model: MermaidModel): string[] {
  const errors: string[] = [];
  const nodeById = new Map(model.nodes.map((n) => [n.id, n]));

  // Check that all edge endpoints exist
  for (const edge of model.edges) {
    if (!nodeById.has(edge.from)) {
      errors.push(`Edge references undefined node: ${edge.from}`);
    }
    if (!nodeById.has(edge.to)) {
      errors.push(`Edge references undefined node: ${edge.to}`);
    }
  }

  // Check message flows cross pools
  for (const edge of model.edges.filter((e) => e.kind === "message")) {
    const fromNode = nodeById.get(edge.from);
    const toNode = nodeById.get(edge.to);
    if (fromNode && toNode && fromNode.pool === toNode.pool) {
      errors.push(`Message flow ${edge.from} -> ${edge.to} must cross pools (both in ${fromNode.pool})`);
    }
  }

  // Check for start/end events
  const hasStart = model.nodes.some((n) => n.kind === "start");
  const hasEnd = model.nodes.some((n) => n.kind === "end");
  if (!hasStart) {
    errors.push("Model should have at least one start event");
  }
  if (!hasEnd) {
    errors.push("Model should have at least one end event");
  }

  // Check gateway connections
  for (const node of model.nodes.filter((n) => n.kind === "gateway")) {
    const incoming = model.edges.filter((e) => e.to === node.id);
    const outgoing = model.edges.filter((e) => e.from === node.id);
    if (outgoing.length < 2) {
      errors.push(`Gateway ${node.id} should have at least 2 outgoing edges (has ${outgoing.length})`);
    }
  }

  return errors;
}
