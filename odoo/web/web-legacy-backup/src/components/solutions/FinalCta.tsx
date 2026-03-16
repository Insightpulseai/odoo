'use client';

import Link from 'next/link';
import clsx from 'clsx';

interface CTA {
  label: string;
  href: string;
}

interface FinalCtaProps {
  title: string;
  subtitle?: string;
  primaryCta?: CTA;
  secondaryCta?: CTA;
}

export function FinalCta({
  title,
  subtitle,
  primaryCta,
  secondaryCta,
}: FinalCtaProps) {
  return (
    <section className="solution-section">
      <div className="solution-container">
        <div
          className={clsx(
            'relative overflow-hidden rounded-ipai-lg',
            'bg-gradient-to-br from-ipai-surface via-ipai-surface to-ipai-primary/10',
            'border border-ipai-border',
            'p-10 md:p-16 text-center'
          )}
        >
          {/* Decorative gradient */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-ipai-primary/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-ipai-primary2/5 rounded-full blur-3xl" />

          <div className="relative z-10">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-balance">
              {title}
            </h2>
            {subtitle && (
              <p className="solution-subheading mx-auto mb-8">{subtitle}</p>
            )}

            <div className="flex flex-wrap items-center justify-center gap-4">
              {primaryCta && (
                <Link
                  href={primaryCta.href}
                  className={clsx(
                    'inline-flex items-center px-8 py-4 rounded-ipai font-semibold',
                    'bg-ipai-primary text-ipai-bg hover:bg-ipai-primary2',
                    'transition-all duration-200 shadow-lg hover:shadow-xl',
                    'transform hover:-translate-y-0.5'
                  )}
                >
                  {primaryCta.label}
                </Link>
              )}
              {secondaryCta && (
                <Link
                  href={secondaryCta.href}
                  className={clsx(
                    'inline-flex items-center px-8 py-4 rounded-ipai font-semibold',
                    'bg-transparent border-2 border-ipai-border text-ipai-text',
                    'hover:border-ipai-primary hover:text-ipai-primary',
                    'transition-all duration-200'
                  )}
                >
                  {secondaryCta.label}
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
