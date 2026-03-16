'use client';

import { CheckCircle, AlertTriangle, XCircle, Info, RefreshCw, Plus } from 'lucide-react';
import clsx from 'clsx';
import { Card, CardHeader } from '@/components/common/Card';
import type { ActivityItem } from '@/types/models';

interface ActivityFeedProps {
  activities: ActivityItem[];
  maxItems?: number;
}

const statusConfig = {
  success: {
    icon: CheckCircle,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-amber-400',
    bgColor: 'bg-amber-400/10',
  },
  error: {
    icon: XCircle,
    color: 'text-red-400',
    bgColor: 'bg-red-400/10',
  },
  info: {
    icon: Info,
    color: 'text-blue-400',
    bgColor: 'bg-blue-400/10',
  },
};

const typeIcons = {
  job_run: RefreshCw,
  dq_issue: AlertTriangle,
  sync: RefreshCw,
  action: Plus,
};

function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export function ActivityFeed({ activities, maxItems = 10 }: ActivityFeedProps) {
  const displayedActivities = activities.slice(0, maxItems);

  return (
    <Card>
      <CardHeader title="Recent Activity" subtitle="Last 24 hours" />

      <div className="space-y-3">
        {displayedActivities.length === 0 ? (
          <p className="text-sm text-surface-200 text-center py-4">
            No recent activity
          </p>
        ) : (
          displayedActivities.map((activity) => {
            const config = statusConfig[activity.status];
            const StatusIcon = config.icon;
            const TypeIcon = typeIcons[activity.type];

            return (
              <div
                key={activity.id}
                className="flex items-start gap-3 p-3 rounded-lg bg-surface-900/50"
              >
                <div className={clsx('p-1.5 rounded-lg', config.bgColor)}>
                  <StatusIcon className={clsx('h-4 w-4', config.color)} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white truncate">
                      {activity.title}
                    </span>
                    <TypeIcon className="h-3.5 w-3.5 text-surface-400" />
                  </div>
                  {activity.description && (
                    <p className="text-xs text-surface-200 mt-0.5 truncate">
                      {activity.description}
                    </p>
                  )}
                </div>

                <span className="text-xs text-surface-400 whitespace-nowrap">
                  {formatTimeAgo(activity.timestamp)}
                </span>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}
