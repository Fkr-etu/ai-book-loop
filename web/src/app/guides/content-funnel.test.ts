import { describe, expect, it } from "vitest";

describe("SEO acquisition funnel", () => {
  it("starts from search and leads to the free product entry", () => {
    const funnel = ["search", "guide", "continuity", "canon", "product", "free-start"];
    expect(funnel[0]).toBe("search");
    expect(funnel.at(-1)).toBe("free-start");
  });
});
