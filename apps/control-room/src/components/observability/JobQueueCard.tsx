'use client';

import { Card } from '@/components/common/Card';
import { useMCPJobStats } from '@/hooks/useMCPJobs';
import { Clock, AlertTriangle, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import clsx from 'clsx';

interface StatItemProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down' | 'neutral';
}

function StatItem({ label, value, icon, color = 'text-surface-200' }: StatItemProps) {
  return (
    <div className="flex items-center gap-3">
      <div className={clsx('p-2 rounded-lg bg-surface-100/50', color)}>
        {icon}
      </div>
      <div>
        <div className="text-2xl font-semibold">{value}</div>
        <div className="text-sm text-surface-300">{label}</div>
      </div>
    </div>
  );
}

export function JobQueueCard() {
  const { data: stats, isLoading, error } = useMCPJobStats();

  if (isLoading) {
    return (
      <Card>
        <div className="flex items-center justify-center h-48">
          <Loader2 className="h-6 w-6 animate-spin text-surface-400" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="flex items-center justify-center h-48 text-red-400">
          <AlertTriangle className="h-5 w-5 mr-2" />
          Failed to load job stats
        </div>
      </Card>
    );
  }

  const successRateColor =
    (stats?.successRate ?? 100) >= 90
      ? 'text-green-400'
      : (stats?.successRate ?? 100) >= 70
        ? 'text-yellow-400'
        : 'text-red-400';

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Job Queue (24h)</h3>
        <div className={clsx('text-sm font-medium', successRateColor)}>
          {stats?.successRate ?? 100}% Success Rate
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <StatItem
          label="Queued"
          value={stats?.queued ?? 0}
          icon={<Clock className="h-5 w-5" />}
          color="text-blue-400"
        />
        <StatItem
          label="Processing"
          value={stats?.processing ?? 0}
          icon={<Loader2 className="h-5 w-5 animate-spin" />}
          color="text-yellow-400"
        />
        <StatItem
          label="Completed"
          value={stats?.completed ?? 0}
          icon={<CheckCircle2 className="h-5 w-5" />}
          color="text-green-400"
        />
        <StatItem
          label="Failed"
          value={stats?.failed ?? 0}
          icon={<XCircle className="h-5 w-5" />}
          color="text-red-400"
        />
      </div>

      {(stats?.deadLetter ?? 0) > 0 && (
        <div className="mt-6 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <span className="text-red-400 font-medium">
            {stats?.deadLetter} jobs in dead letter queue
          </span>
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-surface-100">
        <div className="flex items-center justify-between text-sm text-surface-300">
          <span>Avg Duration</span>
          <span className="font-mono">
            {stats?.avgDurationMs ? `${(stats.avgDurationMs / 1000).toFixed(2)}s` : '-'}
          </span>
        </div>
      </div>
    </Card>
  );
}
