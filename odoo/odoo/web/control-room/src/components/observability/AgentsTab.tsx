'use client';

import { useState, useEffect } from 'react';
import {
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Button,
  Spinner,
  Tooltip,
  Card,
  CardHeader,
  Text,
} from '@fluentui/react-components';
import {
  ArrowClockwise24Regular,
  Bot24Regular,
  HeartPulse24Regular,
  Wrench24Regular,
} from '@fluentui/react-icons';
import type { AgentWithState, AgentStatus, AgentStats } from '@/types/observability';

const statusColors: Record<AgentStatus, 'success' | 'warning' | 'danger' | 'informative' | 'subtle'> = {
  active: 'success',
  idle: 'informative',
  busy: 'warning',
  offline: 'danger',
  maintenance: 'subtle',
};

function formatRelativeTime(dateStr?: string): string {
  if (!dateStr) return 'Never';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);

  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
  if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h ago`;
  return `${Math.floor(diffSecs / 86400)}d ago`;
}

export function AgentsTab() {
  const [agents, setAgents] = useState<AgentWithState[]>([]);
  const [stats, setStats] = useState<AgentStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/observability/agents');
      if (!response.ok) throw new Error('Failed to fetch agents');

      const data = await response.json();
      setAgents(data.agents || []);
      setStats(data.stats || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Use mock data
      setAgents(getMockAgents());
      setStats(getMockStats());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
    // Refresh every 30 seconds
    const interval = setInterval(fetchAgents, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleHeartbeat = async (agentId: string) => {
    try {
      await fetch(`/api/observability/agents/${agentId}/heartbeat`, {
        method: 'POST',
      });
      fetchAgents();
    } catch (err) {
      console.error('Failed to send heartbeat:', err);
    }
  };

  if (isLoading && agents.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="large" label="Loading agents..." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-surface-50">
            <CardHeader
              header={<Text weight="semibold">Total Agents</Text>}
              description={
                <span className="text-2xl font-bold">{stats.total_agents}</span>
              }
            />
          </Card>
          <Card className="bg-emerald-500/10 border-emerald-500/30">
            <CardHeader
              header={<Text weight="semibold" className="text-emerald-400">Active</Text>}
              description={
                <span className="text-2xl font-bold text-emerald-400">{stats.active_agents}</span>
              }
            />
          </Card>
          <Card className="bg-amber-500/10 border-amber-500/30">
            <CardHeader
              header={<Text weight="semibold" className="text-amber-400">Busy</Text>}
              description={
                <span className="text-2xl font-bold text-amber-400">{stats.busy_agents}</span>
              }
            />
          </Card>
          <Card className="bg-red-500/10 border-red-500/30">
            <CardHeader
              header={<Text weight="semibold" className="text-red-400">Offline</Text>}
              description={
                <span className="text-2xl font-bold text-red-400">{stats.offline_agents}</span>
              }
            />
          </Card>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-surface-400">
          {agents.length} agents registered
        </div>
        <Button
          appearance="subtle"
          icon={<ArrowClockwise24Regular />}
          onClick={fetchAgents}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded text-amber-400 text-sm">
          Using mock data: {error}
        </div>
      )}

      {/* Agents Table */}
      <div className="border border-surface-100 rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHeaderCell className="w-24">Status</TableHeaderCell>
              <TableHeaderCell>Name</TableHeaderCell>
              <TableHeaderCell>Version</TableHeaderCell>
              <TableHeaderCell>Capabilities</TableHeaderCell>
              <TableHeaderCell>Queue</TableHeaderCell>
              <TableHeaderCell>Last Heartbeat</TableHeaderCell>
              <TableHeaderCell className="w-24">Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {agents.map((agent) => (
              <TableRow key={agent.id} className="hover:bg-surface-100/50">
                <TableCell>
                  <Badge color={statusColors[agent.status]} appearance="filled">
                    {agent.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Bot24Regular className="text-surface-400" />
                    <div>
                      <div className="font-medium">{agent.name}</div>
                      <div className="text-xs text-surface-400 font-mono">{agent.id}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="font-mono text-sm">{agent.version}</TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.slice(0, 3).map((cap) => (
                      <Badge key={cap} appearance="outline" size="small">
                        {cap}
                      </Badge>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <Badge appearance="outline" size="small">
                        +{agent.capabilities.length - 3}
                      </Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <span className={agent.state?.queue_depth ? 'text-amber-400' : 'text-surface-400'}>
                    {agent.state?.queue_depth || 0} jobs
                  </span>
                </TableCell>
                <TableCell className="text-surface-300">
                  {formatRelativeTime(agent.last_heartbeat)}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Tooltip content="Send Heartbeat" relationship="label">
                      <Button
                        appearance="subtle"
                        icon={<HeartPulse24Regular />}
                        size="small"
                        onClick={() => handleHeartbeat(agent.id)}
                      />
                    </Tooltip>
                    <Tooltip content="Set Maintenance" relationship="label">
                      <Button
                        appearance="subtle"
                        icon={<Wrench24Regular />}
                        size="small"
                        disabled={agent.status === 'maintenance'}
                      />
                    </Tooltip>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {agents.length === 0 && !isLoading && (
        <div className="text-center py-8 text-surface-400">
          No agents registered
        </div>
      )}
    </div>
  );
}

// Mock data
function getMockAgents(): AgentWithState[] {
  return [
    {
      id: 'claude-code-agent',
      name: 'Claude Code Agent',
      version: '1.0.0',
      description: 'Primary coding assistant',
      capabilities: ['code_generation', 'code_review', 'debugging', 'refactoring'],
      transport: 'http',
      endpoint: 'http://localhost:8001',
      tools: ['read_file', 'write_file', 'execute_command'],
      timeout_ms: 30000,
      max_concurrent: 5,
      tags: ['ai', 'coding'],
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_heartbeat: new Date(Date.now() - 15000).toISOString(),
      state: {
        agent_id: 'claude-code-agent',
        status: 'active',
        queue_depth: 2,
        last_heartbeat: new Date(Date.now() - 15000).toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
    {
      id: 'odoo-erp-agent',
      name: 'Odoo ERP Agent',
      version: '0.5.0',
      description: 'ERP operations agent',
      capabilities: ['accounting', 'inventory', 'sales'],
      transport: 'http',
      endpoint: 'http://localhost:8002',
      tools: ['create_record', 'update_record', 'search_records'],
      timeout_ms: 60000,
      max_concurrent: 3,
      tags: ['erp', 'business'],
      status: 'idle',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_heartbeat: new Date(Date.now() - 45000).toISOString(),
      state: {
        agent_id: 'odoo-erp-agent',
        status: 'idle',
        queue_depth: 0,
        last_heartbeat: new Date(Date.now() - 45000).toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
    {
      id: 'data-sync-agent',
      name: 'Data Sync Agent',
      version: '2.1.0',
      description: 'Cross-system data synchronization',
      capabilities: ['etl', 'sync', 'validation'],
      transport: 'grpc',
      endpoint: 'grpc://localhost:9000',
      tools: ['sync_tables', 'validate_schema', 'run_migration'],
      timeout_ms: 120000,
      max_concurrent: 2,
      tags: ['data', 'sync'],
      status: 'busy',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_heartbeat: new Date(Date.now() - 5000).toISOString(),
      state: {
        agent_id: 'data-sync-agent',
        status: 'busy',
        current_task_id: 'task-123',
        queue_depth: 5,
        last_heartbeat: new Date(Date.now() - 5000).toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
    {
      id: 'notification-agent',
      name: 'Notification Agent',
      version: '1.2.0',
      description: 'Alerts and notifications',
      capabilities: ['email', 'slack', 'webhook'],
      transport: 'http',
      tools: ['send_email', 'post_slack', 'trigger_webhook'],
      timeout_ms: 10000,
      max_concurrent: 10,
      tags: ['notifications'],
      status: 'offline',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_heartbeat: new Date(Date.now() - 600000).toISOString(),
    },
  ];
}

function getMockStats(): AgentStats {
  return {
    total_agents: 4,
    active_agents: 1,
    idle_agents: 1,
    busy_agents: 1,
    offline_agents: 1,
    pending_jobs: 3,
    processing_jobs: 2,
  };
}

export default AgentsTab;
