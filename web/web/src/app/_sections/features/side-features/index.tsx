import Image from "next/image";

import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";
import { ButtonLink } from "@/common/button";

const sideFeatures = [
  {
    title: "Advanced Reporting",
    subtitle: "Generate custom reports with drag-and-drop report builder. Export to PDF, Excel, or share via link.",
    icon: "/icons/reporting.svg",
  },
  {
    title: "API & Webhooks",
    subtitle: "Connect your existing tools with our comprehensive REST API and real-time webhooks.",
    icon: "/icons/api.svg",
  },
  {
    title: "Mobile App",
    subtitle: "Stay productive on the go with our fully-featured mobile application for iOS and Android.",
    icon: "/icons/mobile.svg",
  },
  {
    title: "Custom Workflows",
    subtitle: "Design and automate complex business workflows with our visual workflow builder.",
    icon: "/icons/workflows.svg",
  },
];

export function SideFeatures() {
  return (
    <Section
      className="relative lg:container lg:mx-auto lg:flex-row! lg:gap-0 lg:p-28"
      container="full"
    >
      <div className="relative top-0 container mx-auto shrink self-stretch px-6 lg:w-1/2 lg:pr-12 lg:pl-0 xl:pr-20">
        <div className="sticky top-[calc(var(--header-height)+40px)] bottom-0 flex flex-col gap-10">
          <Heading className="items-start" subtitle="Extend your platform with powerful add-ons" tag="Extensions">
            <h4>Do more with add-ons</h4>
          </Heading>
          <div className="flex items-center gap-3 md:order-3">
            <ButtonLink
              href="/features"
              intent="primary"
              size="lg"
            >
              View all features
            </ButtonLink>
          </div>
        </div>
      </div>
      <div className="w-full flex-1 shrink-0 lg:w-1/2 lg:flex-1">
        <div className="no-scrollbar flex gap-10 overflow-auto px-6 lg:flex-col lg:px-0">
          {sideFeatures.map(({ title, icon, subtitle }) => (
            <article
              key={title}
              className="border-neutral-stroke1 bg-neutral-bg2 flex w-[280px] shrink-0 flex-col gap-4 rounded-lg border p-4 lg:w-full lg:flex-row lg:p-5"
            >
              <figure className="bg-neutral-bg3 flex size-12 shrink-0 items-center justify-center rounded-full p-3">
                <Image
                  alt={title}
                  height={24}
                  src={icon}
                  width={24}
                />
              </figure>
              <div className="flex flex-col items-start gap-1">
                <h5 className="text-lg font-medium">{title}</h5>
                <p className="text-neutral-fg3 text-pretty">
                  {subtitle}
                </p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </Section>
  );
}
