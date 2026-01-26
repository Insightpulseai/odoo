'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg" />
            <span className="font-bold text-xl text-gray-900">InsightPulse AI</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            <Link href="/pricing" className="text-gray-600 hover:text-gray-900 transition-colors">
              Pricing
            </Link>
            <Link href="/features" className="text-gray-600 hover:text-gray-900 transition-colors">
              Features
            </Link>
            <Link href="/docs" className="text-gray-600 hover:text-gray-900 transition-colors">
              Documentation
            </Link>
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <Link href="/auth/signin" className="text-gray-600 hover:text-gray-900 transition-colors">
              Sign in
            </Link>
            <Link href="/auth/signup" className="btn btn-primary">
              Get Started
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-4">
            <Link href="/pricing" className="block py-2 text-gray-600 hover:text-gray-900">
              Pricing
            </Link>
            <Link href="/features" className="block py-2 text-gray-600 hover:text-gray-900">
              Features
            </Link>
            <Link href="/docs" className="block py-2 text-gray-600 hover:text-gray-900">
              Documentation
            </Link>
            <hr className="my-4" />
            <Link href="/auth/signin" className="block py-2 text-gray-600 hover:text-gray-900">
              Sign in
            </Link>
            <Link href="/auth/signup" className="btn btn-primary w-full text-center">
              Get Started
            </Link>
          </div>
        )}
      </nav>
    </header>
  )
}
