/**
 * Root layout — applies global fonts, metadata, and CSS to all pages.
 *
 * Configures DM Sans (body) and Lora (display) fonts via next/font/google
 * and sets the base HTML structure for the Voyager application.
 */

import type { Metadata } from "next";
import { DM_Sans, Lora, Inter, Fraunces } from 'next/font/google';
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
});

const lora = Lora({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
  style: ['normal', 'italic'],
});

export const metadata: Metadata = {
  title: "Voyager",
  description: "The world's first constraint-solving, vibe-reading travel intelligence engine.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${dmSans.variable} ${lora.variable} font-sans antialiased bg-background text-foreground`}>
        {children}
      </body>
    </html>
  );
}
