'use client';

import Image from 'next/image';
import cn from 'classnames';

interface UseCase {
  id?: string;
  title: string;
  description: string;
  image?: string;
  steps?: string[];
  artifacts?: Array<{
    label: string;
    meta?: string;
    href?: string;
  }>;
}

interface UseCasesProps {
  title?: string;
  items: UseCase[];
}

export function UseCases({ title, items }: UseCasesProps) {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        {title && (
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-white">
            {title}
          </h2>
        )}

        <div className="space-y-12">
          {items.map((useCase, idx) => (
            <div
              key={useCase.id || idx}
              className={cn(
                'grid md:grid-cols-2 gap-8 items-center',
                idx % 2 === 1 && 'md:grid-flow-dense'
              )}
            >
              {/* Image */}
              {useCase.image && (
                <div
                  className={cn(
                    'relative rounded-lg overflow-hidden',
                    idx % 2 === 1 && 'md:col-start-2'
                  )}
                >
                  <Image
                    src={useCase.image}
                    alt={useCase.title}
                    width={600}
                    height={400}
                    className="w-full h-auto"
                  />
                </div>
              )}

              {/* Content */}
              <div>
                <h3 className="text-2xl font-bold mb-4 text-white">
                  {useCase.title}
                </h3>
                <p className="text-zinc-300 mb-6">{useCase.description}</p>

                {useCase.steps && useCase.steps.length > 0 && (
                  <ol className="space-y-2 mb-6">
                    {useCase.steps.map((step, stepIdx) => (
                      <li
                        key={stepIdx}
                        className="flex items-start gap-3 text-sm text-zinc-400"
                      >
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-pink-500/20 text-pink-400 flex items-center justify-center text-xs font-bold">
                          {stepIdx + 1}
                        </span>
                        {step}
                      </li>
                    ))}
                  </ol>
                )}

                {useCase.artifacts && useCase.artifacts.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {useCase.artifacts.map((artifact, artIdx) => (
                      <span
                        key={artIdx}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-zinc-900 border border-zinc-700 rounded-full text-xs text-zinc-400"
                      >
                        {artifact.label}
                        {artifact.meta && (
                          <span className="text-zinc-500">• {artifact.meta}</span>
                        )}
                      </span>
                    ))}
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
