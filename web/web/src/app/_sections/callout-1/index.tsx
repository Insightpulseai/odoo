import clsx from "clsx";

import { Section } from "@/common/layout";
import { ButtonLink } from "@/common/button";

import s from "./callout-1.module.scss";

export function Callout() {
  return (
    <Section>
      <article className="border-neutral-stroke1 bg-neutral-bg2 relative flex flex-col items-center justify-center gap-9 self-stretch overflow-hidden rounded-xl border p-6">
        {/* Lines and bg  */}
        <div
          className={clsx(
            "absolute top-10 left-0 h-px w-full bg-linear-to-l from-black/40 to-transparent",
            s.line,
          )}
        />
        <div
          className={clsx(
            "absolute bottom-[72px] left-0 h-px w-full bg-linear-to-l from-black/40 to-transparent",
            s.line,
          )}
        />
        <div
          className={clsx(
            "absolute bottom-7 left-0 h-px w-full bg-linear-to-l from-black/40 to-transparent",
            s.line,
          )}
        />
        <div className="bg-neutral-bg2 absolute top-0 left-0 z-10 h-full w-full blur-3xl filter" />
        {/* -------- */}
        <div className="relative z-20 flex flex-col items-center gap-2 text-center">
          <h4 className="text-neutral-fg1 text-center text-3xl font-medium tracking-tighter sm:max-w-full sm:px-0 md:text-4xl">
            Ready to get started?
          </h4>
          <p className="text-neutral-fg2 text-lg md:text-xl">
            Join thousands of businesses already using our platform.
          </p>
        </div>
        <div className="relative z-10 flex items-center gap-2">
          <ButtonLink href="/sign-up" intent="primary">
            Start free trial
          </ButtonLink>
          <ButtonLink href="/demo" intent="secondary">
            Book a demo
          </ButtonLink>
        </div>
      </article>
    </Section>
  );
}
