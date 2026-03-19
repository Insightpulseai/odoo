'use client'

import { useEffect, useCallback } from 'react'

declare global {
  interface Window {
    Paddle?: {
      Initialize: (options: { token: string }) => void
      Checkout: {
        open: (options: {
          items: Array<{ priceId: string; quantity: number }>
          customer?: { email: string }
          customData?: Record<string, string>
          successCallback?: () => void
        }) => void
      }
    }
  }
}

interface PaddleCheckoutProps {
  priceId: string
  email?: string
  customData?: Record<string, string>
  onSuccess?: () => void
}

export function usePaddleCheckout() {
  useEffect(() => {
    // Load Paddle.js if not already loaded
    if (typeof window !== 'undefined' && !window.Paddle) {
      const script = document.createElement('script')
      script.src = 'https://cdn.paddle.com/paddle/v2/paddle.js'
      script.async = true
      script.onload = () => {
        if (window.Paddle && process.env.NEXT_PUBLIC_PADDLE_CLIENT_TOKEN) {
          window.Paddle.Initialize({
            token: process.env.NEXT_PUBLIC_PADDLE_CLIENT_TOKEN,
          })
        }
      }
      document.body.appendChild(script)
    }
  }, [])

  const openCheckout = useCallback(
    ({ priceId, email, customData, onSuccess }: PaddleCheckoutProps) => {
      if (!window.Paddle) {
        console.error('Paddle.js not loaded')
        return
      }

      window.Paddle.Checkout.open({
        items: [{ priceId, quantity: 1 }],
        customer: email ? { email } : undefined,
        customData,
        successCallback: onSuccess,
      })
    },
    []
  )

  return { openCheckout }
}
