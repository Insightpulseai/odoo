"use client";

import { Button, ButtonLink } from "@/common/button";

interface TrackProps {
  analyticsKey?: string;
  name?: string;
}

type TrackedButtonProps = React.ComponentProps<typeof Button> & TrackProps;

export const TrackedButton = ({
  analyticsKey,
  children,
  onClick,
  name,
  ref,
  ...props
}: TrackedButtonProps) => {
  return (
    <Button
      {...props}
      ref={ref}
      onClick={(e) => {
        // Analytics tracking - implement with your analytics provider
        if (onClick) {
          onClick(e);
        }
      }}
    >
      {children}
    </Button>
  );
};

type TrackedButtonLinkProps = React.ComponentProps<typeof ButtonLink> & TrackProps;

export const TrackedButtonLink = ({
  analyticsKey,
  children,
  onClick,
  name,
  ref,
  ...props
}: TrackedButtonLinkProps) => {
  return (
    <ButtonLink
      {...props}
      ref={ref}
      onClick={(e) => {
        // Analytics tracking - implement with your analytics provider
        if (onClick) {
          onClick(e);
        }
      }}
    >
      {children}
    </ButtonLink>
  );
};
