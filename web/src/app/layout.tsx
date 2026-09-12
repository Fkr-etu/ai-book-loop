import type { Metadata } from "next";
import { Playfair_Display, Merriweather, Inter, Courier_Prime } from "next/font/google";
import { Providers } from "@/components/Providers";
import { CookieConsent } from "@/components/CookieConsent";
import { AnalyticsBootstrap } from "@/components/AnalyticsBootstrap";
import "./globals.css";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://book-loop-web-nddyzebo7a-od.a.run.app";

const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair", display: "swap" });
const merriweather = Merriweather({ weight: ["300", "400", "700"], subsets: ["latin"], variable: "--font-merriweather", display: "swap" });
const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const courier = Courier_Prime({ weight: ["400", "700"], subsets: ["latin"], variable: "--font-courier", display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Book Loop — Écrire, reprendre son histoire, garder le fil",
    template: "%s — Book Loop",
  },
  description: "Écrivez vos histoires à votre rythme, retrouvez ce qui s'est déjà passé et continuez sans perdre le fil.",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "fr_FR",
    url: "/",
    siteName: "Book Loop",
    title: "Book Loop — Écrire, reprendre son histoire, garder le fil",
    description: "Un atelier pour écrire des histoires longues sans perdre le fil.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Book Loop — Écrire, reprendre son histoire, garder le fil",
    description: "Écrivez, relisez et continuez votre histoire sans perdre ce qui compte.",
  },
  icons: {
    icon: [
      { url: "/brand/favicon-256.png", type: "image/png", sizes: "256x256" },
      { url: "/brand/symbol-transparent.svg", type: "image/svg+xml" },
    ],
    shortcut: "/brand/favicon-256.png",
    apple: [{ url: "/brand/favicon-256.png", type: "image/png", sizes: "256x256" }],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr" className={`${playfair.variable} ${merriweather.variable} ${inter.variable} ${courier.variable}`}>
      <body className="antialiased min-h-screen bg-[#f8f9ff] text-[#0b1c30] selection:bg-[#ffddb8] selection:text-[#0b1c30]">
        <Providers>
          {children}
          <CookieConsent />
          <AnalyticsBootstrap />
        </Providers>
      </body>
    </html>
  );
}
