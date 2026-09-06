import { describe, expect, it } from "vitest";
import { GUIDE_SLUGS } from "./index";

describe("guide index", () => {
  it("contains the four initial evergreen guides", () => {
    expect(GUIDE_SLUGS).toEqual([
      "ecrire-un-roman-avec-ia",
      "garder-coherence-roman-ia",
      "bible-narrative",
      "eviter-contradictions-roman",
    ]);
  });
});
