import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Platform Kit uses monaco-editor which requires this
  transpilePackages: ['@monaco-editor/react'],
}

export default nextConfig
