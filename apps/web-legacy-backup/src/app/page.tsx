import type { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { FeatureCard } from '@/components/ui/FeatureCard';
import { BenefitBadge } from '@/components/ui/BenefitBadge';

export const metadata: Metadata = {
  title: 'InsightPulse AI — Open ERP Platform for Modern Teams',
  description:
    'End-to-end business operations platform built on Odoo CE 19, OCA modules, and open standards. ERP, automation, analytics, and integrations — self-hosted or cloud.',
  openGraph: {
    title: 'InsightPulse AI — Open ERP Platform',
    description:
      'End-to-end operations: ERP, automation, analytics. Built on Odoo CE 19 + OCA. No vendor lock-in.',
    type: 'website',
  },
  robots: { index: true, follow: true },
};

const PLATFORM_FEATURES = [
  {
    icon: '📊',
    title: 'ERP Core',
    description:
      'Complete business management: accounting, inventory, sales, purchasing, CRM, and HR — all integrated.',
  },
  {
    icon: '⚡',
    title: 'Automation',
    description:
      'Workflow automation with n8n integration. Connect your tools, automate repetitive tasks, scale operations.',
  },
  {
    icon: '📈',
    title: 'Analytics & BI',
    description:
      'Apache Superset and Tableau integration. Real-time dashboards, custom reports, data-driven decisions.',
  },
  {
    icon: '🔐',
    title: 'Governance & Compliance',
    description:
      'Audit trails, role-based access, compliance tools. Built for regulated industries and security-first teams.',
  },
  {
    icon: '🔌',
    title: 'Integrations',
    description:
      'Connect with Slack, GitHub, Supabase, Zoho Mail, and 100+ services. Open APIs, webhooks, custom connectors.',
  },
  {
    icon: '🌐',
    title: 'Self-Hosted or Cloud',
    description:
      'Deploy on your infrastructure or use our managed service. Full data ownership, no vendor lock-in.',
  },
];

const TECH_STACK = [
  'Odoo CE 19',
  'OCA Modules',
  'PostgreSQL 16',
  'n8n',
  'Apache Superset',
  'Next.js',
  'Tailwind CSS',
  'TypeScript',
];

const BENEFITS = [
  {
    label: 'Open Source',
    description: 'Built on Odoo CE and OCA community modules',
  },
  {
    label: 'No Lock-In',
    description: 'Export your data anytime, deploy anywhere',
  },
  {
    label: 'Cost-Optimized',
    description: 'Up to 80% cost savings vs proprietary ERP',
  },
  {
    label: 'Fully Auditable',
    description: 'Complete audit trails for compliance',
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-[#0a0a0a] to-[#1a1a1a]">
      {/* Navigation */}
      <nav className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5 font-extrabold tracking-tight text-lg text-white">
            <span className="pulser-dot" aria-hidden="true" />
            <span>InsightPulseAI</span>
          </div>
          <div className="flex gap-4">
            <Link
              href="https://github.com/InsightPulseAI/odoo"
              className="text-sm font-semibold text-white/70 hover:text-white transition-colors"
            >
              GitHub
            </Link>
            <a
              href="mailto:hello@insightpulseai.com"
              className="text-sm font-semibold text-white/70 hover:text-white transition-colors"
            >
              Contact
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-block px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm font-bold text-white/80 mb-8">
          Open Source ERP Platform
        </div>

        <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-6 leading-tight">
          Run Your Business
          <br />
          <span className="bg-gradient-to-r from-[var(--ipai-primary)] to-[var(--ipai-accent-teal)] bg-clip-text text-transparent">
            End-to-End
          </span>
        </h1>

        <p className="text-xl text-white/70 max-w-3xl mx-auto mb-10 leading-relaxed">
          Complete business operations platform built on Odoo CE 19, OCA modules, and open standards.
          Self-hosted or cloud. No vendor lock-in. Fully auditable.
        </p>

        <div className="flex flex-wrap gap-4 justify-center">
          <Button variant="primary" size="md" href="mailto:hello@insightpulseai.com">
            Get Started
          </Button>
          <Button variant="secondary" size="md" href="https://github.com/InsightPulseAI/odoo">
            View on GitHub
          </Button>
        </div>
      </section>

      {/* Benefits Bar */}
      <section className="border-y border-white/10 bg-white/[0.02] backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {BENEFITS.map((benefit) => (
              <div key={benefit.label} className="text-center">
                <BenefitBadge
                  icon={<svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>}
                  text={benefit.label}
                />
                <div className="text-xs text-white/60 mt-1">
                  {benefit.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Features */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-extrabold text-white mb-4">
            Everything You Need
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Integrated platform that grows with your business
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {PLATFORM_FEATURES.map((feature) => (
            <FeatureCard
              key={feature.title}
              icon={<span className="text-2xl">{feature.icon}</span>}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-7xl mx-auto px-6 py-24 border-t border-white/10">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-extrabold text-white mb-4">
            Built with Modern Tech
          </h2>
          <p className="text-lg text-white/70">
            Open source foundations, production-ready stack
          </p>
        </div>

        <div className="flex flex-wrap gap-3 justify-center max-w-4xl mx-auto">
          {TECH_STACK.map((tech) => (
            <div
              key={tech}
              className="px-5 py-3 rounded-full bg-white/[0.04] border border-white/10 text-sm font-bold text-white/90 hover:bg-white/[0.08] transition-colors"
            >
              {tech}
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 py-24 border-t border-white/10">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-4xl font-extrabold text-white mb-6">
            Ready to Transform Your Operations?
          </h2>
          <p className="text-xl text-white/70 mb-10">
            Join teams building on open foundations. Self-hosted or managed cloud deployment.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Button variant="primary" size="md" href="mailto:hello@insightpulseai.com">
              Get in Touch
            </Button>
            <Button variant="secondary" size="md" href="https://github.com/InsightPulseAI/odoo/blob/main/README.md">
              Read Documentation
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div className="text-sm text-white/60">
              © 2026 InsightPulseAI. Built on Odoo CE 19 + OCA.
            </div>
            <div className="flex gap-6">
              <a
                href="https://github.com/InsightPulseAI/odoo"
                className="text-sm text-white/60 hover:text-white transition-colors"
              >
                GitHub
              </a>
              <a
                href="mailto:hello@insightpulseai.com"
                className="text-sm text-white/60 hover:text-white transition-colors"
              >
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
