import type { MetadataRoute } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://book-loop-web-nddyzebo7a-od.a.run.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const publicRoutes = [
    "/",
    "/pricing",
    "/guides",
    "/guides/ecrire-un-roman-avec-ia",
    "/guides/garder-coherence-roman-ia",
    "/guides/bible-narrative",
    "/guides/eviter-contradictions-roman",
    "/mentions-legales",
    "/politique-confidentialite",
    "/cgv",
  ];

  return publicRoutes.map((path) => ({
    url: `${SITE_URL}${path}`,
    changeFrequency: path === "/" ? "weekly" : "monthly",
    priority:
      path === "/" ? 1 : path === "/guides" ? 0.8 : path.startsWith("/guides/") ? 0.7 : path === "/pricing" ? 0.7 : 0.3,
  }));
}
