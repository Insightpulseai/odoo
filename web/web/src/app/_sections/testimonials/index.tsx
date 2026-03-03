import { Section } from "@/common/layout";
import { Heading } from "@/common/heading";

import { Slider } from "./slider";

export type TestimonialsSlider = {
  heading: {
    title: string;
    subtitle?: string;
    tag?: string;
    align?: "center" | "left" | "right" | "none" | null;
  };
  quotes: Array<{
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
  }>;
};

export function Testimonials({ heading, quotes }: TestimonialsSlider) {
  return (
    <div className="relative overflow-clip">
      <Section>
        <Slider quotes={quotes}>
          {heading.align === "none" ? (
            <div />
          ) : (
            <Heading className="self-stretch" {...heading}>
              <h4>{heading.title}</h4>
            </Heading>
          )}
        </Slider>
      </Section>
    </div>
  );
}
