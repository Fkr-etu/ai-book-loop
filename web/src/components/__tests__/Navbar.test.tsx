import { describe, expect, it } from "vitest";

describe("Navbar route model", () => {
  const publicRoutes = ["/", "/login", "/register", "/pricing"];

  it("keeps private workspace routes out of public navigation", () => {
    expect(publicRoutes).not.toContain("/dashboard");
    expect(publicRoutes).not.toContain("/studio");
    expect(publicRoutes).not.toContain("/studio/export");
    expect(publicRoutes).not.toContain("/account");
  });

  it("recognizes only the intended public routes", () => {
    expect(publicRoutes).toEqual(["/", "/login", "/register", "/pricing"]);
  });
});
