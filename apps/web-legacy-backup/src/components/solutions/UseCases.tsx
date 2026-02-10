'use client';

import Image from 'next/image';
import Link from 'next/link';
import { FileDown, ChevronRight } from 'lucide-react';
import clsx from 'clsx';

interface Artifact {
  label: string;
  meta?: string;
  href?: string;
}

interface UseCase {
  id?: string;
  title: string;
  description: string;
  image?: string;
  steps?: string[];
  artifacts?: Artifact[];
}

interface UseCasesProps {
  title?: string;
  subtitle?: string;
  items: UseCase[];
}

export function UseCases({ title, subtitle, items }: UseCasesProps) {
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

        <div className="space-y-16">
          {items.map((useCase, idx) => (
            <div
              key={useCase.id || idx}
              className={clsx(
                'grid lg:grid-cols-2 gap-8 items-center',
                idx % 2 === 1 && 'lg:grid-flow-dense'
              )}
            >
              {/* Content */}
              <div className={clsx(idx % 2 === 1 && 'lg:col-start-2')}>
                <h3 className="text-2xl md:text-3xl font-bold mb-4">
                  {useCase.title}
                </h3>
                <p className="text-ipai-muted mb-6">{useCase.description}</p>

                {/* Steps */}
                {useCase.steps && useCase.steps.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-ipai-muted uppercase tracking-wider mb-3">
                      Workflow Steps
                    </h4>
                    <ol className="space-y-2">
                      {useCase.steps.map((step, stepIdx) => (
                        <li
                          key={stepIdx}
                          className="flex items-center gap-3 text-sm"
                        >
                          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-ipai-primary/20 text-ipai-primary text-xs font-semibold flex items-center justify-center">
                            {stepIdx + 1}
                          </span>
                          {step}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* Artifacts */}
                {useCase.artifacts && useCase.artifacts.length > 0 && (
                  <div className="flex flex-wrap gap-3">
                    {useCase.artifacts.map((artifact, artIdx) => (
                      <Link
                        key={artIdx}
                        href={artifact.href || '#'}
                        className={clsx(
                          'inline-flex items-center gap-2 px-4 py-2 rounded-ipai-sm',
                          'bg-ipai-surface border border-ipai-border',
                          'hover:border-ipai-primary/50 transition-colors',
                          'text-sm'
                        )}
                      >
                        <FileDown className="w-4 h-4 text-ipai-primary" />
                        <span>{artifact.label}</span>
                        {artifact.meta && (
                          <span className="text-ipai-faint text-xs">
                            {artifact.meta}
                          </span>
                        )}
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* Image */}
              <div
                className={clsx(
                  'relative aspect-video rounded-ipai-lg overflow-hidden',
                  'bg-ipai-surface border border-ipai-border',
                  idx % 2 === 1 && 'lg:col-start-1 lg:row-start-1'
                )}
              >
                {useCase.image ? (
                  <Image
                    src={useCase.image}
                    alt={useCase.title}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-ipai-faint">
                      <ChevronRight className="w-12 h-12 mx-auto opacity-50" />
                      <p className="text-sm mt-2">Visual placeholder</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
