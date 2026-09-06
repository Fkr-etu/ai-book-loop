import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Book Loop",
    short_name: "Book Loop",
    description: "Atelier d’écriture IA pour les histoires longues, avec un Canon narratif pour préserver la cohérence.",
    start_url: "/",
    display: "standalone",
    lang: "fr-FR",
    background_color: "#F7F2E9",
    theme_color: "#13243A",
    icons: [
      {
        src: "/book-loop-mark.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any",
      },
    ],
  };
}
