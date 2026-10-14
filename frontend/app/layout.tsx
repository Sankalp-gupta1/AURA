import type { Metadata } from "next";
import { Space_Grotesk, Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import SessionCleanup from "@/components/SessionCleanup";

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display-loaded",
  weight: ["500", "700"],
});
const body = Inter({ subsets: ["latin"], variable: "--font-body-loaded" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], variable: "--font-mono-loaded", weight: ["400", "500"] });

export const metadata: Metadata = {
  title: "AURA — Personal AI Operating System",
  description: "Your inbox, calendar, and tasks — unified into one intelligence layer.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body className="antialiased"><SessionCleanup />{children}</body>
    </html>
  );
}
