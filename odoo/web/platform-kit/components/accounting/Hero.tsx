'use client'

import Link from 'next/link'
import Image from 'next/image'

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-mint-100 to-mint-50 py-16 md:py-24 lg:py-32 mt-[72px]">
      <div className="container mx-auto px-6 md:px-8 lg:px-16">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          {/* Left column - Content */}
          <div className="space-y-6 lg:space-y-8">
            <div className="inline-block">
              <span className="text-forest-700 font-medium text-sm md:text-base">
                Noble Finances
              </span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-forest-900 leading-tight">
              Financial Clarity You Can Trust
            </h1>

            <p className="text-lg md:text-xl text-forest-700 leading-relaxed max-w-xl">
              Expert accounting services that help you navigate the complexities
              of tax filing and financial management with confidence.
            </p>

            <div className="flex flex-wrap gap-4">
              <Link
                href="#contact"
                className="inline-flex items-center justify-center px-6 py-3 bg-forest-600 text-white font-medium rounded-full hover:bg-forest-700 transition-colors shadow-md hover:shadow-lg"
              >
                Get started today
              </Link>
              <Link
                href="#services"
                className="inline-flex items-center justify-center px-6 py-3 bg-white text-forest-700 font-medium rounded-full hover:bg-mint-50 transition-colors border-2 border-forest-200"
              >
                Learn more
              </Link>
            </div>
          </div>

          {/* Right column - Illustration */}
          <div className="relative flex justify-center lg:justify-end">
            <div className="relative w-full max-w-md lg:max-w-lg">
              <div className="aspect-square relative">
                {/* Globe illustration placeholder */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-64 h-64 lg:w-80 lg:h-80 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 shadow-2xl relative overflow-hidden">
                    {/* Continents - simplified representation */}
                    <div className="absolute inset-0 opacity-30">
                      <svg viewBox="0 0 100 100" className="w-full h-full">
                        <circle cx="50" cy="50" r="45" fill="currentColor" className="text-green-500" />
                      </svg>
                    </div>
                    {/* Orbital rings */}
                    <div className="absolute inset-0 border-4 border-orange-400 rounded-full opacity-50 animate-spin-slow" style={{ animationDuration: '20s' }} />
                    <div className="absolute inset-2 border-4 border-yellow-300 rounded-full opacity-50 animate-spin-slow" style={{ animationDuration: '15s', animationDirection: 'reverse' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
