import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Control Plane',
  description: 'BugBot, Vercel Bot, Odoo.sh-equivalent platform control, and infrastructure automation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">{children}</body>
    </html>
  );
}
