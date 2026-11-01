import type { Metadata } from "next";
import type { ReactNode } from "react";
import { IBM_Plex_Mono, Newsreader, Source_Sans_3 } from "next/font/google";
import { CodeEnhance } from "@/components/code-enhance";
import { Shell } from "@/components/shell";
import { ThemeProvider } from "@/components/theme-provider";
import { getCatalog } from "@/lib/content";
import "./globals.css";

const sans = Source_Sans_3({ subsets: ["latin"], variable: "--font-source" });
const serif = Newsreader({ subsets: ["latin"], variable: "--font-newsreader" });
const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-plex",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://c.umutabali.com"),
  title: { default: "C Reference", template: "%s · C Reference" },
  description: "A modern C language and standard library reference for c.umutabali.com, derived from cppreference under CC BY-SA 3.0, with C23 notes, diagrams, and search.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const catalog = getCatalog();
  const pages = catalog.pages.map((page) => ({
    slug: page.slug,
    title: page.title,
    category: page.category,
    summary: page.summary,
  }));
  return (
    <html lang="en" className={`${sans.variable} ${serif.variable} ${mono.variable}`} suppressHydrationWarning>
      <body className="font-sans antialiased">
        <ThemeProvider>
          <Shell pages={pages} categories={catalog.categories}>
            {children}
          </Shell>
          <CodeEnhance />
        </ThemeProvider>
      </body>
    </html>
  );
}
