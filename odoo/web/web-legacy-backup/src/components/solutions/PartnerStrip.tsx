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
    <section className="py-16">
      <div className="solution-container">
        {title && (
          <h2 className="text-2xl md:text-3xl font-bold text-center mb-10">
            {title}
          </h2>
        )}
        <div className="flex flex-wrap items-center justify-center gap-10 md:gap-16">
          {items.map((partner) => {
            const content = (
              <div className="logo-grayscale flex items-center justify-center h-12">
                <Image
                  src={partner.src}
                  alt={partner.name}
                  width={140}
                  height={48}
                  className="max-h-10 w-auto object-contain"
                />
              </div>
            );

            return partner.href ? (
              <Link
                key={partner.name}
                href={partner.href}
                target="_blank"
                rel="noopener noreferrer"
                className="block"
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
