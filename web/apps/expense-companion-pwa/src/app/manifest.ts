import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Expense Companion',
    short_name: 'Expense',
    description: 'Concur-style Odoo expense companion for receipt capture, approvals, and payout tracking.',
    start_url: '/',
    display: 'standalone',
    background_color: '#101417',
    theme_color: '#101417',
    orientation: 'portrait',
    icons: [
      {
        src: '/icon-192.svg',
        sizes: '192x192',
        type: 'image/svg+xml',
      },
      {
        src: '/icon-512.svg',
        sizes: '512x512',
        type: 'image/svg+xml',
      },
      {
        src: '/maskable-icon.svg',
        sizes: '512x512',
        type: 'image/svg+xml',
        purpose: 'maskable',
      },
    ],
  };
}
