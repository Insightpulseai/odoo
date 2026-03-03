import Image from "next/image";

import { ThemeSwitcher } from "../theme-switcher";
import { ButtonLink } from "@/common/button";
import Link from "next/link";

function isExternalLink(url: string | null | undefined) {
  return url && /^https?:\/\//.test(url);
}

const footerData = {
  copyright: "2026 InsightPulse AI. All rights reserved.",
  navbar: {
    items: [
      { _title: "Features", url: "/features" },
      { _title: "Pricing", url: "/pricing" },
      { _title: "Docs", url: "/docs" },
      { _title: "Blog", url: "/blog" },
    ],
  },
  socialLinks: [] as Array<{ _title: string; icon?: { url: string }; url: string }>,
};

export async function Footer() {
  const footer = footerData;

  return (
    <footer className="border-t border-neutral-stroke1 py-16">
      <div className="container mx-auto grid grid-cols-2 grid-rows-[auto_auto_auto] place-items-start items-center gap-y-7 px-6 sm:grid-cols-[1fr_auto_1fr] sm:grid-rows-2 sm:gap-x-3 sm:gap-y-16">
        <Link aria-label="Homepage" href="/">
          <Image
            priority
            alt="Logo"
            className="h-8 w-auto"
            height={32}
            src="/logo.svg"
            width={120}
          />
        </Link>
        <nav className="col-start-1 row-start-2 flex flex-col gap-x-2 gap-y-3 self-center sm:col-span-1 sm:col-start-2 sm:row-start-1 sm:flex-row sm:items-center sm:place-self-center md:gap-x-4 lg:gap-x-8">
          {footer.navbar.items.map(({ _title, url }) => (
            <ButtonLink
              key={_title}
              unstyled
              className="px-2 font-light tracking-tight text-neutral-fg3 hover:text-neutral-fg1"
              href={url ?? "#"}
              target={isExternalLink(url) ? "_blank" : "_self"}
            >
              {_title}
            </ButtonLink>
          ))}
        </nav>
        <div className="col-start-2 row-start-1 flex items-center gap-3 self-center justify-self-end sm:col-span-1 sm:col-start-3 sm:row-start-1">
          <p className="hidden text-neutral-fg3 sm:block">
            Appearance
          </p>
          <ThemeSwitcher />
        </div>

        <p className="col-span-2 text-pretty text-sm text-neutral-fg3 sm:col-span-1 ">
          {footer.copyright}
        </p>

        <ul className="col-span-2 col-start-1 row-start-3 flex w-full items-center gap-x-3.5 gap-y-4 sm:col-span-1 sm:col-start-3 sm:row-start-2 sm:w-auto sm:flex-wrap sm:justify-self-end">
          {footer.socialLinks.map((link) => {
            return (
              <li key={link._title} className="shrink-0 sm:first:ml-auto">
                <ButtonLink
                  unstyled
                  className="block aspect-square p-0.5 hover:brightness-75"
                  href={link.url}
                  target="_blank"
                >
                  <Image
                    alt={link._title}
                    height={24}
                    src={link.icon?.url ?? ""}
                    width={24}
                  />
                </ButtonLink>
              </li>
            );
          })}
        </ul>
      </div>
    </footer>
  );
}
