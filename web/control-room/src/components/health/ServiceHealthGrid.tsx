'use client';

import { Card } from '@/components/common/Card';
import { useServiceHealth, getStatusColor, getStatusBadgeVariant } from '@/hooks/useServiceHealth';
import type { ServiceHealth } from '@/lib/supabase';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Server,
  Activity,
  Zap,
  Database,
  BarChart2,
  Bot,
} from 'lucide-react';
import clsx from 'clsx';

const SERVICE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  'odoo-core': Server,
  'odoo-marketing': Server,
  'odoo-accounting': Server,
  superset: BarChart2,
  n8n: Zap,
  'mcp-coordinator': Bot,
  supabase: Database,
};

function StatusIcon({ status }: { status: ServiceHealth['status'] }) {
  switch (status) {
    case 'healthy':
      return <CheckCircle2 className="h-5 w-5 text-green-400" />;
    case 'unhealthy':
      return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
    case 'unreachable':
    case 'error':
      return <XCircle className="h-5 w-5 text-red-400" />;
    default:
      return <Loader2 className="h-5 w-5 text-surface-400 animate-spin" />;
  }
}

interface ServiceCardProps {
  service: ServiceHealth;
}

function ServiceCard({ service }: ServiceCardProps) {
  const Icon = SERVICE_ICONS[service.name] || Server;

  return (
    <Card className="p-4 hover:bg-surface-100/50 transition-colors cursor-pointer">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div
            className={clsx(
              'p-2 rounded-lg',
              service.status === 'healthy' ? 'bg-green-500/10' : 'bg-surface-100'
            )}
          >
            <Icon className="h-5 w-5 text-surface-200" />
          </div>
          <div>
            <div className="font-medium capitalize">
              {service.name.replace(/-/g, ' ')}
            </div>
            <div className="text-sm text-surface-300">
              {service.responseTime}ms
            </div>
          </div>
        </div>
        <StatusIcon status={service.status} />
      </div>

      {service.error && (
        <div className="mt-3 text-xs text-red-400 font-mono truncate">
          {service.error}
        </div>
      )}

      {service.statusCode && service.statusCode !== 200 && (
        <div className="mt-2 text-xs text-surface-300">
          HTTP {service.statusCode}
        </div>
      )}
    </Card>
  );
}

interface ServiceHealthGridProps {
  services?: ServiceHealth[];
  compact?: boolean;
}

export function ServiceHealthGrid({ services, compact }: ServiceHealthGridProps) {
  const { data, isLoading, error } = useServiceHealth();
  const serviceList = services || data?.services || [];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i} className="p-4 animate-pulse">
            <div className="h-16 bg-surface-100 rounded" />
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center text-red-400">
          <AlertTriangle className="h-5 w-5 mr-2" />
          Failed to load service health
        </div>
      </Card>
    );
  }

  return (
    <div>
      {!compact && (
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Service Health</h3>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-surface-400" />
            <span className="text-sm text-surface-300">
              {data?.healthy}/{data?.total} healthy
            </span>
          </div>
        </div>
      )}

      <div
        className={clsx(
          'grid gap-4',
          compact
            ? 'grid-cols-2 md:grid-cols-3'
            : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
        )}
      >
        {serviceList.map((service) => (
          <ServiceCard key={service.name} service={service} />
        ))}
      </div>
    </div>
  );
}

// Status banner for overall health
export function HealthStatusBanner() {
  const { data, isLoading } = useServiceHealth();

  if (isLoading) return null;

  const status = data?.status;
  const bgColor =
    status === 'healthy'
      ? 'bg-green-500/10 border-green-500/30'
      : status === 'degraded'
        ? 'bg-yellow-500/10 border-yellow-500/30'
        : 'bg-red-500/10 border-red-500/30';

  const textColor =
    status === 'healthy'
      ? 'text-green-400'
      : status === 'degraded'
        ? 'text-yellow-400'
        : 'text-red-400';

  return (
    <div className={clsx('p-3 rounded-lg border flex items-center gap-2', bgColor)}>
      {status === 'healthy' ? (
        <CheckCircle2 className={clsx('h-5 w-5', textColor)} />
      ) : status === 'degraded' ? (
        <AlertTriangle className={clsx('h-5 w-5', textColor)} />
      ) : (
        <XCircle className={clsx('h-5 w-5', textColor)} />
      )}
      <span className={clsx('font-medium capitalize', textColor)}>
        {status === 'healthy'
          ? 'All systems operational'
          : status === 'degraded'
            ? 'Some services experiencing issues'
            : 'System outage detected'}
      </span>
      <span className="text-surface-300 ml-auto text-sm">
        {data?.healthy}/{data?.total} services healthy
      </span>
    </div>
  );
}
