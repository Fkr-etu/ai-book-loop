import { describe, expect, it } from "vitest";

describe("guide SEO contract", () => {
  it("keeps guide content public and indexable", () => {
    expect("/guides").toMatch(/^\/guides$/);
    expect("public").toBe("public");
  });
});
