import Image from "next/image";

import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";

const features = [
  {
    title: "Intelligent Automation",
    description: "Automate complex workflows with AI-powered tools that learn and adapt to your business needs.",
    icon: "/icons/automation.svg",
  },
  {
    title: "Seamless Integration",
    description: "Connect with your favorite tools and services through our extensive integration marketplace.",
    icon: "/icons/integration.svg",
  },
  {
    title: "Enterprise Security",
    description: "Bank-grade security with end-to-end encryption, SSO, and comprehensive audit trails.",
    icon: "/icons/security.svg",
  },
];

export function BigFeature() {
  return (
    <Section container="default">
      <Image
        alt="Platform overview"
        className="block rounded-xl border border-neutral-stroke1 md:order-3 md:w-full"
        height={600}
        src="/images/features/big-feature.png"
        width={1216}
      />
      <Heading subtitle="One platform, infinite possibilities" tag="Platform">
        <h4>Everything you need to succeed</h4>
      </Heading>
      <div className="flex w-full flex-col items-start gap-4 md:order-2 md:grid md:grid-cols-3 md:gap-16">
        {features.map(({ title, description, icon }) => (
          <article key={title} className="flex flex-col gap-4">
            <figure className="flex size-9 items-center justify-center rounded-full border border-neutral-stroke1 bg-neutral-bg2 p-2">
              <Image
                alt={title}
                height={18}
                src={icon}
                width={18}
              />
            </figure>
            <div className="flex flex-col items-start gap-1">
              <h5 className="text-lg font-medium">{title}</h5>
              <p className="text-neutral-fg3">{description}</p>
            </div>
          </article>
        ))}
      </div>
    </Section>
  );
}
