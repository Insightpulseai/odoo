'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import clsx from 'clsx';
import { Card } from '@/components/common/Card';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

const variantClasses = {
  default: 'border-surface-700',
  success: 'border-emerald-500/30 bg-emerald-500/5',
  warning: 'border-amber-500/30 bg-amber-500/5',
  error: 'border-red-500/30 bg-red-500/5',
};

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
};

const trendColors = {
  up: 'text-emerald-400',
  down: 'text-red-400',
  neutral: 'text-surface-400',
};

export function KPICard({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  icon,
  variant = 'default',
}: KPICardProps) {
  const TrendIcon = trend ? trendIcons[trend] : null;

  return (
    <Card className={clsx(variantClasses[variant])}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-surface-200">{title}</p>
          <p className="mt-2 text-3xl font-bold text-white">{value}</p>
          {(subtitle || trendValue) && (
            <div className="mt-1 flex items-center gap-2">
              {trend && TrendIcon && (
                <span className={clsx('flex items-center gap-1 text-sm', trendColors[trend])}>
                  <TrendIcon className="h-4 w-4" />
                  {trendValue}
                </span>
              )}
              {subtitle && (
                <span className="text-sm text-surface-200">{subtitle}</span>
              )}
            </div>
          )}
        </div>
        {icon && (
          <div className="p-2 rounded-lg bg-surface-700/50">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
