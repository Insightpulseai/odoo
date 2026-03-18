'use client';

import Image from 'next/image';

interface Logo {
  name: string;
  src: string;
}

interface LogoStripProps {
  title?: string;
  logos: Logo[];
}

export function LogoStrip({ title, logos }: LogoStripProps) {
  if (!logos || logos.length === 0) return null;

  return (
    <section className="py-12 bg-zinc-900/30 border-y border-zinc-700">
      <div className="container mx-auto px-4">
        {title && (
          <p className="text-center text-sm text-zinc-400 mb-8 uppercase tracking-wider">
            {title}
          </p>
        )}
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
          {logos.map((logo) => (
            <div
              key={logo.name}
              className="grayscale hover:grayscale-0 transition-all flex items-center justify-center h-12"
            >
              <Image
                src={logo.src}
                alt={logo.name}
                width={120}
                height={48}
                className="max-h-10 w-auto object-contain"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
