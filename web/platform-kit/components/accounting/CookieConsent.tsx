'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const consent = localStorage.getItem('cookie-consent')
    if (!consent) {
      setIsVisible(true)
    }
  }, [])

  const acceptCookies = () => {
    localStorage.setItem('cookie-consent', 'accepted')
    setIsVisible(false)
  }

  const declineCookies = () => {
    localStorage.setItem('cookie-consent', 'declined')
    setIsVisible(false)
  }

  if (!isVisible) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-forest-900 text-white">
      <div className="px-6 lg:px-16 py-6">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex-1">
            <p className="text-sm leading-relaxed opacity-90">
              We use cookies to enhance your browsing experience and analyze our traffic.
              By clicking "Accept", you consent to our use of cookies.{' '}
              <Link href="#privacy" className="underline hover:opacity-60 transition-opacity">
                Learn more
              </Link>
            </p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={declineCookies}
              className="px-6 py-2 text-[13px] font-medium uppercase tracking-[0.1em] border border-white/20 rounded hover:bg-white/10 transition-colors"
            >
              Decline
            </button>
            <button
              onClick={acceptCookies}
              className="px-6 py-2 text-[13px] font-medium uppercase tracking-[0.1em] bg-white text-forest-900 rounded hover:bg-white/90 transition-colors"
            >
              Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
