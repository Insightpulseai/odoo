import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TBWA Odoo Portal',
  description: 'Decoupled frontend for Odoo CE 18',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
