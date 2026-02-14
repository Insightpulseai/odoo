'use client'

import Link from 'next/link'

interface Segment {
  icon: string
  title: string
  subtitle: string
  description: string
}

const segments: Segment[] = [
  {
    icon: '💼',
    title: 'For Freelancers',
    subtitle: 'Simplify & Succeed',
    description: 'Maximize deductions with expert guidance tailored for freelancers. From quarterly estimates to year-end filing, we help you stay compliant and keep more of what you earn.',
  },
  {
    icon: '👨‍👩‍👧‍👦',
    title: 'For Families',
    subtitle: 'Stability & Security',
    description: 'Navigate life changes with confidence—tax breaks for education, homeownership, childcare, and more. We make tax time less stressful so you can focus on what matters most.',
  },
  {
    icon: '🏢',
    title: 'For Small Businesses',
    subtitle: 'Growth & Guidance',
    description: 'Affordable accounting support that scales with you. From startup bookkeeping to strategic tax planning, get the clarity you need to make informed decisions and drive growth.',
  },
]

export function TargetSegments() {
  return (
    <section className="py-16 md:py-20 lg:py-24 bg-gray-50">
      <div className="container mx-auto px-6 md:px-8 lg:px-16">
        <div className="text-center mb-12 md:mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-forest-900 mb-4">
            Smart Finance for everyone
          </h2>
          <p className="text-lg md:text-xl text-forest-700 max-w-2xl mx-auto">
            In Noble Finance, we believe that financial services are accessible
            to everyone. Whether you're an individual or a business owner, we're
            here to simplify accounting & servicing to make it easier.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 lg:gap-10 mb-12">
          {segments.map((segment, index) => (
            <div
              key={index}
              className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="space-y-4">
                <div className="text-4xl">{segment.icon}</div>
                <div>
                  <h3 className="text-xl font-bold text-forest-900 mb-1">
                    {segment.title}
                  </h3>
                  <p className="text-sm text-forest-600 font-medium mb-3">
                    {segment.subtitle}
                  </p>
                  <p className="text-forest-700 leading-relaxed">
                    {segment.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Custom Plan CTA */}
        <div className="bg-gradient-to-br from-forest-700 to-forest-600 rounded-2xl p-8 md:p-12 lg:p-16 text-white shadow-xl">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="space-y-6">
              <h3 className="text-2xl md:text-3xl lg:text-4xl font-bold">
                A custom built plan for you.
              </h3>
              <p className="text-lg leading-relaxed text-forest-100">
                At Noble Finances, we offer tailor-fit pricing based on your
                specific needs. Whether you're a freelancer or a growing business,
                we'll work with you to create a plan that fits perfectly.
              </p>
              <Link
                href="#contact"
                className="inline-flex items-center justify-center px-6 py-3 bg-white text-forest-700 font-medium rounded-full hover:bg-mint-50 transition-colors"
              >
                Build my plan
              </Link>
            </div>
            <div className="flex justify-center md:justify-end">
              {/* Stair-step illustration */}
              <div className="relative w-48 h-48">
                <div className="absolute bottom-0 left-0 space-y-2">
                  {[40, 60, 80, 100, 120, 140].map((width, i) => (
                    <div
                      key={i}
                      className="bg-gradient-to-r from-amber-400 to-orange-400 rounded"
                      style={{ width: `${width}px`, height: '20px' }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
