import * as React from "react";
import { cn } from "@/lib/utils";

interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackSrc?: string;
}

export function Avatar({
  src,
  alt = "Avatar",
  className,
  fallbackSrc = "/assets/avatar-placeholder.svg",
  ...props
}: AvatarProps) {
  const [imgSrc, setImgSrc] = React.useState(src || fallbackSrc);

  React.useEffect(() => {
    setImgSrc(src || fallbackSrc);
  }, [src, fallbackSrc]);

  return (
    <img
      src={imgSrc}
      alt={alt}
      className={cn("rounded-full", className)}
      onError={() => setImgSrc(fallbackSrc)}
      loading="lazy"
      {...props}
    />
  );
}
