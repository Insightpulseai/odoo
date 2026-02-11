import { DocLayout } from '@/components/DocLayout'
import { Heading, Text } from '@primer/react'
import GettingStartedContent from '@/content/getting-started.mdx'

export default function GettingStartedPage() {
  return (
    <DocLayout>
      <GettingStartedContent />
    </DocLayout>
  )
}
