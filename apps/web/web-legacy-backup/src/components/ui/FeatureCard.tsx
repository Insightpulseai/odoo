import { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  className?: string;
}

export function FeatureCard({ icon, title, description, className = '' }: FeatureCardProps) {
  return (
    <div className={`card p-8 ${className}`}>
      <div className="text-[var(--ipai-accent-green)] mb-4 flex items-center justify-center w-12 h-12 rounded-xl" style={{ background: 'rgba(123, 192, 67, 0.1)' }}>
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3 text-[var(--ipai-text)]">{title}</h3>
      <p className="text-[var(--ipai-text-muted)]">{description}</p>
    </div>
  );
}
