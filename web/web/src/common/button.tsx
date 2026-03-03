import { type VariantProps, cva } from "class-variance-authority";
import Link, { type LinkProps } from "next/link";

export const $button = cva(
  "gap-1 font-normal shrink-0 rounded-[var(--borderRadiusMedium)] ring-neutral-stroke-accessible focus-visible:ring-2 outline-hidden outline-0",
  {
    variants: {
      intent: {
        primary: "bg-brand hover:bg-brand-hover text-neutral-fg-on-brand border-brand-hover",
        secondary:
          "bg-neutral-bg2 text-neutral-fg1 border-neutral-stroke1 border hover:bg-neutral-bg3",
        tertiary:
          "bg-neutral-fg1 text-neutral-bg1 border border-neutral-stroke1 hover:bg-neutral-bg3",
      },
      disabled: {
        true: "opacity-30",
      },
      onlyButton: {
        true: "rounded-xs",
      },
      iconSide: {
        left: "flex-row-reverse pl-3",
        right: "flex-row pr-3",
      },
      unstyled: {
        true: "px-0 py-0 bg-transparent border-none hover:bg-transparent hover:border-none",
      },
      size: {
        md: "inline-flex items-center justify-center px-3.5 text-sm h-8 md:px-5",
        lg: "inline-flex items-center justify-center h-9 px-5 text-sm md:text-base md:h-10",
      },
    },
  },
);

type ButtonProps<C extends keyof React.JSX.IntrinsicElements> = VariantProps<typeof $button> &
  React.JSX.IntrinsicElements[C] & {
    icon?: React.ReactNode;
    unstyled?: boolean;
  };

export const Button = ({
  children,
  intent = "primary",
  disabled = false,
  onlyButton = false,
  icon,
  iconSide = "left",
  unstyled,
  className,
  size = "md",
  ref,
  ...props
}: ButtonProps<"button">) => {
  return (
    <button
      ref={ref}
      className={$button(
        !unstyled
          ? {
              intent,
              disabled,
              onlyButton,
              iconSide: icon ? iconSide : undefined,
              unstyled,
              className,
              size,
            }
          : { className },
      )}
      disabled={disabled}
      {...props}
    >
      {children}
      {icon ? <span>{typeof icon === "string" ? icon : icon}</span> : null}
    </button>
  );
};

export const ButtonLink = ({
  children,
  intent = "primary",
  disabled = false,
  onlyButton = false,
  icon,
  iconSide = "left",
  unstyled,
  className,
  size = "md",
  ref,
  ...props
}: ButtonProps<"a"> & LinkProps) => {
  return (
    <Link
      ref={ref}
      className={$button(
        !unstyled
          ? {
              intent,
              disabled,
              onlyButton,
              iconSide: icon ? iconSide : undefined,
              className,
              unstyled,
              size,
            }
          : { className },
      )}
      {...props}
    >
      {children}
      {icon ? <span>{icon}</span> : null}
    </Link>
  );
};
