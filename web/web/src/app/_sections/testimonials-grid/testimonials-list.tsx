"use client";

import * as React from "react";

import { Button } from "@/common/button";
import type { QuoteFragment } from ".";
import { cx } from "class-variance-authority";
import Image from "next/image";

const ITEMS_PER_COLUMN = 3;

export function TestimonialsGridClient({ quotes }: { quotes: QuoteFragment[] }) {
  const [showMore, setShowMore] = React.useState(false);

  const filteredItems = React.useMemo(() => {
    if (showMore) return quotes;
    // split in three
    const chunkSize = Math.ceil(quotes.length / 3);
    const itemsToDisplay: QuoteFragment[] = [];

    for (let i = 0; i < 3; i++) {
      // Push the first 3 items for each column
      itemsToDisplay.push(
        ...quotes.slice(i * chunkSize, (i + 1) * chunkSize).slice(0, ITEMS_PER_COLUMN),
      );
    }

    return itemsToDisplay;
  }, [quotes, showMore]);

  return (
    <>
      <div className="relative overflow-hidden md:columns-3">
        {filteredItems.map(({ quote, author, _id }, i) => (
          <article
            key={_id}
            className={cx(
              "mb-8 break-inside-avoid overflow-hidden rounded-xl border border-neutral-stroke1 last:mb-0",
              { "hidden md:block": i > 2 && !showMore },
            )}
          >
            <div className="flex items-start border-b border-neutral-stroke1 p-5">
              <blockquote className="text-pretty text-base font-light text-neutral-fg2 md:text-lg">
                {quote}
              </blockquote>
            </div>
            <div className="flex items-center bg-neutral-bg2 px-4 py-3">
              <div className="flex flex-1 flex-col gap-0.5">
                <h5 className="text-xs font-medium text-neutral-fg3 md:text-sm">
                  {author._title}
                </h5>
                <p className="text-pretty text-xs text-neutral-fg3 md:text-sm">
                  {author.role}, {author.company._title}
                </p>
              </div>
              <div className="pl-4">
                <figure className="aspect-square size-8 rounded-full">
                  <Image
                    alt={author.image.alt ?? author._title}
                    className="size-8 rounded-full"
                    src={author.image.url}
                    width={32}
                    height={32}
                  />
                </figure>
              </div>
            </div>
          </article>
        ))}
      </div>

      {!showMore && (
        <div
          className={cx(
            "justify-center",
            quotes.length > filteredItems.length ? "flex" : quotes.length > 3 && "flex md:hidden",
          )}
        >
          <Button intent="secondary" onClick={() => setShowMore(!showMore)}>
            Show more
          </Button>
        </div>
      )}
    </>
  );
}
