import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";

import { Accordion } from "./accordion";

type FaqItem = {
  title: string;
  answer: string;
};

const faqItems: FaqItem[] = [
  {
    title: "How do I get started?",
    answer: "Sign up for a free account and follow our onboarding guide to set up your workspace in minutes.",
  },
  {
    title: "Can I upgrade or downgrade my plan?",
    answer: "Yes, you can change your plan at any time. Changes take effect immediately and are prorated.",
  },
  {
    title: "Is there a free trial?",
    answer: "Yes, all paid plans come with a 14-day free trial. No credit card required.",
  },
  {
    title: "What kind of support do you offer?",
    answer: "We offer email support for all plans, priority support for Professional, and dedicated support for Enterprise.",
  },
];

export function AccordionFaq() {
  return (
    <Section>
      <Heading subtitle="Find answers to common questions" tag="FAQ">
        <h4>Frequently asked questions</h4>
      </Heading>
      <div className="mx-auto flex w-full gap-8 md:max-w-(--breakpoint-sm) lg:max-w-(--breakpoint-md) lg:gap-14 lg:px-24 xl:max-w-(--breakpoint-xl)">
        <Accordion items={faqItems} />
      </div>
    </Section>
  );
}
