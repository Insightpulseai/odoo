import clsx from "clsx";
import Image, { type ImageProps } from "next/image";

type DarkLightImageProps = {
  dark?: {
    url: string;
    alt?: string | null;
    width?: number;
    height?: number;
    blurDataURL?: string;
    aspectRatio?: string;
  } | null;
  light: {
    url: string;
    alt?: string | null;
    width?: number;
    height?: number;
    blurDataURL?: string;
    aspectRatio: string;
  };
} & Omit<ImageProps, "src" | "alt"> & {
    alt?: string;
    withPlaceholder?: boolean;
  };

export function DarkLightImage({
  alt,
  dark,
  light,
  className,
  width,
  height,
  withPlaceholder,
  ...props
}: DarkLightImageProps) {
  return (
    <Image
      alt={light.alt ?? alt ?? ""}
      className={className}
      height={height ?? light.height}
      src={light.url}
      width={width ?? light.width}
      {...props}
      {...(withPlaceholder && light.blurDataURL
        ? {
            placeholder: "blur",
            blurDataURL: light.blurDataURL,
          }
        : {})}
    />
  );
}

export function DarkLightImageAutoscale(props: DarkLightImageProps) {
  const [aspectRatioWidth, aspectRatioHeight] = props.light.aspectRatio.split("/").map(Number);
  const aspectRatio = (aspectRatioWidth ?? 0) / (aspectRatioHeight ?? 0);
  let logoStyle;

  switch (true) {
    case aspectRatio <= 1.2:
      logoStyle = "square";
      break;
    case aspectRatio < 1.4:
      logoStyle = "4/3";
      break;
    case aspectRatio < 4:
      logoStyle = "portrait";
      break;
    default:
      logoStyle = "landscape";
      break;
  }

  return (
    <DarkLightImage
      priority
      alt="logo"
      className={clsx("w-auto max-w-[200px] object-contain", {
        "h-10": logoStyle === "square",
        "h-9": logoStyle === "4/3",
        "h-8": logoStyle === "portrait",
        "h-6": logoStyle === "landscape",
      })}
      style={{
        aspectRatio: props.light.aspectRatio,
      }}
      {...props}
    />
  );
}
