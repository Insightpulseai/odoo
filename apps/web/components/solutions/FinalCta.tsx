'use client';

import Link from 'next/link';
import cn from 'classnames';

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
  secondaryCta
}: FinalCtaProps) {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div
          className={cn(
            'relative overflow-hidden rounded-lg',
            'bg-gradient-to-br from-zinc-900 via-zinc-900 to-pink-500/10',
            'border border-zinc-700',
            'p-10 md:p-16 text-center'
          )}
        >
          {/* Decorative gradient */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-pink-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />

          <div className="relative z-10">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
              {title}
            </h2>
            {subtitle && (
              <p className="text-xl text-zinc-300 max-w-3xl mx-auto mb-8">
                {subtitle}
              </p>
            )}

            <div className="flex flex-wrap items-center justify-center gap-4">
              {primaryCta && (
                <Link
                  href={primaryCta.href}
                  className={cn(
                    'inline-flex items-center px-8 py-4 rounded-lg font-semibold',
                    'bg-pink-500 text-white hover:bg-pink-600',
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
                  className={cn(
                    'inline-flex items-center px-8 py-4 rounded-lg font-semibold',
                    'bg-transparent border-2 border-zinc-600 text-white',
                    'hover:border-pink-500 hover:text-pink-400',
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
