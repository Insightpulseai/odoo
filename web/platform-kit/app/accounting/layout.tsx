import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Noble Finances - Accounting Services',
  description: 'Professional accounting and tax services',
}

export default function AccountingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
