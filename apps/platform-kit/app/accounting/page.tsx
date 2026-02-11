import { Header } from '@/components/accounting/Header'
import { Footer } from '@/components/accounting/Footer'
import { CookieConsent } from '@/components/accounting/CookieConsent'

export const metadata = {
  title: 'Template - TBWA Style',
  description: 'Clean template with TBWA-style header, footer, and cookie consent.',
}

export default function AccountingPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-[72px]">
        {/* Your content goes here */}
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-forest-900 mb-4">
              Template Ready
            </h1>
            <p className="text-lg text-forest-700">
              Add your content here
            </p>
          </div>
        </div>
      </main>
      <Footer />
      <CookieConsent />
    </div>
  )
}
