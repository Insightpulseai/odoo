// Generated from Figma frame: "Card/Product"
// Figma URL: https://www.figma.com/design/ABC123/MyDesign?node-id=1234
// Generated: 2025-01-21T00:00:00Z

import { cn } from '@/lib/utils';

interface ProductCardProps {
  title: string;
  description: string;
  price: number;
  imageUrl: string;
  className?: string;
}

export function ProductCard({
  title,
  description,
  price,
  imageUrl,
  className
}: ProductCardProps) {
  return (
    <article
      className={cn(
        // Layout (from Auto Layout)
        "flex flex-col gap-4",
        // Sizing
        "w-full max-w-sm",
        // Spacing (from Figma padding)
        "p-6",
        // Visual (from Figma fills/effects)
        "bg-card text-card-foreground rounded-lg shadow-md",
        // Interactive
        "hover:shadow-lg transition-shadow",
        className
      )}
    >
      <img
        src={imageUrl}
        alt={title}
        className="w-full h-48 object-cover rounded-md"
      />
      <div className="flex flex-col gap-2">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
        <span className="text-xl font-bold text-primary">{price.toLocaleString()}</span>
      </div>
    </article>
  );
}
