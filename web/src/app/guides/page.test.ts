import { describe, expect, it } from "vitest";

describe("SEO guides", () => {
  it("defines the expected public guide routes", () => {
    const routes = [
      "/guides",
      "/guides/ecrire-un-roman-avec-ia",
      "/guides/garder-coherence-roman-ia",
      "/guides/bible-narrative",
      "/guides/eviter-contradictions-roman",
    ];

    expect(routes).toHaveLength(5);
    expect(new Set(routes).size).toBe(routes.length);
  });
});
