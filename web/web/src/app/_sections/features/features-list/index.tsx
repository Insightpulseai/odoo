import { CheckIcon } from "@radix-ui/react-icons";

import { Section } from "@/common/layout";
import { Heading } from "@/common/heading";
import Image from "next/image";

type FeatureCard = {
  title: string;
  description: string;
  image: string;
  characteristics: string[];
};

const featureCards: FeatureCard[] = [
  {
    title: "Financial Management",
    description: "Complete accounting, invoicing, and expense management in one place.",
    image: "/images/features/finance.png",
    characteristics: ["Automated invoicing", "Expense tracking", "Financial reports"],
  },
  {
    title: "Project Management",
    description: "Plan, track, and deliver projects on time with powerful project tools.",
    image: "/images/features/projects.png",
    characteristics: ["Task management", "Time tracking", "Resource planning"],
  },
];

export function FeaturesList() {
  return (
    <Section container="default">
      <Heading subtitle="Comprehensive tools for every department" tag="Capabilities">
        <h4>Built for your entire organization</h4>
      </Heading>
      <div className="flex flex-col gap-6">
        {featureCards.map((item) => (
          <article
            key={item.title}
            className="flex min-h-96 w-full max-w-[380px] flex-col rounded-lg border border-neutral-stroke1 bg-neutral-bg2 p-px sm:max-w-full md:w-full md:flex-row md:odd:flex-row-reverse xl:gap-16"
          >
            <figure className="p-2 md:h-auto md:w-[360px] lg:w-[480px] xl:w-[560px]">
              <Image
                alt={item.title}
                className="block aspect-video h-[200px] w-full rounded-lg border border-neutral-stroke1 object-cover md:h-full"
                height={374}
                src={item.image}
                width={560}
              />
            </figure>
            <div className="flex flex-col gap-8 p-5 pt-6 md:flex-1 md:p-10">
              <div className="flex flex-col items-start gap-2">
                <h5 className="text-2xl font-medium text-neutral-fg1 md:text-3xl">
                  {item.title}
                </h5>
                <p className="font-normal text-neutral-fg2 md:text-lg">
                  {item.description}
                </p>
              </div>
              <ul className="flex flex-col items-start gap-3 pl-2 md:text-lg">
                {item.characteristics.map((char) => (
                  <li
                    key={char}
                    className="flex items-center gap-4 font-normal text-neutral-fg2"
                  >
                    <span className="flex size-6 items-center justify-center rounded-full bg-neutral-bg3">
                      <CheckIcon className="text-neutral-fg3" />
                    </span>
                    {char}
                  </li>
                ))}
              </ul>
            </div>
          </article>
        ))}
      </div>
    </Section>
  );
}
