'use client'

import Link from 'next/link'

export function ValueProp() {
  return (
    <section className="py-16 md:py-20 bg-white">
      <div className="container mx-auto px-6 md:px-8 lg:px-16">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="space-y-4">
            <p className="text-sm md:text-base text-forest-600 font-medium uppercase tracking-wider">
              Services
            </p>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-forest-900 leading-tight">
              Let us handle the numbers,
              <br />
              so you can handle your success.
            </h2>
          </div>

          <p className="text-lg md:text-xl text-forest-700 leading-relaxed max-w-2xl mx-auto">
            Serving individuals and businesses across the United States
            since 1987
          </p>

          <div className="pt-4">
            <Link
              href="#services"
              className="inline-flex items-center justify-center px-8 py-4 bg-forest-600 text-white font-medium rounded-full hover:bg-forest-700 transition-colors shadow-md hover:shadow-lg"
            >
              Learn more
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}
