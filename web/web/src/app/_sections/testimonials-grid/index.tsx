import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";

import { TestimonialsGridClient } from "./testimonials-list";

export type QuoteFragment = {
  _id: string;
  quote: string;
  author: {
    _title: string;
    role?: string;
    image: { url: string; alt?: string | null };
    company: {
      _title: string;
      image?: { url: string; alt?: string | null } | null;
    };
  };
};

type TestimonialsGrid = {
  heading: {
    title: string;
    subtitle?: string;
    tag?: string;
    align?: "center" | "left" | "right" | "none" | null;
  };
  quotes: QuoteFragment[];
};

export function TestimonialsGrid({ heading, quotes }: TestimonialsGrid) {
  return (
    <Section>
      <Heading {...heading}>
        <h4>{heading.title}</h4>
      </Heading>
      <TestimonialsGridClient quotes={quotes} />
    </Section>
  );
}
