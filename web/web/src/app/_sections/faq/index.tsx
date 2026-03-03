import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";

export type FaqQuestion = {
  title: string;
  answer: string;
};

export type Faq = {
  heading: {
    title: string;
    subtitle?: string;
    tag?: string;
    align?: "center" | "left" | "right" | "none" | null;
  };
  questions: {
    items: FaqQuestion[];
  };
};

const defaultFaqData: Faq = {
  heading: {
    title: "Frequently asked questions",
    subtitle: "Everything you need to know",
    tag: "FAQ",
  },
  questions: {
    items: [
      { title: "What is included in the free plan?", answer: "The free plan includes up to 5 users, basic analytics, and email support." },
      { title: "How does billing work?", answer: "Billing is done monthly or annually. Annual billing saves you 20%." },
      { title: "Can I cancel anytime?", answer: "Yes, you can cancel your subscription at any time with no penalties." },
    ],
  },
};

export function Faq(faq: Faq = defaultFaqData) {
  return (
    <Section>
      <Heading {...faq.heading}>
        <h4>{faq.heading.title}</h4>
      </Heading>
      <ul className="mx-auto flex w-full grid-cols-3 flex-col place-content-start items-start gap-8 self-stretch lg:grid lg:gap-14 lg:px-24">
        {faq.questions.items.map((question) => (
          <li key={question.title} className="flex flex-col gap-1.5">
            <p className="leading-relaxed font-medium tracking-tighter sm:text-lg">
              {question.title}
            </p>
            <p className="text-neutral-fg3 text-sm leading-relaxed tracking-tight sm:text-base">
              {question.answer}
            </p>
          </li>
        ))}
      </ul>
    </Section>
  );
}
