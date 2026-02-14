'use client';

import clsx from 'clsx';

type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  dot?: boolean;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  neutral: 'bg-surface-700 text-surface-200 border-surface-600',
};

const dotClasses: Record<BadgeVariant, string> = {
  success: 'bg-emerald-400',
  warning: 'bg-amber-400',
  error: 'bg-red-400',
  info: 'bg-blue-400',
  neutral: 'bg-surface-400',
};

export function Badge({ children, variant = 'neutral', size = 'sm', dot = false }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 border rounded-full font-medium',
        variantClasses[variant],
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
      )}
    >
      {dot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full',
            dotClasses[variant]
          )}
        />
      )}
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const statusMap: Record<string, BadgeVariant> = {
    SUCCESS: 'success',
    RUNNING: 'info',
    PENDING: 'neutral',
    FAILED: 'error',
    SKIPPED: 'neutral',
    CANCELLED: 'warning',
    healthy: 'success',
    degraded: 'warning',
    unhealthy: 'error',
    connected: 'success',
    disconnected: 'error',
    Active: 'success',
    'In Progress': 'info',
    Planning: 'neutral',
    Completed: 'success',
    'On Hold': 'warning',
    Open: 'warning',
    Mitigating: 'info',
    Closed: 'success',
    Accepted: 'neutral',
    critical: 'error',
    warning: 'warning',
    info: 'info',
    High: 'error',
    Medium: 'warning',
    Low: 'info',
  };

  return (
    <Badge variant={statusMap[status] || 'neutral'} dot>
      {status}
    </Badge>
  );
}
