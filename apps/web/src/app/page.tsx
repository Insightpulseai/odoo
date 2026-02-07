import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Coming Soon',
  description:
    'We are shipping a rebuilt homepage. InsightPulseAI helps teams run operations end-to-end — faster, cleaner, and fully auditable.',
  openGraph: {
    title: 'InsightPulseAI — Coming Soon',
    description:
      'We are shipping a rebuilt homepage. Faster, cleaner, fully auditable operations.',
    type: 'website',
  },
  robots: { index: true, follow: true },
};

const CAPABILITIES = [
  'ERP Core',
  'Automation',
  'Analytics',
  'Governance',
  'Integrations',
];

export default function HomePage() {
  return (
    <main className="coming-soon-root min-h-screen flex items-center justify-center p-7">
      <div className="w-full max-w-[860px]">
        <div className="glass-card p-6">
          {/* Header */}
          <div className="flex items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-2.5 font-extrabold tracking-tight text-lg">
              <span className="pulser-dot" aria-hidden="true" />
              <span>InsightPulseAI</span>
            </div>
            <span className="text-[var(--ipai-text-muted)] font-bold text-xs tracking-[0.12em] uppercase">
              Pulsating Soon
            </span>
          </div>

          {/* Headline */}
          <h1 className="solution-heading text-balance mb-3">
            Coming soon — a cleaner, faster, fully auditable homepage.
          </h1>

          {/* Description */}
          <p className="text-[var(--ipai-text-muted)] text-[15px] leading-relaxed max-w-[62ch]">
            We are shipping an updated experience built on open foundations:
            ERP, automation, analytics, and integrations — designed to scale
            without vendor lock-in.
          </p>

          {/* Capability pills */}
          <div
            className="flex flex-wrap gap-2.5 mt-5"
            role="list"
            aria-label="Platform capabilities"
          >
            {CAPABILITIES.map((label) => (
              <div
                key={label}
                role="listitem"
                className="border border-[var(--ipai-border)] bg-white/[0.04] px-3 py-2.5 rounded-full text-xs font-bold text-white/80"
              >
                {label}
              </div>
            ))}
          </div>

          {/* CTA buttons */}
          <div className="flex flex-wrap gap-3 mt-5">
            <a
              href="mailto:hello@insightpulseai.com"
              className="coming-soon-btn-primary inline-flex items-center justify-center h-11 px-5 rounded-full font-extrabold no-underline"
            >
              Get in Touch
            </a>
            <a
              href="https://github.com/InsightPulseAI/odoo"
              className="inline-flex items-center justify-center h-11 px-5 rounded-full font-extrabold no-underline bg-white/[0.04] text-[var(--ipai-text)] border border-white/[0.14] hover:bg-white/[0.08] transition-colors"
            >
              View on GitHub
            </a>
          </div>

          {/* Footer */}
          <div className="mt-4 text-[var(--ipai-text-muted)] text-xs flex justify-between gap-3 flex-wrap">
            <span>&copy; 2026 InsightPulseAI</span>
            <span>Status: deploying UI refresh &bull; tokens preserved</span>
          </div>
        </div>
      </div>
    </main>
  );
}
