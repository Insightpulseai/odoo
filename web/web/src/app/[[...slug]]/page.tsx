import { Hero } from "../_sections/hero";
import { FeaturesGrid } from "../_sections/features/features-grid";
import { FeaturesList } from "../_sections/features/features-list";
import { Pricing } from "../_sections/pricing";
import { AccordionFaq } from "../_sections/accordion-faq";
import { Callout } from "../_sections/callout-1";

export default function HomePage() {
  return (
    <>
      <Hero />
      <FeaturesGrid />
      <FeaturesList />
      <Pricing />
      <AccordionFaq />
      <Callout />
    </>
  );
}
