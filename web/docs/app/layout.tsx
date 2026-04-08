import { Footer, Layout, Navbar } from 'nextra-theme-docs'
import { Banner, Head } from 'nextra/components'
import { getPageMap } from 'nextra/page-map'
import 'nextra-theme-docs/style.css'

export const metadata = {
  title: {
    default: 'InsightPulse AI Docs',
    template: '%s — InsightPulse AI Docs',
  },
  description: 'InsightPulse AI Platform Documentation — Odoo CE 19, Agent Platform, Data Intelligence',
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head />
      <body>
        <Layout
          banner={
            <Banner storageKey="docs-preview">
              This documentation is in preview. Content is being actively developed.
            </Banner>
          }
          navbar={
            <Navbar
              logo={
                <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>
                  InsightPulse AI Docs
                </span>
              }
              projectLink="https://github.com/Insightpulseai/odoo"
            />
          }
          pageMap={await getPageMap()}
          docsRepositoryBase="https://github.com/Insightpulseai/odoo/tree/main/web/docs"
          editLink="Edit this page on GitHub →"
          sidebar={{ defaultMenuCollapseLevel: 1, toggleButton: true }}
          footer={
            <Footer>
              © {new Date().getFullYear()} InsightPulse AI. Built on Odoo CE 19 + Azure.
            </Footer>
          }
        >
          {children}
        </Layout>
      </body>
    </html>
  )
}
