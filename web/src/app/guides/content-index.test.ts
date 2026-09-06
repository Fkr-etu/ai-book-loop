import { describe, expect, it } from "vitest";
import { SEO_GUIDES } from "./content-index";

describe("SEO guide index", () => {
  it("tracks the initial content set", () => {
    expect(SEO_GUIDES).toBe(4);
  });
});
