import { test, expect } from "@playwright/test";

test.describe("Book Loop - Complete Page Coverage Suite", () => {
  test("France B2C — public legal pages are reachable", async ({ page }) => {
    await page.goto("/mentions-legales");
    await expect(page.getByRole("heading", { name: "Mentions légales" })).toBeVisible();
    await expect(page.getByText("Entrepreneur individuel — régime micro-entreprise")).toBeVisible();
    await expect(page.getByText(/SIREN/)).toBeVisible();
    await expect(page.getByText(/SIRET/)).toBeVisible();
    await expect(page.getByText(/Code APE\/NAF/)).toBeVisible();

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
});
