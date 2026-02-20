import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Control Plane',
  description: 'BugBot, Vercel Bot, and infrastructure automation via Vercel AI Gateway + Supabase Vault',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
