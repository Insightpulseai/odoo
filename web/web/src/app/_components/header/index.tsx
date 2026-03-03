import { ButtonLink } from "@/common/button";
import Image from "next/image";

import { DesktopMenu, MobileMenu } from "./navigation-menu";

// Static header data - replace with site-data import as needed
const headerData = {
  navbar: {
    items: [
      { _id: "1", _title: "Features", href: "/features", sublinks: { items: [] } },
      { _id: "2", _title: "Pricing", href: "/pricing", sublinks: { items: [] } },
      { _id: "3", _title: "Docs", href: "/docs", sublinks: { items: [] } },
    ],
  },
  rightCtas: {
    items: [
      { _id: "login", href: "/login", label: "Log in", type: "secondary" as const },
      { _id: "signup", href: "/sign-up", label: "Sign up", type: "primary" as const },
    ],
  },
};

export type HeaderLiksFragment = {
  _id: string;
  _title: string;
  href?: string | null;
  sublinks: {
    items: Array<{
      _id: string;
      _title: string;
      link: {
        __typename: string;
        text?: string;
        page?: { pathname: string; _title: string };
      };
    }>;
  };
};

export type HeaderFragment = {
  navbar: { items: HeaderLiksFragment[] };
  rightCtas: {
    items: Array<{
      _id: string;
      href: string;
      label: string;
      type: "primary" | "secondary";
    }>;
  };
};

export async function Header() {
  const header = headerData as unknown as HeaderFragment;

  return (
    <header className="sticky left-0 top-0 z-100 flex w-full flex-col border-b border-neutral-stroke1 bg-neutral-bg1">
      <div className="flex h-(--header-height) bg-neutral-bg1">
        <div className="container mx-auto grid w-full grid-cols-header place-items-center content-center items-center px-6 *:first:justify-self-start">
          <ButtonLink unstyled className="flex items-center ring-offset-2" href="/">
            <Image
              priority
              alt="Logo"
              className="h-8 w-auto"
              height={32}
              src="/logo.svg"
              width={120}
            />
          </ButtonLink>
          <DesktopMenu {...header} />
          <MobileMenu {...header} />
        </div>
      </div>
    </header>
  );
}
