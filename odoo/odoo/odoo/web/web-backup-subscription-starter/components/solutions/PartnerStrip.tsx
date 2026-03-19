'use client';

import Image from 'next/image';
import Link from 'next/link';

interface Partner {
  name: string;
  src: string;
  href?: string;
}

interface PartnerStripProps {
  title?: string;
  items: Partner[];
}

export function PartnerStrip({ title, items }: PartnerStripProps) {
  if (!items || items.length === 0) return null;

  return (
    <section className="py-12 border-y border-zinc-700">
      <div className="container mx-auto px-4">
        {title && (
          <p className="text-center text-sm text-zinc-400 mb-8 uppercase tracking-wider">
            {title}
          </p>
        )}
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
          {items.map((partner) => {
            const content = (
              <div className="grayscale hover:grayscale-0 transition-all flex items-center justify-center h-16">
                <Image
                  src={partner.src}
                  alt={partner.name}
                  width={140}
                  height={64}
                  className="max-h-12 w-auto object-contain"
                />
              </div>
            );

            return partner.href ? (
              <Link
                key={partner.name}
                href={partner.href}
                target="_blank"
                rel="noopener noreferrer"
              >
                {content}
              </Link>
            ) : (
              <div key={partner.name}>{content}</div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
