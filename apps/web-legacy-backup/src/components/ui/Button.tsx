import Link from 'next/link';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  href?: string;
  onClick?: () => void;
  className?: string;
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  href,
  onClick,
  className = ''
}: ButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center font-extrabold rounded-full transition-all duration-200';

  const variantClasses = {
    primary: 'bg-[var(--ipai-accent-green)] text-white hover:bg-[#6AA839] active:bg-[#5A9032] shadow-md',
    secondary: 'border-2 border-[var(--ipai-primary)] text-[var(--ipai-primary)] hover:bg-[var(--ipai-primary)] hover:text-white',
    ghost: 'text-[var(--ipai-primary)] hover:bg-[var(--ipai-primary)]/5',
  };

  const sizeClasses = {
    sm: 'h-10 px-6 text-sm',
    md: 'h-14 px-8 text-base',
    lg: 'h-16 px-10 text-lg',
  };

  const combinedClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  if (href) {
    return (
      <Link href={href} className={combinedClasses}>
        {children}
      </Link>
    );
  }

  return (
    <button onClick={onClick} className={combinedClasses}>
      {children}
    </button>
  );
}
