import { ReactNode } from 'react';

interface BenefitBadgeProps {
  icon: ReactNode;
  text: string;
  className?: string;
}

export function BenefitBadge({ icon, text, className = '' }: BenefitBadgeProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center" style={{ background: 'var(--ipai-accent-green)' }}>
        {icon}
      </div>
      <span className="text-[var(--ipai-text)] font-medium">{text}</span>
    </div>
  );
}
