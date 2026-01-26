import Link from 'next/link'
import { ArrowRight, BarChart3, Bot, Shield, Zap, RefreshCw, Globe } from 'lucide-react'

const features = [
  {
    icon: Bot,
    title: 'AI-Powered Automation',
    description: 'Automate repetitive tasks with intelligent workflows that learn and adapt to your business processes.',
  },
  {
    icon: BarChart3,
    title: 'Real-Time Analytics',
    description: 'Get instant insights with customizable dashboards and reports that help you make data-driven decisions.',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Bank-grade security with SSO, audit logs, and compliance certifications to protect your data.',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Built for speed with sub-second response times and 99.99% uptime guarantee.',
  },
  {
    icon: RefreshCw,
    title: 'Seamless Integrations',
    description: 'Connect with your existing tools including Slack, Teams, Salesforce, and 100+ more.',
  },
  {
    icon: Globe,
    title: 'Global Scale',
    description: 'Deploy anywhere with multi-region support, CDN, and automatic scaling.',
  },
]

const integrations = [
  'Slack', 'Microsoft Teams', 'Salesforce', 'HubSpot', 'Zendesk', 'Jira', 'GitHub', 'Stripe'
]

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-accent-50 py-20 sm:py-32">
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight">
              Transform Your Business with{' '}
              <span className="bg-gradient-to-r from-primary-600 to-accent-500 bg-clip-text text-transparent">
                Intelligent Automation
              </span>
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
              InsightPulse AI combines powerful automation, advanced analytics, and AI-driven insights
              to help you work smarter, not harder.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/auth/signup" className="btn btn-primary text-lg px-8 py-4">
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link href="/pricing" className="btn btn-secondary text-lg px-8 py-4">
                View Pricing
              </Link>
            </div>
            <p className="mt-4 text-sm text-gray-500">
              No credit card required. 14-day free trial.
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Everything you need to scale your operations
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              A complete platform that grows with your business, from startup to enterprise.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="card p-6 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Works with your favorite tools
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Connect to 100+ integrations out of the box
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            {integrations.map((integration) => (
              <div
                key={integration}
                className="bg-white px-6 py-3 rounded-lg shadow-sm border border-gray-100 text-gray-700 font-medium"
              >
                {integration}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Trusted by growing companies
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Join thousands of businesses that rely on InsightPulse AI
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-4xl font-bold text-primary-600">10K+</div>
                <div className="text-gray-500 mt-1">Active Users</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-primary-600">99.99%</div>
                <div className="text-gray-500 mt-1">Uptime</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-primary-600">500K+</div>
                <div className="text-gray-500 mt-1">Tasks Automated</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-primary-600">50+</div>
                <div className="text-gray-500 mt-1">Countries</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to transform your business?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Start your free trial today. No credit card required.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signup" className="btn bg-white text-primary-600 hover:bg-primary-50 text-lg px-8 py-4">
              Get Started Free
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <a
              href="mailto:business@insightpulseai.com"
              className="text-white hover:text-primary-100 font-medium"
            >
              Contact Sales
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
