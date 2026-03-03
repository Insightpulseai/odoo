import clsx from "clsx";

import { AvatarsGroup } from "@/common/avatars-group";
import { ButtonLink } from "@/common/button";

export function Hero() {
  return (
    <section className="relative min-h-[calc(630px-var(--header-height))] overflow-hidden pb-10">
      <div className="border-neutral-stroke1 absolute top-0 left-0 z-0 grid h-full w-full grid-cols-[clamp(28px,10vw,120px)_auto_clamp(28px,10vw,120px)] border-b">
        {/* Decorations */}
        <div className="col-span-1 flex h-full items-center justify-center" />
        <div className="border-neutral-stroke1 col-span-1 flex h-full items-center justify-center border-x" />
        <div className="col-span-1 flex h-full items-center justify-center" />
      </div>
      {/* --- */}
      <figure className="bg-brand/40 pointer-events-none absolute -bottom-[70%] left-1/2 z-0 block aspect-square w-[520px] -translate-x-1/2 rounded-full blur-[200px]" />
      <figure className="bg-neutral-bg1 pointer-events-none absolute top-[64px] left-[4vw] z-20 hidden aspect-square w-[32vw] rounded-full opacity-50 blur-[100px] md:block" />
      <figure className="bg-neutral-bg1 pointer-events-none absolute right-[7vw] bottom-[-50px] z-20 hidden aspect-square w-[30vw] rounded-full opacity-50 blur-[100px] md:block" />
      {/* --- */}
      <div className="divide-neutral-stroke1 relative z-10 flex flex-col divide-y pt-[35px]">
        <div className="flex flex-col items-center justify-end">
          <div className="border-neutral-stroke1 flex items-center gap-2 border! border-b-0! px-4 py-2">
            <AvatarsGroup>
              {/* Avatars placeholder */}
            </AvatarsGroup>
            <p className="text-neutral-fg3 text-sm tracking-tight">
              Trusted by thousands of users
            </p>
          </div>
        </div>
        <div>
          <div className="mx-auto flex min-h-[288px] max-w-[80vw] shrink-0 flex-col items-center justify-center gap-2 px-2 py-4 sm:px-16 lg:px-24">
            <h1 className="text-neutral-fg1 max-w-(--breakpoint-lg) text-center text-[clamp(32px,7vw,64px)] leading-none font-medium tracking-[-1.44px] text-pretty md:tracking-[-2.16px]">
              Your all-in-one business platform
            </h1>
            <h2 className="text-md text-neutral-fg3 max-w-2xl text-center text-pretty md:text-lg">
              Streamline operations, automate workflows, and grow your business with our integrated suite of tools.
            </h2>
          </div>
        </div>
        <div className="flex items-start justify-center px-8 sm:px-24">
          <div className="flex w-full max-w-[80vw] flex-col items-center justify-start md:max-w-[392px]!">
            <ButtonLink
              className={clsx(
                "h-14! flex-col items-center justify-center rounded-none text-base!",
                "flex w-full",
              )}
              href="/sign-up"
              intent="primary"
            >
              Get Started
            </ButtonLink>
            <ButtonLink
              className={clsx(
                "h-14! flex-col items-center justify-center rounded-none text-base!",
                "max-w-sm:border-x-0! border-neutral-stroke1 flex w-full border-x! border-y-0! bg-transparent! backdrop-blur-xl transition-colors duration-150 hover:bg-black/5!",
              )}
              href="/demo"
              intent="secondary"
            >
              Book a Demo
            </ButtonLink>
          </div>
        </div>
      </div>
    </section>
  );
}
