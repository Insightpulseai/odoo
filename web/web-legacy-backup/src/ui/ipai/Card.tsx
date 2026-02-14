import { tokens } from "@ipai/design-tokens";
import { cva, type VariantProps } from "class-variance-authority";

const cardVariants = cva("rounded-xl transition-all", {
  variants: {
    variant: {
      default: "",
      glass: "",  // Replaces undefined "glass-card" class
      elevated: "",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export function Card({ variant, className, children, ...props }: CardProps) {
  const variantStyles: Record<string, React.CSSProperties> = {
    default: {
      backgroundColor: tokens.color.surface,
      border: `1px solid ${tokens.color.border}`,
      boxShadow: tokens.shadow.default,
    },
    glass: {
      backgroundColor: "rgba(255, 255, 255, 0.7)",
      backdropFilter: "blur(12px)",
      border: `1px solid ${tokens.color.border}`,
    },
    elevated: {
      backgroundColor: tokens.color.surface,
      boxShadow: tokens.shadow.lg,
    },
  };

  const currentVariant = variant || "default";

  return (
    <div
      className={cardVariants({ variant, className })}
      style={variantStyles[currentVariant]}
      {...props}
    >
      {children}
    </div>
  );
}
