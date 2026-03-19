'use client';

import Link from 'next/link';
import Image from 'next/image';
import { FileText, BookOpen, Briefcase, LucideIcon } from 'lucide-react';
import cn from 'classnames';

interface Resource {
  type: 'guide' | 'blog' | 'brief' | 'case-study';
  title: string;
  description?: string;
  href: string;
  thumb?: string;
}

interface ResourceGridProps {
  title?: string;
  items: Resource[];
}

const iconMap: Record<string, LucideIcon> = {
  guide: FileText,
  blog: BookOpen,
  brief: FileText,
  'case-study': Briefcase
};

export function ResourceGrid({ title, items }: ResourceGridProps) {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        {title && (
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-white">
            {title}
          </h2>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((resource, idx) => {
            const Icon = iconMap[resource.type] || FileText;
            return (
              <Link
                key={idx}
                href={resource.href}
                className={cn(
                  'group bg-zinc-900/50 border border-zinc-700 rounded-lg overflow-hidden',
                  'transition-all duration-300',
                  'hover:border-pink-500/50 hover:shadow-lg'
                )}
              >
                {resource.thumb && (
                  <div className="relative h-48 overflow-hidden">
                    <Image
                      src={resource.thumb}
                      alt={resource.title}
                      fill
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="w-4 h-4 text-pink-400" />
                    <span className="text-xs text-zinc-500 uppercase tracking-wider">
                      {resource.type.replace('-', ' ')}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-white group-hover:text-pink-400 transition-colors">
                    {resource.title}
                  </h3>
                  {resource.description && (
                    <p className="text-sm text-zinc-400">{resource.description}</p>
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
