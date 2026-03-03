import * as React from "react";
import { clsx } from "clsx";

export function LabeledInput({
  label,
  id: _id,
  className,
  ...props
}: { label: string; id?: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  const reactId = React.useId();
  const id = _id ?? reactId;

  return (
    <LabeledWrapper id={id} label={label}>
      <input
        className={clsx(
          className,
          "rounded-md border border-neutral-stroke1 bg-neutral-bg2 py-2 pl-3 pr-3.5 text-sm placeholder:text-sm placeholder:text-neutral-fg3/50",
        )}
        id={id}
        {...props}
      />
    </LabeledWrapper>
  );
}

export const LabeledTextarea = ({
  label,
  id: _id,
  ref,
  className,
  ...props
}: { label: string } & React.JSX.IntrinsicElements["textarea"]) => {
  const reactId = React.useId();
  const id = _id ?? reactId;

  return (
    <LabeledWrapper id={id} label={label}>
      <textarea
        ref={ref}
        className={clsx(
          className,
          "rounded-md border border-neutral-stroke1 bg-neutral-bg2 py-2 pl-3 pr-3.5 text-sm [form-sizing:content] placeholder:text-sm placeholder:text-neutral-fg3",
        )}
        id={id}
        {...props}
      />
    </LabeledWrapper>
  );
};

export const LabeledWrapper = ({
  label,
  children,
  id,
  ref,
}: {
  id?: string;
  label: string;
  children: React.ReactNode;
} & React.JSX.IntrinsicElements["div"]) => {
  return (
    <div ref={ref} className="relative flex flex-col">
      <label
        className="pb-1.5 text-xs font-medium text-neutral-fg1"
        htmlFor={id}
      >
        {label}
      </label>
      {children}
    </div>
  );
};
