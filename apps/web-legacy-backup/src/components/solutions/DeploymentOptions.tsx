'use client';

import {
  Server,
  Cloud,
  Globe,
  Download,
  LucideIcon,
} from 'lucide-react';
import clsx from 'clsx';

interface DeploymentOption {
  id: string;
  title: string;
  description: string;
  icon: string;
}

interface DeploymentOptionsProps {
  title?: string;
  items: DeploymentOption[] | string[];
}

const iconMap: Record<string, LucideIcon> = {
  server: Server,
  cloud: Cloud,
  globe: Globe,
  download: Download,
};

export function DeploymentOptions({ title, items }: DeploymentOptionsProps) {
  // Handle both simple string array and full object array
  const normalizedItems: DeploymentOption[] = items.map((item, idx) => {
    if (typeof item === 'string') {
      return {
        id: `option-${idx}`,
        title: item,
        description: '',
        icon: ['server', 'cloud', 'globe', 'download'][idx] || 'server',
      };
    }
    return item;
  });

  return (
    <section className="solution-section bg-ipai-surface/30">
      <div className="solution-container">
        <div className="glass-card p-8 md:p-12">
          {title && (
            <h2 className="text-2xl md:text-3xl font-bold text-center mb-10">
              {title}
            </h2>
          )}

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {normalizedItems.map((option, idx) => {
              const Icon = iconMap[option.icon] || Server;
              return (
                <div
                  key={option.id}
                  className={clsx(
                    'text-center p-6 rounded-ipai',
                    'bg-ipai-bg/50 border border-ipai-border',
                    'hover:border-ipai-primary/50 transition-colors'
                  )}
                >
                  <div className="w-14 h-14 mx-auto rounded-full bg-ipai-primary/20 flex items-center justify-center mb-4">
                    <Icon className="w-7 h-7 text-ipai-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">{option.title}</h3>
                  {option.description && (
                    <p className="text-sm text-ipai-muted">
                      {option.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
