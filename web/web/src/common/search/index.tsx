"use client";
import * as React from "react";
import { MagnifyingGlassIcon } from "@radix-ui/react-icons";
import NextLink from "next/link";
import clsx from "clsx";
import * as Popover from "@radix-ui/react-popover";

import { Avatar } from "../avatar";
import { AvatarsGroup } from "../avatars-group";

// Simplified search component - basehub search removed
export function SearchContent() {
  const [query, setQuery] = React.useState("");
  const [open, setOpen] = React.useState(false);
  const searchInputRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    if (query) setOpen(true);
    else setOpen(false);
  }, [query]);

  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "k" && event.metaKey) {
        event.preventDefault();
        searchInputRef.current?.blur();
        searchInputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Anchor asChild>
        {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
        <label
          className={clsx(
            "ml-auto flex w-full cursor-text items-center gap-x-1 rounded-full border border-neutral-stroke1 px-3.5 py-2.5 ring-brand-foreground! focus-within:ring-3 md:max-w-[280px]",
          )}
        >
          <MagnifyingGlassIcon
            className="pointer-events-none size-5 shrink-0 text-neutral-fg2 transition-colors duration-75"
            color="currentColor"
          />
          <input
            ref={searchInputRef}
            className="grow bg-transparent outline-hidden! placeholder:text-neutral-fg3 focus-visible:outline-hidden"
            placeholder="Search"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              if (query) setOpen(true);
            }}
          />
        </label>
      </Popover.Anchor>

      <Popover.Portal>
        <Popover.Content
          asChild
          align="end"
          className="z-modal"
          sideOffset={8}
          onOpenAutoFocus={(e) => {
            e.preventDefault();
          }}
        >
          <div className="relative mx-5 min-h-20 w-[calc(100vw_-_2.5rem)] scroll-py-2 overflow-y-auto overscroll-y-contain rounded-xl border border-neutral-bg3 bg-neutral-bg1 p-2 shadow-md md:mx-0 md:max-h-[320px] md:w-[550px]">
            <div className="absolute left-1/2 top-1/2 w-fit max-w-full -translate-x-1/2 -translate-y-1/2 items-center overflow-hidden text-ellipsis whitespace-nowrap px-2 py-1 text-neutral-fg3">
              {query ? (
                <>No results for <span className="font-medium">&ldquo;{query}&rdquo;</span></>
              ) : (
                "Start typing to search..."
              )}
            </div>
          </div>
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
