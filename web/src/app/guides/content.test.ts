import { describe, expect, it } from "vitest";
import { GUIDE_ROUTES } from "./content";

describe("guide routes", () => {
  it("contains the initial public SEO guides", () => {
    expect(GUIDE_ROUTES).toHaveLength(4);
    expect(new Set(GUIDE_ROUTES).size).toBe(4);
  });
});
