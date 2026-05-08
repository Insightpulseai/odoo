import type { Metadata, Viewport } from 'next';
import './globals.css';
import ServiceWorkerRegistration from '@/components/ServiceWorkerRegistration';
import { MsalProvider } from '@/lib/auth/MsalProvider';

export const metadata: Metadata = {
  title: 'Expense Companion',
  description: 'Concur-style Odoo expense companion for mobile-first receipt capture and approvals.',
  manifest: '/manifest.webmanifest',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Expense Companion',
  },
  icons: {
    icon: [
      { url: '/icon-192.svg', type: 'image/svg+xml' },
      { url: '/icon-512.svg', type: 'image/svg+xml' },
    ],
    apple: '/icon-192.svg',
  },
};

export const viewport: Viewport = {
  themeColor: '#101417',
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ServiceWorkerRegistration />
        <MsalProvider>{children}</MsalProvider>
      </body>
    </html>
  );
}
