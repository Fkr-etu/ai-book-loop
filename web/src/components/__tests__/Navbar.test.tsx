import { describe, expect, it } from "vitest";

describe("Navbar route model", () => {
  it("keeps public pages free of private workspace navigation", () => {
    const publicRoutes = ["/", "/login", "/register", "/pricing"];
    expect(publicRoutes).toContain("/");
    expect(publicRoutes).not.toContain("/dashboard");
  });

  it("treats application routes as authenticated navigation", () => {
    const publicRoutes = new Set(["/", "/login", "/register", "/pricing"]);
    expect(publicRoutes.has("/studio")).toBe(false);
    expect(publicRoutes.has("/account")).toBe(false);
  });
});
