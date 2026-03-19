'use client';

import { useState, useEffect } from 'react';
import {
  Badge,
  Button,
  Spinner,
  Card,
  CardHeader,
  Text,
  Tooltip,
} from '@fluentui/react-components';
import {
  ArrowClockwise24Regular,
  CheckmarkCircle24Filled,
  Warning24Filled,
  DismissCircle24Filled,
  Cloud24Regular,
  Database24Regular,
  Server24Regular,
  Globe24Regular,
} from '@fluentui/react-icons';
import { HealthBadge } from '@/components/dashboard/HealthBadge';
import type { Service, ServiceStatus, HealthSummary } from '@/types/observability';

const statusIcons: Record<ServiceStatus, React.ReactNode> = {
  healthy: <CheckmarkCircle24Filled className="text-emerald-400" />,
  degraded: <Warning24Filled className="text-amber-400" />,
  unhealthy: <DismissCircle24Filled className="text-red-400" />,
  offline: <DismissCircle24Filled className="text-surface-400" />,
  unknown: <Warning24Filled className="text-surface-400" />,
};

const serviceTypeIcons: Record<string, React.ReactNode> = {
  application: <Server24Regular className="text-blue-400" />,
  database: <Database24Regular className="text-purple-400" />,
  queue: <Cloud24Regular className="text-cyan-400" />,
  external: <Globe24Regular className="text-emerald-400" />,
};

function formatRelativeTime(dateStr?: string): string {
  if (!dateStr) return 'Never';
  const date = new Date(dateStr);
  const now = new Date();
  const diffSecs = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
  return `${Math.floor(diffSecs / 3600)}h ago`;
}

export function HealthTab() {
  const [services, setServices] = useState<Service[]>([]);
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/observability/health');
      if (!response.ok) throw new Error('Failed to fetch health');

      const data = await response.json();
      setServices(data.services || []);
      setSummary(data.summary || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Use mock data
      setServices(getMockServices());
      setSummary(getMockSummary());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading && services.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="large" label="Loading health status..." />
      </div>
    );
  }

  const overallStatus = summary?.overall_status || 'unknown';

  return (
    <div className="space-y-6">
      {/* Overall Health Banner */}
      <div
        className={`p-4 rounded-lg border ${
          overallStatus === 'healthy'
            ? 'bg-emerald-500/10 border-emerald-500/30'
            : overallStatus === 'degraded'
            ? 'bg-amber-500/10 border-amber-500/30'
            : 'bg-red-500/10 border-red-500/30'
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {statusIcons[overallStatus]}
            <div>
              <Text size={500} weight="semibold">
                System Status:{' '}
                <span
                  className={
                    overallStatus === 'healthy'
                      ? 'text-emerald-400'
                      : overallStatus === 'degraded'
                      ? 'text-amber-400'
                      : 'text-red-400'
                  }
                >
                  {overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1)}
                </span>
              </Text>
              <Text size={200} className="text-surface-400">
                {summary?.total_services || 0} services monitored
              </Text>
            </div>
          </div>
          <Button
            appearance="subtle"
            icon={<ArrowClockwise24Regular />}
            onClick={fetchHealth}
          >
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded text-amber-400 text-sm">
          Using mock data: {error}
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-emerald-500/10 border-emerald-500/30">
            <CardHeader
              header={<Text weight="semibold" className="text-emerald-400">Healthy</Text>}
              description={
                <span className="text-3xl font-bold text-emerald-400">{summary.healthy_count}</span>
              }
            />
          </Card>
          <Card className="bg-amber-500/10 border-amber-500/30">
            <CardHeader
              header={<Text weight="semibold" className="text-amber-400">Degraded</Text>}
              description={
                <span className="text-3xl font-bold text-amber-400">{summary.degraded_count}</span>
              }
            />
          </Card>
          <Card className="bg-red-500/10 border-red-500/30">
            <CardHeader
              header={<Text weight="semibold" className="text-red-400">Unhealthy</Text>}
              description={
                <span className="text-3xl font-bold text-red-400">{summary.unhealthy_count}</span>
              }
            />
          </Card>
          <Card className="bg-surface-100 border-surface-200">
            <CardHeader
              header={<Text weight="semibold" className="text-surface-400">Offline</Text>}
              description={
                <span className="text-3xl font-bold text-surface-400">{summary.offline_count}</span>
              }
            />
          </Card>
        </div>
      )}

      {/* Service Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((service) => (
          <Card key={service.id} className="hover:bg-surface-100/50 transition-colors">
            <CardHeader
              image={serviceTypeIcons[service.service_type]}
              header={
                <div className="flex items-center justify-between w-full">
                  <Text weight="semibold">{service.name}</Text>
                  {statusIcons[service.status]}
                </div>
              }
              description={
                <div className="space-y-2 mt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-surface-400">Type</span>
                    <Badge appearance="outline">{service.service_type}</Badge>
                  </div>
                  {service.endpoint && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-surface-400">Endpoint</span>
                      <span className="font-mono text-xs truncate max-w-[150px]">{service.endpoint}</span>
                    </div>
                  )}
                  {service.port && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-surface-400">Port</span>
                      <span className="font-mono">{service.port}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-surface-400">Last Check</span>
                    <span>{formatRelativeTime(service.last_check)}</span>
                  </div>
                </div>
              }
            />
          </Card>
        ))}
      </div>

      {services.length === 0 && !isLoading && (
        <div className="text-center py-8 text-surface-400">
          No services configured
        </div>
      )}
    </div>
  );
}

// Mock data
function getMockServices(): Service[] {
  return [
    {
      id: 'odoo-core',
      name: 'Odoo CE Core',
      description: 'Main Odoo CE instance',
      service_type: 'application',
      endpoint: 'http://localhost:8069',
      health_endpoint: '/web/health',
      protocol: 'http',
      port: 8069,
      status: 'healthy',
      last_check: new Date(Date.now() - 30000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'postgres',
      name: 'PostgreSQL',
      description: 'Primary database',
      service_type: 'database',
      endpoint: 'localhost',
      protocol: 'tcp',
      port: 5432,
      status: 'healthy',
      last_check: new Date(Date.now() - 15000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n8n',
      name: 'n8n Workflows',
      description: 'Workflow automation engine',
      service_type: 'application',
      endpoint: 'http://localhost:5678',
      health_endpoint: '/healthz',
      protocol: 'http',
      port: 5678,
      status: 'healthy',
      last_check: new Date(Date.now() - 45000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'mcp-coordinator',
      name: 'MCP Coordinator',
      description: 'MCP routing and aggregation',
      service_type: 'application',
      endpoint: 'http://localhost:8766',
      health_endpoint: '/health',
      protocol: 'http',
      port: 8766,
      status: 'degraded',
      last_check: new Date(Date.now() - 60000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'supabase',
      name: 'Supabase',
      description: 'External BaaS',
      service_type: 'external',
      endpoint: 'https://spdtwktxdalcfigzeqrz.supabase.co',
      health_endpoint: '/rest/v1/',
      protocol: 'http',
      port: 443,
      status: 'healthy',
      last_check: new Date(Date.now() - 20000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'redis',
      name: 'Redis Cache',
      description: 'In-memory cache',
      service_type: 'queue',
      endpoint: 'localhost',
      protocol: 'tcp',
      port: 6379,
      status: 'offline',
      last_check: new Date(Date.now() - 300000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];
}

function getMockSummary(): HealthSummary {
  return {
    total_services: 6,
    healthy_count: 4,
    degraded_count: 1,
    unhealthy_count: 0,
    offline_count: 1,
    overall_status: 'degraded',
  };
}

export default HealthTab;
