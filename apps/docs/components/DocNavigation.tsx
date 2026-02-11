'use client'

import { NavList, Box, Heading } from '@primer/react'
import { BookIcon, CodeIcon, GearIcon, PersonIcon, RocketIcon } from '@primer/octicons-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function DocNavigation() {
  const pathname = usePathname()

  return (
    <Box sx={{ padding: 3, borderRight: '1px solid', borderColor: 'border.default', height: '100vh', overflowY: 'auto' }}>
      <Heading as="h2" sx={{ fontSize: 2, marginBottom: 3 }}>
        Documentation
      </Heading>

      <NavList>
        <NavList.Item as={Link} href="/getting-started" aria-current={pathname?.startsWith('/getting-started') ? 'page' : undefined}>
          <NavList.LeadingVisual>
            <RocketIcon />
          </NavList.LeadingVisual>
          Getting Started
        </NavList.Item>

        <NavList.Item as={Link} href="/developer" aria-current={pathname?.startsWith('/developer') ? 'page' : undefined}>
          <NavList.LeadingVisual>
            <CodeIcon />
          </NavList.LeadingVisual>
          Developer
        </NavList.Item>

        <NavList.Item as={Link} href="/administrator" aria-current={pathname?.startsWith('/administrator') ? 'page' : undefined}>
          <NavList.LeadingVisual>
            <GearIcon />
          </NavList.LeadingVisual>
          Administrator
        </NavList.Item>

        <NavList.Item as={Link} href="/user" aria-current={pathname?.startsWith('/user') ? 'page' : undefined}>
          <NavList.LeadingVisual>
            <PersonIcon />
          </NavList.LeadingVisual>
          User Guides
        </NavList.Item>

        <NavList.Item as={Link} href="/platform-kit" aria-current={pathname?.startsWith('/platform-kit') ? 'page' : undefined}>
          <NavList.LeadingVisual>
            <BookIcon />
          </NavList.LeadingVisual>
          Platform Kit
        </NavList.Item>
      </NavList>

      <Box sx={{ marginTop: 4 }}>
        <Heading as="h3" sx={{ fontSize: 1, marginBottom: 2, color: 'fg.muted' }}>
          Version
        </Heading>
        <select style={{ width: '100%', padding: '8px', borderRadius: '6px' }}>
          <option value="19.0">19.0 (Latest)</option>
          <option value="18.0">18.0</option>
        </select>
      </Box>
    </Box>
  )
}
