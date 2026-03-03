import Image from "next/image";
import clsx from "clsx";

import { Section } from "@/common/layout";

import s from "./companies.module.scss";

const companies = [
  { title: "Company 1", image: "/images/companies/company-1.svg" },
  { title: "Company 2", image: "/images/companies/company-2.svg" },
  { title: "Company 3", image: "/images/companies/company-3.svg" },
  { title: "Company 4", image: "/images/companies/company-4.svg" },
  { title: "Company 5", image: "/images/companies/company-5.svg" },
];

export function Companies() {
  return (
    <Section container="full">
      <h2 className="text-center tracking-tight text-neutral-fg3 opacity-50">
        Trusted by leading companies
      </h2>
      <div className="no-scrollbar flex max-w-full justify-center overflow-auto">
        <div className="pointer-events-none absolute left-0 top-0 h-full w-[30vw] bg-transparent bg-linear-to-r from-neutral-bg1 xl:hidden" />
        <div className="pointer-events-none absolute right-0 top-0 h-full w-[30vw] bg-transparent bg-linear-to-l from-neutral-bg1 xl:hidden" />
        <div
          className={clsx("flex shrink-0 items-center gap-4 px-6 lg:gap-6 lg:px-12", s.scrollbar)}
        >
          {companies.map((company) => (
            <figure
              key={company.title}
              className="flex h-16 items-center px-2 py-3 lg:p-4"
            >
              <Image
                alt={company.title}
                className="w-24 lg:w-32"
                height={20}
                src={company.image}
                width={32}
              />
            </figure>
          ))}
        </div>
      </div>
    </Section>
  );
}
