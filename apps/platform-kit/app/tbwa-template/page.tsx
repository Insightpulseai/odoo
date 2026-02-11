import { Header } from '@/components/tbwa-template/Header'
import { Footer } from '@/components/tbwa-template/Footer'
import { CookieConsent } from '@/components/tbwa-template/CookieConsent'
import { MattermostHero } from '@/components/tbwa-template/MattermostHero'

export const metadata = {
  title: 'TBWA Template',
  description: 'Clean template based on TBWA-SMP structure',
}

export default function TBWATemplatePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-[72px]">
        <MattermostHero />
      </main>
      <Footer />
      <CookieConsent />
    </div>
  )
}
