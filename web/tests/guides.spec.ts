import { test, expect } from "@playwright/test";

test.describe("SEO guides", () => {
  test("guides hub exposes the core evergreen articles", async ({ page }) => {
    await page.goto("/guides");
    await expect(page.getByRole("heading", { name: /Écrire avec l’IA sans perdre le fil/i })).toBeVisible();

    const guideCards = page.locator("article");
    await expect(guideCards).toHaveCount(4);
    await expect(guideCards.filter({ hasText: /Écrire un roman avec l’IA/i }).getByRole("link", { name: /Lire le guide/i })).toHaveAttribute("href", "/guides/ecrire-un-roman-avec-ia");
    await expect(guideCards.filter({ hasText: /cohérence d’un roman/i }).getByRole("link", { name: /Lire le guide/i })).toHaveAttribute("href", "/guides/garder-coherence-roman-ia");
    await expect(guideCards.filter({ hasText: /bible narrative/i }).getByRole("link", { name: /Lire le guide/i })).toHaveAttribute("href", "/guides/bible-narrative");
    await expect(guideCards.filter({ hasText: /contradictions dans un roman/i }).getByRole("link", { name: /Lire le guide/i })).toHaveAttribute("href", "/guides/eviter-contradictions-roman");
  });

  test("an evergreen guide has useful metadata and internal navigation", async ({ page }) => {
    await page.goto("/guides/bible-narrative");
    await expect(page).toHaveTitle(/bible narrative/i);
    await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", /bible narrative/i);
    await expect(page.getByRole("link", { name: /Tous les guides/i })).toBeVisible();
  });
});
