'use client';

import Image from 'next/image';
import Link from 'next/link';
import { FileText, BookOpen, Briefcase, Newspaper } from 'lucide-react';
import clsx from 'clsx';

interface Resource {
  type: 'guide' | 'blog' | 'brief' | 'case-study';
  title: string;
  description?: string;
  href: string;
  thumb?: string;
}

interface ResourceGridProps {
  title?: string;
  subtitle?: string;
  items: Resource[];
}

const typeConfig: Record<
  Resource['type'],
  { label: string; icon: typeof FileText; color: string }
> = {
  guide: { label: 'Guide', icon: BookOpen, color: 'text-blue-400' },
  blog: { label: 'Blog', icon: Newspaper, color: 'text-green-400' },
  brief: { label: 'Brief', icon: FileText, color: 'text-purple-400' },
  'case-study': { label: 'Case Study', icon: Briefcase, color: 'text-amber-400' },
};

export function ResourceGrid({ title, subtitle, items }: ResourceGridProps) {
  return (
    <section className="solution-section bg-ipai-surface/30">
      <div className="solution-container">
        {(title || subtitle) && (
          <div className="text-center mb-12">
            {title && (
              <h2 className="text-3xl md:text-4xl font-bold mb-4">{title}</h2>
            )}
            {subtitle && (
              <p className="solution-subheading mx-auto">{subtitle}</p>
            )}
          </div>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {items.map((resource, idx) => {
            const config = typeConfig[resource.type] || typeConfig.guide;
            const Icon = config.icon;

            return (
              <Link
                key={idx}
                href={resource.href}
                className={clsx(
                  'group glass-card overflow-hidden transition-all duration-300',
                  'hover:border-ipai-primary/50 hover:shadow-ipai-lg',
                  'hover:-translate-y-1'
                )}
              >
                {/* Thumbnail */}
                <div className="relative aspect-[16/10] bg-ipai-bg">
                  {resource.thumb ? (
                    <Image
                      src={resource.thumb}
                      alt={resource.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Icon className={clsx('w-12 h-12 opacity-30', config.color)} />
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={clsx('w-4 h-4', config.color)} />
                    <span className="text-xs font-semibold uppercase tracking-wider text-ipai-muted">
                      {config.label}
                    </span>
                  </div>
                  <h3 className="font-semibold line-clamp-2 group-hover:text-ipai-primary transition-colors">
                    {resource.title}
                  </h3>
                  {resource.description && (
                    <p className="mt-2 text-sm text-ipai-muted line-clamp-2">
                      {resource.description}
                    </p>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
