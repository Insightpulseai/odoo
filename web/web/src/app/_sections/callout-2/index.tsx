import { Section } from "@/common/layout";
import { ButtonLink } from "@/common/button";

export function Callout2() {
  return (
    <Section>
      <article className="bg-brand/10 flex flex-col justify-center gap-9 self-stretch rounded-xl p-6 lg:flex-row lg:justify-between lg:p-10">
        <div className="flex flex-col gap-2">
          <h4 className="text-neutral-fg1 text-3xl font-medium lg:text-4xl">
            Transform your business today
          </h4>
          <p className="text-neutral-fg2 text-lg lg:text-xl">
            Start your free trial and see results in minutes.
          </p>
        </div>
        <div className="grid grid-cols-2 items-center gap-2 md:flex lg:flex-col">
          <ButtonLink href="/sign-up" intent="primary">
            Get started
          </ButtonLink>
          <ButtonLink href="/contact" intent="secondary">
            Contact sales
          </ButtonLink>
        </div>
      </article>
    </Section>
  );
}
