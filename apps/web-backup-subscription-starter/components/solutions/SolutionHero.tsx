'use client';

import Image from 'next/image';
import Link from 'next/link';
import cn from 'classnames';

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
  heroImages
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
          <div className="absolute inset-0 bg-gradient-to-b from-zinc-800/80 via-zinc-800/60 to-zinc-800" />
        </div>
      )}

      {/* Decorative elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />

      <div className="container mx-auto px-4 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="animate-fade-in">
            {kicker && (
              <span className="inline-block px-4 py-1.5 mb-6 text-sm font-semibold bg-pink-500/20 text-pink-400 rounded-full">
                {kicker}
              </span>
            )}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-white">
              {title}
            </h1>
            <p className="text-xl md:text-2xl text-zinc-300 mb-8">
              {subtitle}
            </p>
            <div className="flex flex-wrap gap-4">
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

          {/* Hero Images */}
          {heroImages && heroImages.length > 0 && (
            <div className="relative">
              <div className="relative flex items-end justify-center gap-4">
                {heroImages.map((img, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      'relative rounded-lg overflow-hidden shadow-2xl',
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
