'use client';

import { Cloud, Server, Globe, LucideIcon } from 'lucide-react';
import cn from 'classnames';

interface DeploymentOption {
  id: string;
  title: string;
  description: string;
  icon: string;
}

interface DeploymentOptionsProps {
  title?: string;
  items: DeploymentOption[];
}

const iconMap: Record<string, LucideIcon> = {
  cloud: Cloud,
  server: Server,
  globe: Globe,
  saas: Cloud,
  onpremise: Server,
  hybrid: Globe
};

export function DeploymentOptions({ title, items }: DeploymentOptionsProps) {
  return (
    <section className="py-16 md:py-24 bg-zinc-900/30">
      <div className="container mx-auto px-4">
        {title && (
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-white">
            {title}
          </h2>
        )}

        <div className="grid md:grid-cols-3 gap-6">
          {items.map((option) => {
            const Icon = iconMap[option.icon] || Cloud;
            return (
              <div
                key={option.id}
                className={cn(
                  'bg-zinc-900/50 border border-zinc-700 rounded-lg p-6',
                  'transition-all duration-300',
                  'hover:border-emerald-500/50 hover:shadow-lg'
                )}
              >
                <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-emerald-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2 text-white">
                  {option.title}
                </h3>
                <p className="text-zinc-400">{option.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
