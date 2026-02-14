'use client';

import {
  Shield,
  Lock,
  Activity,
  Settings,
  LucideIcon,
} from 'lucide-react';
import clsx from 'clsx';

interface Pillar {
  id?: string;
  title: string;
  description?: string;
  icon: string;
  points: string[];
}

interface PillarsProps {
  title?: string;
  subtitle?: string;
  items: Pillar[];
}

const iconMap: Record<string, LucideIcon> = {
  shield: Shield,
  lock: Lock,
  activity: Activity,
  pulse: Activity,
  settings: Settings,
  gear: Settings,
};

export function Pillars({ title, subtitle, items }: PillarsProps) {
  return (
    <section className="solution-section">
      <div className="solution-container">
        {(title || subtitle) && (
          <div className="text-center mb-16">
            {title && (
              <h2 className="text-3xl md:text-4xl font-bold mb-4">{title}</h2>
            )}
            {subtitle && (
              <p className="solution-subheading mx-auto">{subtitle}</p>
            )}
          </div>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {items.map((pillar, idx) => {
            const Icon = iconMap[pillar.icon] || Shield;
            return (
              <div
                key={pillar.id || idx}
                className={clsx(
                  'glass-card p-6 transition-all duration-300',
                  'hover:border-ipai-primary/50 hover:shadow-ipai-lg',
                  'animate-fade-in',
                  idx === 1 && 'animation-delay-100',
                  idx === 2 && 'animation-delay-200',
                  idx === 3 && 'animation-delay-300'
                )}
              >
                <div className="w-12 h-12 rounded-ipai bg-ipai-primary/20 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-ipai-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{pillar.title}</h3>
                {pillar.description && (
                  <p className="text-sm text-ipai-muted mb-4">
                    {pillar.description}
                  </p>
                )}
                <ul className="space-y-2">
                  {pillar.points.map((point, pointIdx) => (
                    <li
                      key={pointIdx}
                      className="flex items-start gap-2 text-sm text-ipai-muted"
                    >
                      <span className="w-1.5 h-1.5 mt-2 rounded-full bg-ipai-primary flex-shrink-0" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
