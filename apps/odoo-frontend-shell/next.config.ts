import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['www.tbwa-smp.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/odoo/:path*',
        destination: `${process.env.NEXT_PUBLIC_ODOO_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
