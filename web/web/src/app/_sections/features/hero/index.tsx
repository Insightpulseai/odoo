import Image from "next/image";

import { Heading } from "@/common/heading";
import { Section } from "@/common/layout";
import { ButtonLink } from "@/common/button";

import s from "./hero.module.scss";
import clsx from "clsx";

type FeatureHeroProps = {
  layout?: "image-bottom" | "image-right" | "full-image" | "gradient";
  title: string;
  subtitle?: string;
  tag?: string;
  image?: string;
  actions?: Array<{ id: string; href: string; label: string; intent: "primary" | "secondary" }>;
};

export default function FeatureHero({
  layout = "image-bottom",
  title,
  subtitle,
  tag,
  image,
  actions = [],
}: FeatureHeroProps) {
  switch (layout) {
    case "image-bottom": {
      return (
        <Section>
          <div className="flex flex-col gap-6">
            <Heading subtitle={subtitle} tag={tag}>
              <h4>{title}</h4>
            </Heading>
            <div className="flex justify-center gap-3">
              {actions.map((action) => (
                <ButtonLink
                  key={action.id}
                  href={action.href}
                  intent={action.intent}
                  size="lg"
                >
                  {action.label}
                </ButtonLink>
              ))}
            </div>
          </div>
          {image && (
            <Image
              priority
              alt={title}
              className="border-neutral-stroke1 block rounded-lg border"
              height={600}
              src={image}
              width={1200}
            />
          )}
        </Section>
      );
    }
    case "image-right": {
      return (
        <Section>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center">
            <div className="flex flex-1 flex-col gap-6 lg:pr-16">
              <Heading subtitle={subtitle} tag={tag} align="left">
                <h4>{title}</h4>
              </Heading>
              <div className="flex justify-start gap-3">
                {actions.map((action) => (
                  <ButtonLink
                    key={action.id}
                    href={action.href}
                    intent={action.intent}
                    size="lg"
                  >
                    {action.label}
                  </ButtonLink>
                ))}
              </div>
            </div>
            {image && (
              <Image
                priority
                alt={title}
                className="border-neutral-stroke1 block flex-1 rounded-lg border lg:w-1/2"
                height={600}
                src={image}
                width={600}
              />
            )}
          </div>
        </Section>
      );
    }
    case "full-image": {
      return (
        <>
          {image && (
            <Image
              priority
              alt={title}
              className="border-neutral-stroke1 block max-h-[720px] w-full border-y border-t-0 object-cover"
              height={720}
              src={image}
              width={1920}
            />
          )}
          <Section>
            <div className="flex items-center justify-between self-stretch">
              <Heading subtitle={subtitle} tag={tag} align="left">
                <h4>{title}</h4>
              </Heading>
              {actions.length > 0 ? (
                <div className="flex gap-3">
                  {actions.map((action) => (
                    <ButtonLink
                      key={action.id}
                      href={action.href}
                      intent={action.intent}
                      size="lg"
                    >
                      {action.label}
                    </ButtonLink>
                  ))}
                </div>
              ) : null}
            </div>
          </Section>
        </>
      );
    }
    case "gradient": {
      return (
        <Section>
          <div className="z-10 flex flex-col items-center gap-8">
            <Heading subtitle={subtitle} tag={tag}>
              <h4>{title}</h4>
            </Heading>
            <div className="flex gap-3">
              {actions.map((action) => (
                <ButtonLink
                  key={action.id}
                  href={action.href}
                  intent={action.intent}
                  size="lg"
                >
                  {action.label}
                </ButtonLink>
              ))}
            </div>
          </div>
          {/* Gradient */}
          <div
            className={clsx(
              "absolute -top-1/2 left-1/2 z-0 h-[400px] w-[60vw] -translate-x-1/2 scale-150 rounded-[50%]",
              s.gradient,
            )}
          />
        </Section>
      );
    }
    default: {
      return null;
    }
  }
}
