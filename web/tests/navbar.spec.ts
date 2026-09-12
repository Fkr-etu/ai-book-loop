import { test, expect } from "@playwright/test";

test.describe("public navigation", () => {
  test("homepage exposes public navigation only", async ({ page }) => {
    await page.goto("/");
    const header = page.locator("header");
    await expect(header.getByRole("link", { name: "Mes livres" })).toHaveCount(0);
    await expect(header.getByRole("link", { name: "Atelier" })).toHaveCount(0);
    await expect(header.getByRole("link", { name: "Exportation" })).toHaveCount(0);
    await expect(header.getByRole("link", { name: "Compte" })).toHaveCount(0);
    await expect(header.getByRole("link", { name: "Se connecter" })).toBeVisible();
    await expect(header.getByRole("link", { name: "Commencer" })).toBeVisible();
  });

  test("homepage uses the official Book Loop lockup", async ({ page }) => {
    await page.goto("/");
    const logo = page.locator('header a[aria-label="Book Loop — accueil"] img');
    await expect(logo).toHaveAttribute("src", /\/brand\/lockup-horizontal\.svg/);
    await expect(logo).toHaveAttribute("alt", "Book Loop");
  });
});
