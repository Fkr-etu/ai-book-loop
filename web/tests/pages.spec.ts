import { test, expect } from "@playwright/test";

test.describe("Book Loop - Complete Page Coverage Suite", () => {
  test("France B2C — public legal pages are reachable", async ({ page }) => {
    await page.goto("/mentions-legales");
    await expect(page.getByRole("heading", { name: "Mentions légales" })).toBeVisible();
    await expect(page.getByText("Entrepreneur individuel — régime micro-entreprise")).toBeVisible();
    await expect(page.getByText("SIREN", { exact: true })).toBeVisible();
    await expect(page.getByText("SIRET", { exact: true })).toBeVisible();
    await expect(page.getByText("Code APE/NAF", { exact: true })).toBeVisible();

    await page.goto("/cgv");
    await expect(page.getByRole("heading", { name: "Conditions générales de vente" })).toBeVisible();
    await expect(page.getByText(/entrepreneur individuel sous régime micro-entreprise/)).toBeVisible();

    await page.goto("/politique-confidentialite");
    await expect(page.getByRole("heading", { name: "Politique de confidentialité" })).toBeVisible();
  });

  test("France B2C — legal identity placeholders cannot look like final data", async ({ page }) => {
    await page.goto("/mentions-legales");
    await expect(page.getByText(/À COMPLÉTER — numéro SIREN/)).toBeVisible();
    await expect(page.getByText(/À COMPLÉTER — prénom et nom/)).toBeVisible();
  });

  test("France B2C — cookie choice is explicit and persisted", async ({ page }) => {
    await page.goto("/mentions-legales");
    const banner = page.getByRole("complementary", { name: "Préférences de cookies" });
    await expect(banner).toBeVisible();
    await page.getByRole("button", { name: "Refuser" }).click();
    await expect(banner).toBeHidden();
    await page.reload();
    await expect(banner).toBeHidden();
  });

  test("SEO — public pages expose canonical URLs", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", /\/?$/);
    await page.goto("/guides");
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", /\/guides\/?$/);
    await page.goto("/pricing");
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", /\/pricing\/?$/);
  });

  test("SEO — private and authentication pages are noindex", async ({ page }) => {
    for (const path of ["/login", "/register", "/setup", "/dashboard", "/studio", "/parametres"]) {
      await page.goto(path);
      await expect(page.locator('meta[name="robots"]')).toHaveAttribute("content", /noindex/);
    }
  });

  test("SEO — discovery files are available", async ({ request }) => {
    const robots = await request.get("/robots.txt");
    expect(robots.ok()).toBeTruthy();
    expect(await robots.text()).toContain("/sitemap.xml");

    const sitemap = await request.get("/sitemap.xml");
    expect(sitemap.ok()).toBeTruthy();
    expect(await sitemap.text()).toContain("/guides");

    const manifest = await request.get("/manifest.webmanifest");
    expect(manifest.ok()).toBeTruthy();
  });
});
