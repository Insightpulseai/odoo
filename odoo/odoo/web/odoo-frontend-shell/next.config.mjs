/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['www.tbwa-smp.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/odoo/:path*',
        destination: `${process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069'}/:path*`,
      },
    ];
  },
};

export default nextConfig;
