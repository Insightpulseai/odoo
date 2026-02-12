'use client'

import Link from 'next/link'

export function FinalCTA() {
  return (
    <section className="py-16 md:py-20 lg:py-24 bg-white">
      <div className="container mx-auto px-6 md:px-8 lg:px-16">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-forest-900 leading-tight">
            We believe that tax filing should be seamless, accurate,
            and stress-free. Get started with Noble Finance today!
          </h2>

          <div className="pt-4">
            <Link
              href="#contact"
              className="inline-flex items-center justify-center px-8 py-4 bg-forest-600 text-white font-medium rounded-full hover:bg-forest-700 transition-colors shadow-md hover:shadow-lg text-lg"
            >
              Contact with an expert
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}
