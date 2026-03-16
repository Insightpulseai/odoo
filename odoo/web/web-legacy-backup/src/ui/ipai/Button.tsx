import { tokens } from "@ipai/design-tokens";
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center font-extrabold transition-all shadow-sm",
  {
    variants: {
      variant: {
        primary: "",  // Styles applied via inline style
        secondary: "",
        ghost: "",
      },
      size: {
        sm: "h-10 px-6 text-sm rounded-full",
        md: "h-14 px-8 text-base rounded-full",
        lg: "h-16 px-10 text-lg rounded-full",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({
  variant = "primary",
  size,
  className,
  children,
  ...props
}: ButtonProps) {
  // Token-driven inline styles
  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: tokens.color.accent.green,
      color: tokens.color.text.onAccent,
    },
    secondary: {
      border: `2px solid ${tokens.color.accent.teal}`,
      color: tokens.color.accent.teal,
    },
    ghost: {
      color: tokens.color.primary,
    },
  };

  const currentVariant = variant || "primary";

  return (
    <button
      className={buttonVariants({ variant, size, className })}
      style={variantStyles[currentVariant]}
      {...props}
    >
      {children}
    </button>
  );
}
