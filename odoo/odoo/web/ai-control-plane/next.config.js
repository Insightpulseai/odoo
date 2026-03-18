/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow external API calls
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
};

module.exports = nextConfig;
