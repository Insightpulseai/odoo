import type { NextConfig } from 'next';
import path from 'node:path';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  outputFileTracingRoot: path.resolve(__dirname),
  async rewrites() {
    if (!process.env.NEXT_PUBLIC_ODOO_URL) {
      return [];
    }

    return [
      {
        source: '/api/odoo/:path*',
        destination: `${process.env.NEXT_PUBLIC_ODOO_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
