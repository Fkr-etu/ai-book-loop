import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Conditions générales de vente",
  alternates: { canonical: "/cgv" },
};

export default function CgvLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
