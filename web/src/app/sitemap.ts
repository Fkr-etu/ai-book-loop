import type { MetadataRoute } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://book-loop-web-nddyzebo7a-od.a.run.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const publicRoutes = ["/", "/pricing", "/mentions-legales", "/politique-confidentialite", "/cgv"];

  return publicRoutes.map((path) => ({
    url: `${SITE_URL}${path}`,
    changeFrequency: path === "/" ? "weekly" : "monthly",
    priority: path === "/" ? 1 : path === "/pricing" ? 0.7 : 0.3,
  }));
}
