'use client'

import Link from 'next/link'

export function Footer() {
  return (
    <footer className="bg-forest-900 text-white py-16 lg:py-20">
      <div className="px-6 lg:px-16">
        {/* Main Footer Content - Flexbox Layout */}
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-16 mb-12">
          {/* Left Column - Address & Branding */}
          <div className="lg:flex-1 space-y-8">
            <div>
              <p className="text-sm leading-relaxed opacity-80">
                16F Liberty Plaza Building, H.V. dela Costa corner Valero St., Salcedo Village, Makati City 1227 Metro Manila
              </p>
            </div>

            {/* Logo */}
            <div className="flex items-center gap-3">
              <span className="text-xl font-bold leading-none">
                NOBLE FINANCES
              </span>
              <span className="text-xl leading-none">\</span>
              <span className="text-sm opacity-80 leading-none">
                The Clarity Company
              </span>
            </div>
          </div>

          {/* Right Column - Social Media */}
          <div className="lg:flex-1 lg:text-right">
            <div className="flex flex-wrap gap-6 lg:justify-end">
              <Link
                href="https://facebook.com/noblefinances"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm uppercase tracking-[0.1em] opacity-80 hover:opacity-100 transition-opacity"
              >
                Facebook
              </Link>
              <Link
                href="https://youtube.com/noblefinances"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm uppercase tracking-[0.1em] opacity-80 hover:opacity-100 transition-opacity"
              >
                YouTube
              </Link>
              <Link
                href="https://instagram.com/noblefinances"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm uppercase tracking-[0.1em] opacity-80 hover:opacity-100 transition-opacity"
              >
                Instagram
              </Link>
              <Link
                href="https://twitter.com/noblefinances"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm uppercase tracking-[0.1em] opacity-80 hover:opacity-100 transition-opacity"
              >
                Twitter
              </Link>
              <Link
                href="https://linkedin.com/company/noble-finances"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm uppercase tracking-[0.1em] opacity-80 hover:opacity-100 transition-opacity"
              >
                LinkedIn
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Bar - Legal Links */}
        <div className="border-t border-white/10 pt-8">
          <div className="flex flex-wrap gap-6">
            <Link
              href="#terms"
              className="text-sm opacity-60 hover:opacity-100 transition-opacity"
            >
              Terms of Service
            </Link>
            <Link
              href="#privacy"
              className="text-sm opacity-60 hover:opacity-100 transition-opacity"
            >
              Privacy Policy
            </Link>
            <Link
              href="#cookies"
              className="text-sm opacity-60 hover:opacity-100 transition-opacity"
            >
              Cookie Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
