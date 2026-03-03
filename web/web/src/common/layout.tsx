import { cva, type VariantProps } from "class-variance-authority";

export const $section = cva("py-16 md:py-24 flex flex-col items-center gap-12 relative", {
  variants: {
    container: {
      default: "container mx-auto px-6",
      full: "",
    },
  },
  defaultVariants: {
    container: "default",
  },
});

type SectionProps = React.AllHTMLAttributes<HTMLDivElement> & VariantProps<typeof $section>;

export function Section({ className, container, ...props }: SectionProps) {
  return <section className={$section({ className, container })} {...props} />;
}
