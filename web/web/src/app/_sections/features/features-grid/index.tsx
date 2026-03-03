import Image from "next/image";

import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";
import { ButtonLink } from "@/common/button";

const features = [
  {
    id: "1",
    title: "Workflow Automation",
    description: "Automate repetitive tasks and streamline your business processes with powerful workflow tools.",
    icon: "/icons/workflow.svg",
  },
  {
    id: "2",
    title: "Real-time Analytics",
    description: "Get instant insights into your business performance with comprehensive dashboards and reports.",
    icon: "/icons/analytics.svg",
  },
  {
    id: "3",
    title: "Team Collaboration",
    description: "Work together seamlessly with built-in communication tools and shared workspaces.",
    icon: "/icons/collaboration.svg",
  },
];

export function FeaturesGrid() {
  return (
    <Section>
      <Heading subtitle="Everything you need to run your business" tag="Features">
        <h4>Powerful features for modern teams</h4>
      </Heading>
      <div className="grid w-full grid-cols-1 gap-4 lg:grid-cols-3 lg:gap-5">
        {features.map(({ id, title, description, icon }) => (
          <article
            key={id}
            className="border-neutral-stroke1 flex flex-col gap-4 rounded-lg border p-4 [box-shadow:_70px_-20px_130px_0px_rgba(255,255,255,0.05)_inset]"
          >
            <figure className="border-neutral-stroke1 bg-neutral-bg2 flex size-9 items-center justify-center rounded-full border p-2">
              <Image
                alt={title}
                height={18}
                src={icon}
                width={18}
              />
            </figure>
            <div className="flex flex-col items-start gap-1">
              <h5 className="text-lg font-medium">{title}</h5>
              <p className="text-neutral-fg2 text-pretty">
                {description}
              </p>
            </div>
          </article>
        ))}
      </div>
      <div className="flex items-center justify-center gap-3 md:order-3">
        <ButtonLink
          href="/features"
          intent="primary"
          size="lg"
        >
          Explore all features
        </ButtonLink>
      </div>
    </Section>
  );
}
