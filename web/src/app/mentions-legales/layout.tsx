import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mentions légales",
  alternates: { canonical: "/mentions-legales" },
};

export default function LegalLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
