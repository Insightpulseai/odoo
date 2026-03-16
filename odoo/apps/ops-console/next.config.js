/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  transpilePackages: [
    '@fluentui/react-components',
    '@fluentui/react-icons',
    '@fluentui/react-charting',
  ],
}
module.exports = nextConfig
