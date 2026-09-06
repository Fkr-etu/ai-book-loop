import type { Metadata } from "next";
import { Playfair_Display, Merriweather, Inter, Courier_Prime } from "next/font/google";
import { Providers } from "@/components/Providers";
import "./globals.css";

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
});

const merriweather = Merriweather({
  weight: ["300", "400", "700"],
  subsets: ["latin"],
  variable: "--font-merriweather",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const courier = Courier_Prime({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-courier",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Book Loop — Gardez votre histoire cohérente",
    template: "%s — Book Loop",
  },
  description: "Écrivez avec l'IA sans perdre le fil de votre histoire. Book Loop protège la cohérence de votre univers au fil de ses évolutions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className={`${playfair.variable} ${merriweather.variable} ${inter.variable} ${courier.variable}`}>
      <body className="antialiased min-h-screen bg-[#f8f9ff] text-[#0b1c30] selection:bg-[#ffddb8] selection:text-[#0b1c30]">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
