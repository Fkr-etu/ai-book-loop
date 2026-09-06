import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Guides d’écriture IA et cohérence narrative",
  description: "Guides pratiques pour écrire avec l’IA, construire une bible narrative et préserver la cohérence d’une histoire longue.",
};

export default function GuidesLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
