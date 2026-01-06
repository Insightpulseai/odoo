'use client';

import Image from 'next/image';
import Link from 'next/link';
import clsx from 'clsx';

interface HeroImage {
  src: string;
  alt: string;
  width?: number;
  height?: number;
}

interface CTA {
  label: string;
  href: string;
}

interface SolutionHeroProps {
  kicker?: string;
  title: string;
  subtitle: string;
  primaryCta?: CTA;
  secondaryCta?: CTA;
  backgroundImage?: string;
  heroImages?: HeroImage[];
}

export function SolutionHero({
  kicker,
  title,
  subtitle,
  primaryCta,
  secondaryCta,
  backgroundImage,
  heroImages,
}: SolutionHeroProps) {
  return (
    <section className="relative min-h-[90vh] flex items-center overflow-hidden">
      {/* Background */}
      {backgroundImage && (
        <div className="absolute inset-0 z-0">
          <Image
            src={backgroundImage}
            alt=""
            fill
            className="object-cover opacity-30"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-ipai-bg/80 via-ipai-bg/60 to-ipai-bg" />
        </div>
      )}

      {/* Decorative elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-ipai-primary/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-ipai-primary2/10 rounded-full blur-3xl" />

      <div className="solution-container relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="animate-fade-in">
            {kicker && (
              <span className="inline-block px-4 py-1.5 mb-6 text-sm font-semibold bg-ipai-primary/20 text-ipai-primary rounded-full">
                {kicker}
              </span>
            )}
            <h1 className="solution-heading mb-6 text-balance">
              {title}
            </h1>
            <p className="solution-subheading mb-8 text-balance">
              {subtitle}
            </p>
            <div className="flex flex-wrap gap-4">
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

          {/* Hero Images */}
          {heroImages && heroImages.length > 0 && (
            <div className="relative animate-slide-up animation-delay-200">
              <div className="relative flex items-end justify-center gap-4">
                {heroImages.map((img, idx) => (
                  <div
                    key={idx}
                    className={clsx(
                      'relative rounded-ipai-lg overflow-hidden shadow-ipai-lg',
                      idx === 0 ? 'w-full max-w-md' : 'w-1/3 max-w-[180px]'
                    )}
                  >
                    <Image
                      src={img.src}
                      alt={img.alt}
                      width={img.width || 400}
                      height={img.height || 300}
                      className="w-full h-auto"
                      priority={idx === 0}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
