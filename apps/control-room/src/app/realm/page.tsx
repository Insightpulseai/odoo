'use client';

import { useServiceHealth } from '@/hooks/useServiceHealth';
import { useMCPJobStats } from '@/hooks/useMCPJobs';
import { Card } from '@/components/common/Card';
import { KPICard } from '@/components/dashboard/KPICard';
import { JobQueueCard } from '@/components/observability';
import { ServiceHealthGrid, HealthStatusBanner } from '@/components/health';
import { PageContainer } from '@/components/layout/PageContainer';
import {
  Server,
  Activity,
  Bot,
  AlertTriangle,
  CheckCircle2,
  Database,
  BarChart2,
  Zap,
  Eye,
} from 'lucide-react';

// Agent/MCP Server data (static for now, can be made dynamic)
const MCP_SERVERS = [
  { name: 'odoo-erp-server', status: 'running', tools: 12 },
  { name: 'superset-mcp-server', status: 'running', tools: 8 },
  { name: 'digitalocean-mcp-server', status: 'running', tools: 15 },
  { name: 'pulser-mcp-server', status: 'running', tools: 6 },
  { name: 'speckit-mcp-server', status: 'stopped', tools: 4 },
  { name: 'mcp-jobs', status: 'running', tools: 5 },
];

function AgentCard({
  name,
  status,
  tools,
}: {
  name: string;
  status: string;
  tools: number;
}) {
  const isRunning = status === 'running';

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg ${
              isRunning ? 'bg-green-500/10' : 'bg-surface-100'
            }`}
          >
            <Bot className="h-4 w-4 text-surface-200" />
          </div>
          <div>
            <div className="font-medium text-sm">{name}</div>
            <div className="text-xs text-surface-300">{tools} tools</div>
          </div>
        </div>
        <div
          className={`w-2 h-2 rounded-full ${
            isRunning ? 'bg-green-400' : 'bg-surface-400'
          }`}
        />
      </div>
    </Card>
  );
}

export default function RealmPage() {
  const { data: health, isLoading: healthLoading } = useServiceHealth();
  const { data: jobStats, isLoading: jobsLoading } = useMCPJobStats();

  const healthyServices =
    health?.services.filter((s) => s.status === 'healthy').length ?? 0;
  const totalServices = health?.services.length ?? 0;

  const runningAgents = MCP_SERVERS.filter((a) => a.status === 'running').length;
  const totalAgents = MCP_SERVERS.length;

  return (
    <PageContainer
      title="Realm Overview"
      subtitle="Bird's eye view of the entire IPAI ecosystem"
    >
      {/* Status Banner */}
      <div className="mb-6">
        <HealthStatusBanner />
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard
          title="Services"
          value={`${healthyServices}/${totalServices}`}
          icon={<Server className="h-5 w-5" />}
          status={
            healthyServices === totalServices
              ? 'success'
              : healthyServices > 0
                ? 'warning'
                : 'error'
          }
          loading={healthLoading}
        />
        <KPICard
          title="Jobs (24h)"
          value={jobStats?.total ?? 0}
          subtitle={`${jobStats?.failed ?? 0} failed`}
          icon={<Activity className="h-5 w-5" />}
          status={(jobStats?.failed ?? 0) > 0 ? 'warning' : 'success'}
          loading={jobsLoading}
        />
        <KPICard
          title="MCP Agents"
          value={`${runningAgents}/${totalAgents}`}
          icon={<Bot className="h-5 w-5" />}
          status={runningAgents === totalAgents ? 'success' : 'warning'}
        />
        <KPICard
          title="Dead Letter"
          value={jobStats?.deadLetter ?? 0}
          icon={<AlertTriangle className="h-5 w-5" />}
          status={(jobStats?.deadLetter ?? 0) > 0 ? 'error' : 'success'}
          loading={jobsLoading}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Service Health */}
        <div className="col-span-12 lg:col-span-8">
          <Card className="p-6">
            <ServiceHealthGrid />
          </Card>
        </div>

        {/* MCP Agents */}
        <div className="col-span-12 lg:col-span-4">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">MCP Servers</h3>
              <span className="text-sm text-surface-300">
                {runningAgents}/{totalAgents} active
              </span>
            </div>
            <div className="space-y-3">
              {MCP_SERVERS.map((agent) => (
                <AgentCard key={agent.name} {...agent} />
              ))}
            </div>
          </Card>
        </div>

        {/* Job Queue */}
        <div className="col-span-12">
          <JobQueueCard />
        </div>

        {/* Quick Actions */}
        <div className="col-span-12">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button className="p-4 bg-surface-100 hover:bg-surface-200 rounded-lg transition-colors text-left">
                <Database className="h-5 w-5 text-blue-400 mb-2" />
                <div className="font-medium">Database</div>
                <div className="text-sm text-surface-300">View Supabase</div>
              </button>
              <button className="p-4 bg-surface-100 hover:bg-surface-200 rounded-lg transition-colors text-left">
                <BarChart2 className="h-5 w-5 text-green-400 mb-2" />
                <div className="font-medium">Analytics</div>
                <div className="text-sm text-surface-300">Open Superset</div>
              </button>
              <button className="p-4 bg-surface-100 hover:bg-surface-200 rounded-lg transition-colors text-left">
                <Zap className="h-5 w-5 text-yellow-400 mb-2" />
                <div className="font-medium">Workflows</div>
                <div className="text-sm text-surface-300">Open n8n</div>
              </button>
              <button className="p-4 bg-surface-100 hover:bg-surface-200 rounded-lg transition-colors text-left">
                <Eye className="h-5 w-5 text-purple-400 mb-2" />
                <div className="font-medium">Logs</div>
                <div className="text-sm text-surface-300">View all logs</div>
              </button>
            </div>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
