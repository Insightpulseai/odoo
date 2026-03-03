"use client";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import clsx from "clsx";

import * as React from "react";

export function Select({
  children,
  className,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
  const [value, setValue] = React.useState("");

  return (
    <div className="relative flex flex-col">
      <select
        className={clsx(
          "appearance-none rounded-md border border-neutral-stroke1 bg-neutral-bg2 py-2 pl-3 pr-3.5 text-sm placeholder:text-sm placeholder:text-neutral-fg3/50",
          value === "" && "text-neutral-fg3/50",
          className,
        )}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        {...props}
      >
        <option disabled value="">
          Select an option
        </option>
        {children}
      </select>
      <ChevronDownIcon className="absolute right-2 top-1/2 size-4 -translate-y-1/2 text-neutral-fg3" />
    </div>
  );
}
