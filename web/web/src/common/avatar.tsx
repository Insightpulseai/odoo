"use client";
import clsx from "clsx";
import Image from "next/image";

import { CustomTooltip } from "./tooltip";
import type { ImageProps } from "next/image";

export interface AvatarFragment {
  url: string;
  alt: string | null;
}

export interface AuthorFragment {
  _id: string;
  _title: string;
  image: {
    url: string;
    alt: string | null;
    height: number;
    width: number;
  };
}

export function Author({
  image,
  _title,
  ...props
}: AuthorFragment & Omit<ImageProps, "src" | "alt">) {
  return (
    <CustomTooltip content={_title}>
      <Image
        alt={image.alt ?? `Avatar for ${_title}`}
        className="size-8 rounded-full border-2 border-neutral-bg1 object-cover transition-all"
        height={image.height}
        src={image.url}
        width={image.width}
        {...props}
      />
    </CustomTooltip>
  );
}

export function Avatar({
  className,
  alt,
  url,
  ...props
}: AvatarFragment & Omit<ImageProps, "src" | "alt">) {
  return (
    <Image
      priority
      alt={alt ?? "Avatar"}
      className={clsx(
        "size-7 shrink-0 rounded-full border-2 border-neutral-bg1 object-cover",
        className,
      )}
      height={28}
      src={url}
      width={28}
      {...props}
    />
  );
}
