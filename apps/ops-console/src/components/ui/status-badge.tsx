'use client';

import {
  Badge,
  makeStyles,
} from '@fluentui/react-components';
import type { BadgeProps } from '@fluentui/react-components';

export type StatusLevel =
  | 'operational'
  | 'partial'
  | 'scaffolded'
  | 'missing'
  | 'live'
  | 'stub'
  | 'blocked'
  | 'planned'
  | 'degraded'
  | 'down'
  | 'active'
  | 'paused'
  | 'error'
  | 'running'
  | 'completed'
  | 'queued'
  | 'success'
  | 'failure'
  | 'pending'
  | 'in_progress'
  | 'hardened';

interface StatusBadgeProps {
  status: string;
  label?: string;
  size?: BadgeProps['size'];
}

const statusConfig: Record<
  string,
  { color: BadgeProps['color']; label: string }
> = {
  operational: { color: 'success', label: 'Operational' },
  partial: { color: 'warning', label: 'Partial' },
  scaffolded: { color: 'brand', label: 'Scaffolded' },
  missing: { color: 'danger', label: 'Missing' },
  live: { color: 'success', label: 'Live' },
  stub: { color: 'warning', label: 'Stub' },
  blocked: { color: 'danger', label: 'Blocked' },
  planned: { color: 'informative', label: 'Planned' },
  degraded: { color: 'warning', label: 'Degraded' },
  down: { color: 'danger', label: 'Down' },
  active: { color: 'success', label: 'Active' },
  paused: { color: 'warning', label: 'Paused' },
  error: { color: 'danger', label: 'Error' },
  running: { color: 'brand', label: 'Running' },
  completed: { color: 'success', label: 'Completed' },
  queued: { color: 'informative', label: 'Queued' },
  success: { color: 'success', label: 'Success' },
  failure: { color: 'danger', label: 'Failure' },
  pending: { color: 'informative', label: 'Pending' },
  in_progress: { color: 'brand', label: 'In Progress' },
  hardened: { color: 'success', label: 'Hardened' },
};

const useStyles = makeStyles({
  badge: {
    textTransform: 'capitalize',
  },
});

export function StatusBadge({ status, label, size = 'medium' }: StatusBadgeProps) {
  const styles = useStyles();
  const config = statusConfig[status] ?? { color: 'informative' as const, label: status };

  return (
    <Badge
      className={styles.badge}
      appearance="filled"
      color={config.color}
      size={size}
    >
      {label ?? config.label}
    </Badge>
  );
}
