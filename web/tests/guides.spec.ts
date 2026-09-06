import { test, expect } from "@playwright/test";

test.describe("SEO guides", () => {
  test("guides hub exposes the core evergreen articles", async ({ page }) => {
    await page.goto("/guides");
    await expect(page.getByRole("heading", { name: /Écrire avec l’IA sans perdre le fil/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Écrire un roman avec l’IA/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /cohérence d’un roman/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /bible narrative/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /contradictions dans un roman/i })).toBeVisible();
  });

  test("an evergreen guide has useful metadata and internal navigation", async ({ page }) => {
    await page.goto("/guides/bible-narrative");
    await expect(page).toHaveTitle(/bible narrative/i);
    await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", /bible narrative/i);
    await expect(page.getByRole("link", { name: /Tous les guides/i })).toBeVisible();
  });
});
