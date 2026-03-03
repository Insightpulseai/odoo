import type { Metadata, Viewport } from "next";

import "./globals.css";
import { Geist, Geist_Mono } from "next/font/google";

import { Providers } from "./providers";
import { Header } from "./_components/header";
import { Footer } from "./_components/footer";

const geist = Geist({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
  fallback: [
    "Inter",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
    "Roboto",
    "Oxygen",
    "Ubuntu",
    "Cantarell",
    "Fira Sans",
    "Droid Sans",
    "Helvetica Neue",
    "sans-serif",
  ],
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
  fallback: ["monaco", "monospace"],
});

export const metadata: Metadata = {
  title: "InsightPulseAI — Enterprise ERP, Powered by AI",
  description:
    "Self-hosted Odoo 19 + intelligent automation for Philippine enterprises",
};

export const viewport: Viewport = {
  maximumScale: 1, // Disable auto-zoom on mobile Safari
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning lang="en">
      <body
        className={`min-h-svh max-w-[100vw] bg-neutral-bg1 text-neutral-fg1 ${geistMono.variable} ${geist.variable} font-sans`}
      >
        <Providers>
          <Header />
          <main className="min-h-[calc(100svh-var(--header-height))]">
            {children}
          </main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
