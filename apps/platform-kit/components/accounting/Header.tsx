'use client'

import Link from 'next/link'
import { useState } from 'react'

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white">
      <div className="px-6 lg:px-16">
        <div className="flex items-center justify-between py-6">
          {/* Logo - Left Aligned */}
          <Link href="/accounting" className="flex-shrink-0">
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold text-forest-900 leading-none">
                NOBLE FINANCES
              </span>
              <span className="text-forest-900 text-xl leading-none">\</span>
              <span className="text-sm text-forest-600 leading-none">
                The Clarity Company
              </span>
            </div>
          </Link>

          {/* Desktop Navigation - Right Aligned */}
          <nav className="hidden lg:block">
            <ul className="flex items-center gap-8">
              <li>
                <Link
                  href="#news"
                  className="text-[13px] font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                >
                  News
                </Link>
              </li>
              <li>
                <Link
                  href="#services"
                  className="text-[13px] font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                >
                  Services
                </Link>
              </li>
              <li>
                <Link
                  href="#works"
                  className="text-[13px] font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                >
                  Works
                </Link>
              </li>
              <li>
                <Link
                  href="#contact"
                  className="text-[13px] font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                >
                  Contact
                </Link>
              </li>
              <li>
                <button
                  className="text-[13px] font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                  aria-label="Search"
                >
                  Search
                </button>
              </li>
            </ul>
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 text-forest-900"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {mobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Offcanvas Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 top-[72px] bg-white z-40">
          <nav className="px-6 py-12">
            <ul className="flex flex-col gap-8">
              <li>
                <Link
                  href="#news"
                  className="text-2xl font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  News
                </Link>
              </li>
              <li>
                <Link
                  href="#services"
                  className="text-2xl font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Services
                </Link>
              </li>
              <li>
                <Link
                  href="#works"
                  className="text-2xl font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Works
                </Link>
              </li>
              <li>
                <Link
                  href="#contact"
                  className="text-2xl font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Contact
                </Link>
              </li>
              <li>
                <button
                  className="text-2xl font-medium text-forest-900 uppercase tracking-[0.1em] hover:opacity-60 transition-opacity"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Search
                </button>
              </li>
            </ul>
          </nav>
        </div>
      )}
    </header>
  )
}
