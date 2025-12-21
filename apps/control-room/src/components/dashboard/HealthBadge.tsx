'use client';

import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import clsx from 'clsx';

type HealthStatus = 'healthy' | 'degraded' | 'unhealthy';

interface HealthBadgeProps {
  status: HealthStatus;
  label?: string;
  showIcon?: boolean;
}

const statusConfig = {
  healthy: {
    icon: CheckCircle,
    label: 'Healthy',
    bgColor: 'bg-emerald-500/20',
    textColor: 'text-emerald-400',
    borderColor: 'border-emerald-500/30',
  },
  degraded: {
    icon: AlertTriangle,
    label: 'Degraded',
    bgColor: 'bg-amber-500/20',
    textColor: 'text-amber-400',
    borderColor: 'border-amber-500/30',
  },
  unhealthy: {
    icon: XCircle,
    label: 'Unhealthy',
    bgColor: 'bg-red-500/20',
    textColor: 'text-red-400',
    borderColor: 'border-red-500/30',
  },
};

export function HealthBadge({ status, label, showIcon = true }: HealthBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border',
        config.bgColor,
        config.textColor,
        config.borderColor
      )}
    >
      {showIcon && <Icon className="h-4 w-4" />}
      {label || config.label}
    </span>
  );
}

interface ServiceHealthProps {
  services: {
    databricks: 'connected' | 'disconnected';
    notion: 'connected' | 'disconnected';
  };
}

export function ServiceHealth({ services }: ServiceHealthProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span
          className={clsx(
            'h-2 w-2 rounded-full',
            services.databricks === 'connected' ? 'bg-emerald-400' : 'bg-red-400'
          )}
        />
        <span className="text-sm text-surface-200">Databricks</span>
      </div>
      <div className="flex items-center gap-2">
        <span
          className={clsx(
            'h-2 w-2 rounded-full',
            services.notion === 'connected' ? 'bg-emerald-400' : 'bg-red-400'
          )}
        />
        <span className="text-sm text-surface-200">Notion</span>
      </div>
    </div>
  );
}
