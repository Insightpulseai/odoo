'use client';

import { useState, useEffect, useMemo } from 'react';
import {
  Badge,
  Button,
  Spinner,
  Select,
  Card,
  CardHeader,
  Text,
} from '@fluentui/react-components';
import {
  ArrowClockwise24Regular,
  ZoomIn24Regular,
  ZoomOut24Regular,
  FullScreenMaximize24Regular,
  Server24Regular,
  Database24Regular,
  Bot24Regular,
  Globe24Regular,
} from '@fluentui/react-icons';
import type { Topology, TopologyNode, TopologyEdge, NodeType, ServiceStatus } from '@/types/observability';

const nodeTypeIcons: Record<NodeType, React.ReactNode> = {
  service: <Server24Regular />,
  database: <Database24Regular />,
  agent: <Bot24Regular />,
  external: <Globe24Regular />,
};

const statusColors: Record<string, string> = {
  healthy: '#10b981',
  active: '#10b981',
  degraded: '#f59e0b',
  busy: '#f59e0b',
  idle: '#3b82f6',
  unhealthy: '#ef4444',
  offline: '#6b7280',
  unknown: '#6b7280',
};

/**
 * SVG-based topology graph component
 * Renders nodes and edges for ecosystem visualization
 */
function TopologyGraph({ topology }: { topology: Topology }) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  // Calculate node positions using a simple force-directed layout
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const width = 800;
    const height = 500;
    const centerX = width / 2;
    const centerY = height / 2;

    // Group nodes by type
    const groups: Record<string, TopologyNode[]> = {
      database: [],
      service: [],
      agent: [],
      external: [],
    };

    topology.nodes.forEach(node => {
      if (groups[node.type]) {
        groups[node.type].push(node);
      }
    });

    // Position databases at top
    groups.database.forEach((node, i) => {
      const total = groups.database.length;
      const spacing = width / (total + 1);
      positions[node.id] = { x: spacing * (i + 1), y: 80 };
    });

    // Position services in middle row
    groups.service.forEach((node, i) => {
      const total = groups.service.length;
      const spacing = width / (total + 1);
      positions[node.id] = { x: spacing * (i + 1), y: centerY };
    });

    // Position agents at bottom left
    groups.agent.forEach((node, i) => {
      const total = groups.agent.length;
      const spacing = 300 / (total + 1);
      positions[node.id] = { x: spacing * (i + 1) + 50, y: height - 100 };
    });

    // Position external services at bottom right
    groups.external.forEach((node, i) => {
      const total = groups.external.length;
      const spacing = 300 / (total + 1);
      positions[node.id] = { x: width - spacing * (i + 1) - 50, y: height - 100 };
    });

    return positions;
  }, [topology.nodes]);

  const handleZoomIn = () => setZoom(z => Math.min(z + 0.2, 2));
  const handleZoomOut = () => setZoom(z => Math.max(z - 0.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="relative w-full h-[500px] bg-surface-50 rounded-lg border border-surface-100 overflow-hidden">
      {/* Controls */}
      <div className="absolute top-2 right-2 z-10 flex gap-1 bg-surface-100/80 rounded p-1">
        <Button
          appearance="subtle"
          icon={<ZoomIn24Regular />}
          size="small"
          onClick={handleZoomIn}
        />
        <Button
          appearance="subtle"
          icon={<ZoomOut24Regular />}
          size="small"
          onClick={handleZoomOut}
        />
        <Button
          appearance="subtle"
          icon={<FullScreenMaximize24Regular />}
          size="small"
          onClick={handleReset}
        />
      </div>

      {/* SVG Graph */}
      <svg
        width="100%"
        height="100%"
        viewBox={`${-pan.x} ${-pan.y} ${800 / zoom} ${500 / zoom}`}
        className="cursor-move"
      >
        <defs>
          {/* Arrow marker for edges */}
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
          </marker>
        </defs>

        {/* Edges */}
        <g className="edges">
          {topology.edges.map((edge) => {
            const sourcePos = nodePositions[edge.source];
            const targetPos = nodePositions[edge.target];

            if (!sourcePos || !targetPos) return null;

            const edgeColor =
              edge.type === 'data_flow'
                ? '#3b82f6'
                : edge.type === 'health_dependency'
                ? '#10b981'
                : edge.type === 'agent_delegation'
                ? '#8b5cf6'
                : '#64748b';

            return (
              <g key={edge.id}>
                <line
                  x1={sourcePos.x}
                  y1={sourcePos.y}
                  x2={targetPos.x}
                  y2={targetPos.y}
                  stroke={edgeColor}
                  strokeWidth="2"
                  strokeDasharray={edge.type === 'api_call' ? '5,5' : undefined}
                  markerEnd="url(#arrowhead)"
                  className="opacity-60 hover:opacity-100 transition-opacity"
                />
              </g>
            );
          })}
        </g>

        {/* Nodes */}
        <g className="nodes">
          {topology.nodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;

            const color = statusColors[node.status] || statusColors.unknown;

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer"
              >
                {/* Node circle */}
                <circle
                  r="30"
                  fill={`${color}20`}
                  stroke={color}
                  strokeWidth="3"
                  className="transition-all hover:r-[35px]"
                />

                {/* Node icon placeholder */}
                <text
                  y="5"
                  textAnchor="middle"
                  fill={color}
                  fontSize="20"
                  className="select-none"
                >
                  {node.type === 'service' ? 'S' : node.type === 'database' ? 'D' : node.type === 'agent' ? 'A' : 'E'}
                </text>

                {/* Node label */}
                <text
                  y="50"
                  textAnchor="middle"
                  fill="currentColor"
                  fontSize="12"
                  className="select-none fill-surface-200"
                >
                  {node.name.length > 15 ? `${node.name.slice(0, 15)}...` : node.name}
                </text>

                {/* Status indicator */}
                <circle
                  cx="20"
                  cy="-20"
                  r="8"
                  fill={color}
                  className="animate-pulse"
                />
              </g>
            );
          })}
        </g>
      </svg>

      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-surface-100/80 rounded p-2 text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-emerald-500" />
            <span>Healthy/Active</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-amber-500" />
            <span>Degraded/Busy</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span>Unhealthy</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-gray-500" />
            <span>Offline</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function TopologyTab() {
  const [topology, setTopology] = useState<Topology | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const fetchTopology = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/observability/topology');
      if (!response.ok) throw new Error('Failed to fetch topology');

      const data = await response.json();
      setTopology(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setTopology(getMockTopology());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTopology();
  }, []);

  // Filter topology by node type
  const filteredTopology = useMemo(() => {
    if (!topology || filter === 'all') return topology;

    const filteredNodes = topology.nodes.filter(n => n.type === filter);
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = topology.edges.filter(
      e => nodeIds.has(e.source) || nodeIds.has(e.target)
    );

    return { nodes: filteredNodes, edges: filteredEdges };
  }, [topology, filter]);

  if (isLoading && !topology) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="large" label="Loading topology..." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Select
            value={filter}
            onChange={(_, data) => setFilter(data.value)}
          >
            <option value="all">All Components</option>
            <option value="service">Services</option>
            <option value="database">Databases</option>
            <option value="agent">Agents</option>
            <option value="external">External</option>
          </Select>

          <div className="text-sm text-surface-400">
            {filteredTopology?.nodes.length || 0} nodes, {filteredTopology?.edges.length || 0} edges
          </div>
        </div>

        <Button
          appearance="subtle"
          icon={<ArrowClockwise24Regular />}
          onClick={fetchTopology}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded text-amber-400 text-sm">
          Using mock data: {error}
        </div>
      )}

      {/* Graph */}
      {filteredTopology && (
        <TopologyGraph topology={filteredTopology} />
      )}

      {/* Node Details */}
      {filteredTopology && filteredTopology.nodes.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {filteredTopology.nodes.map((node) => (
            <Card key={node.id} size="small" className="hover:bg-surface-100/50">
              <CardHeader
                image={nodeTypeIcons[node.type]}
                header={<Text size={200} weight="semibold">{node.name}</Text>}
                description={
                  <Badge
                    size="small"
                    color={
                      node.status === 'healthy' || node.status === 'active'
                        ? 'success'
                        : node.status === 'degraded' || node.status === 'busy'
                        ? 'warning'
                        : node.status === 'unhealthy'
                        ? 'danger'
                        : 'subtle'
                    }
                  >
                    {node.status}
                  </Badge>
                }
              />
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// Mock topology data
function getMockTopology(): Topology {
  return {
    nodes: [
      { id: 'postgres', type: 'database', name: 'PostgreSQL', status: 'healthy' },
      { id: 'odoo-core', type: 'service', name: 'Odoo CE Core', status: 'healthy', service_type: 'application' },
      { id: 'odoo-marketing', type: 'service', name: 'Odoo Marketing', status: 'healthy', service_type: 'application' },
      { id: 'n8n', type: 'service', name: 'n8n Workflows', status: 'healthy', service_type: 'application' },
      { id: 'mcp-coordinator', type: 'service', name: 'MCP Coordinator', status: 'degraded', service_type: 'application' },
      { id: 'claude-agent', type: 'agent', name: 'Claude Code Agent', status: 'active', capabilities: ['code'] },
      { id: 'sync-agent', type: 'agent', name: 'Data Sync Agent', status: 'busy', capabilities: ['etl'] },
      { id: 'supabase', type: 'external', name: 'Supabase', status: 'healthy' },
      { id: 'github', type: 'external', name: 'GitHub API', status: 'healthy' },
    ],
    edges: [
      { id: '1', source: 'odoo-core', target: 'postgres', type: 'data_flow', direction: 'outbound' },
      { id: '2', source: 'odoo-marketing', target: 'postgres', type: 'data_flow', direction: 'outbound' },
      { id: '3', source: 'n8n', target: 'odoo-core', type: 'api_call', direction: 'outbound' },
      { id: '4', source: 'n8n', target: 'supabase', type: 'api_call', direction: 'outbound' },
      { id: '5', source: 'mcp-coordinator', target: 'odoo-core', type: 'api_call', direction: 'outbound' },
      { id: '6', source: 'mcp-coordinator', target: 'claude-agent', type: 'agent_delegation', direction: 'outbound' },
      { id: '7', source: 'mcp-coordinator', target: 'sync-agent', type: 'agent_delegation', direction: 'outbound' },
      { id: '8', source: 'claude-agent', target: 'github', type: 'api_call', direction: 'outbound' },
      { id: '9', source: 'sync-agent', target: 'supabase', type: 'data_flow', direction: 'outbound' },
    ],
  };
}

export default TopologyTab;
