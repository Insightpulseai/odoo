'use client'

import { ServiceCard } from './ServiceCard'

export function Services() {
  return (
    <section id="services" className="py-16 md:py-20 lg:py-24 bg-gray-50">
      <div className="container mx-auto px-6 md:px-8 lg:px-16">
        <div className="space-y-12 md:space-y-16">
          {/* Tax Preparation */}
          <ServiceCard
            title="Tax Preparation & Filing"
            description="Expert tax preparation services for individuals and businesses. We ensure accuracy and maximize your deductions while staying compliant with all regulations."
            icon={
              <div className="relative w-full h-full">
                {/* Tax form illustration */}
                <div className="bg-orange-200 rounded-2xl p-8 shadow-lg transform rotate-3 hover:rotate-0 transition-transform">
                  <div className="space-y-3">
                    <div className="h-3 bg-orange-400 rounded w-3/4" />
                    <div className="h-3 bg-orange-300 rounded w-full" />
                    <div className="h-3 bg-orange-300 rounded w-5/6" />
                    <div className="h-8 bg-orange-400 rounded w-2/3 mt-4" />
                  </div>
                </div>
              </div>
            }
            links={[
              { label: 'Individual', href: '#individual' },
              { label: 'Business', href: '#business' },
              { label: 'Non-profit', href: '#nonprofit' },
            ]}
            variant="mint"
          />

          {/* IRS Audit Assistance */}
          <ServiceCard
            title="IRS Audit Assistance"
            description="Professional representation and support during IRS audits. We handle all correspondence and negotiations with the IRS on your behalf."
            icon={
              <div className="relative w-full h-full">
                {/* Chart/audit illustration */}
                <div className="bg-purple-200 rounded-2xl p-6 shadow-lg">
                  <div className="bg-white rounded-lg p-4 space-y-2">
                    <div className="flex items-end justify-between h-32">
                      <div className="w-8 bg-purple-400 rounded-t" style={{ height: '40%' }} />
                      <div className="w-8 bg-purple-500 rounded-t" style={{ height: '70%' }} />
                      <div className="w-8 bg-purple-600 rounded-t" style={{ height: '55%' }} />
                      <div className="w-8 bg-purple-400 rounded-t" style={{ height: '85%' }} />
                    </div>
                  </div>
                </div>
              </div>
            }
            links={[
              { label: 'Learn more', href: '#audit' },
              { label: 'Resources', href: '#resources' },
              { label: 'Get help', href: '#contact' },
            ]}
            variant="white"
          />

          {/* Bookkeeping */}
          <ServiceCard
            title="Bookkeeping & Accounting"
            description="Complete outsourced bookkeeping and accounting services. Keep your financial records accurate, organized, and always up-to-date."
            icon={
              <div className="relative w-full h-full">
                {/* Ledger/calculator illustration */}
                <div className="bg-red-300 rounded-2xl p-6 shadow-lg transform -rotate-6 hover:rotate-0 transition-transform">
                  <div className="bg-red-400 rounded-lg p-4 space-y-2">
                    <div className="flex gap-2">
                      <div className="w-8 h-8 bg-red-500 rounded" />
                      <div className="w-8 h-8 bg-red-500 rounded" />
                    </div>
                    <div className="flex gap-2">
                      <div className="w-8 h-8 bg-red-500 rounded" />
                      <div className="w-8 h-8 bg-red-600 rounded" />
                    </div>
                  </div>
                </div>
              </div>
            }
            links={[
              { label: 'Learn more', href: '#bookkeeping' },
              { label: 'Accounting', href: '#accounting' },
              { label: 'Payroll', href: '#payroll' },
            ]}
            variant="mint"
          />
        </div>
      </div>
    </section>
  )
}
