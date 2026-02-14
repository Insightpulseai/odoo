import { tokens } from "@ipai/design-tokens";
import { cva, type VariantProps } from "class-variance-authority";

const chipVariants = cva("inline-flex items-center gap-2 px-3 py-1 text-sm font-medium rounded-full", {
  variants: {
    variant: {
      default: "",
      accent: "",
      success: "",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

export interface ChipProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof chipVariants> {}

export function Chip({ variant, className, children, ...props }: ChipProps) {
  const variantStyles: Record<string, React.CSSProperties> = {
    default: {
      backgroundColor: tokens.color.canvas,
      color: tokens.color.text.primary,
    },
    accent: {
      backgroundColor: `rgba(100, 185, 202, 0.1)`,  // Teal with alpha
      color: tokens.color.accent.teal,
    },
    success: {
      backgroundColor: `rgba(123, 192, 67, 0.1)`,  // Green with alpha
      color: tokens.color.accent.green,
    },
  };

  const currentVariant = variant || "default";

  return (
    <div
      className={chipVariants({ variant, className })}
      style={variantStyles[currentVariant]}
      {...props}
    >
      {children}
    </div>
  );
}
