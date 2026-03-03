import Image from "next/image";
import Link, { type LinkProps } from "next/link";

export async function FormLayout({
  children,
  title,
  subtitle,
}: {
  title: string;
  subtitle: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-5 rounded-xl border border-neutral-bg2 bg-neutral-bg1 p-5 shadow-md">
      <header className="flex flex-col gap-3">
        <Image
          priority
          alt="Logo"
          className="size-8 self-start"
          height={32}
          src="/logo-icon.svg"
          width={32}
        />
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-medium">{title}</h1>
          <div className="text-sm text-neutral-fg2">
            {subtitle}
          </div>
        </div>
      </header>
      {children}
    </div>
  );
}

export function RichTextFormWrapper({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

function CustomAnchor({
  children,
  ...props
}: React.AllHTMLAttributes<HTMLAnchorElement> & LinkProps) {
  return (
    <Link className="text-brand-foreground hover:underline" {...props}>
      {children}
    </Link>
  );
}
