import { PageLayout, Heading, Text, Box, Link as PrimerLink } from '@primer/react'
import { BookIcon, CodeIcon, GearIcon, PersonIcon } from '@primer/octicons-react'
import Link from 'next/link'

export default function HomePage() {
  return (
    <PageLayout>
      <PageLayout.Header>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, padding: 3 }}>
          <BookIcon size={32} />
          <Heading as="h1">Odoo Documentation</Heading>
        </Box>
      </PageLayout.Header>

      <PageLayout.Content>
        <Box sx={{ maxWidth: 1200, margin: '0 auto', padding: 4 }}>
          <Box sx={{ marginBottom: 6 }}>
            <Heading as="h2" sx={{ marginBottom: 2 }}>
              Welcome to Odoo Documentation
            </Heading>
            <Text as="p" sx={{ fontSize: 2, color: 'fg.muted' }}>
              Comprehensive guides and API references for Odoo 18/19 with IPAI Platform extensions
            </Text>
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: ['1fr', '1fr 1fr'], gap: 4 }}>
            <DocCard
              icon={<CodeIcon size={24} />}
              title="Developer Documentation"
              description="Learn about ORM, Views, OWL, Security, and Testing"
              href="/developer"
            />

            <DocCard
              icon={<GearIcon size={24} />}
              title="Administrator Guide"
              description="Database management, user permissions, and system configuration"
              href="/administrator"
            />

            <DocCard
              icon={<PersonIcon size={24} />}
              title="User Guides"
              description="Module-specific guides for Accounting, HR, CRM, and more"
              href="/user"
            />

            <DocCard
              icon={<BookIcon size={24} />}
              title="Getting Started"
              description="Installation, tutorials, and quick start guides"
              href="/getting-started"
            />
          </Box>

          <Box sx={{ marginTop: 6, padding: 4, backgroundColor: 'canvas.subtle', borderRadius: 2 }}>
            <Heading as="h3" sx={{ marginBottom: 2 }}>
              IPAI Platform Extensions
            </Heading>
            <Text as="p" sx={{ marginBottom: 3 }}>
              Beyond standard Odoo documentation, we provide guides for:
            </Text>
            <Box as="ul" sx={{ paddingLeft: 4 }}>
              <li>Supabase integration and Edge Functions</li>
              <li>EE → CE/OCA parity mapping</li>
              <li>AI Agent workflows and automation</li>
              <li>BIR compliance and OCR processing</li>
            </Box>
          </Box>
        </Box>
      </PageLayout.Content>
    </PageLayout>
  )
}

function DocCard({ icon, title, description, href }: {
  icon: React.ReactNode
  title: string
  description: string
  href: string
}) {
  return (
    <Link href={href} passHref legacyBehavior>
      <PrimerLink
        as="a"
        sx={{
          display: 'block',
          padding: 4,
          border: '1px solid',
          borderColor: 'border.default',
          borderRadius: 2,
          textDecoration: 'none',
          transition: 'all 0.2s',
          '&:hover': {
            borderColor: 'accent.emphasis',
            boxShadow: 'shadow.medium',
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, marginBottom: 2 }}>
          {icon}
          <Heading as="h3" sx={{ fontSize: 3 }}>{title}</Heading>
        </Box>
        <Text as="p" sx={{ color: 'fg.muted' }}>
          {description}
        </Text>
      </PrimerLink>
    </Link>
  )
}
