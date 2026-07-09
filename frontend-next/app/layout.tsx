import type { Metadata } from "next";
import { Quicksand, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

import { ThemeToggle } from "@/components/layout/ThemeToggle";


const quicksand = Quicksand({
  variable: "--font-quicksand",
  subsets: ["latin"],
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "ComplyScan — NABH Compliance Analysis",
  description:
    "Healthcare compliance analysis tool for NABH accreditation standards",
  icons: {
    icon: "/app/favicon.ico",
    apple: "/app/apple-touch-icon.png",
  },
  manifest: "/app/site.webmanifest",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${quicksand.variable} ${jetbrains.variable} h-full`}
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const theme = localStorage.getItem('complyscan-theme');
                if (theme === 'dark') {
                  document.documentElement.classList.add('dark');
                }
              } catch(e) {}
            `,
          }}
        />
      </head>
      <body className="min-h-full bg-background text-foreground antialiased">
        <Providers>
          <ThemeToggle />
          {children}
        </Providers>
        {/* Global advisory disclaimer — BR-5 / FR-5.1 */}
        <div className="fixed bottom-0 inset-x-0 z-50 bg-background/80 backdrop-blur-sm border-t border-border px-4 py-2">
          <p className="text-center text-[11px] text-muted-foreground">
            Advisory tool only — not a substitute for an official NABH assessment.
          </p>
        </div>
      </body>
    </html>
  );
}
