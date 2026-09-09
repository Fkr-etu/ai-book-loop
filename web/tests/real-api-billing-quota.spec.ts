import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API billing quota", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("Free plan blocks the second project and surfaces the backend quota refusal", async ({ page }) => {
    const email = `billing-quota-e2e-${Date.now()}@bookloop-e2e.com`;
    const password = "BookLoop-Billing-123!";

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByPlaceholder("Votre nom ou pseudonyme").fill("Billing E2E Author");
    await page.getByPlaceholder("votre@email.com").fill(email);
    await page.getByPlaceholder("Créez un mot de passe robuste").fill(password);
    await page.getByRole("button", { name: "Créer mon compte", exact: true }).click();

    await expect(page).toHaveURL(/\/setup$/);
    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Projet quota Free");
    await page.getByRole("button", { name: "Fantasy" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill("Vérifier que la capacité projet est imposée par le backend.");
    await page.getByTestId("next-step-btn").click();
    await page.getByLabel("Qu'aimeriez-vous faire ressentir, raconter ou explorer ?").fill("Vérifier les limites du forfait.");
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();
    await page.getByRole("button", { name: /C'est bien ça — commencer l'atelier/ }).click();

    await expect(page).toHaveURL(/\/studio\?bookId=/);
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Bibliothèque & Tableau de Bord" })).toBeVisible();
    await expect(page.getByText("Vos récits (1)")).toBeVisible();

    await page.getByRole("link", { name: "Commencer un livre" }).click();
    await expect(page).toHaveURL(/\/setup$/);
    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Projet quota refusé");
    await page.getByRole("button", { name: "Fantasy" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill("Ce projet doit être refusé par la capacité du forfait Free.");
    await page.getByTestId("next-step-btn").click();
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();

    const createResponsePromise = page.waitForResponse(
      (response) => response.url().endsWith("/api/books") && response.request().method() === "POST"
    );
    await page.getByRole("button", { name: /C'est bien ça — commencer l'atelier/ }).click();

    const createResponse = await createResponsePromise;
    expect(createResponse.status()).toBe(429);
    await expect(page.getByRole("alert")).toContainText("La limite de votre forfait est atteinte");
    await expect(page).toHaveURL(/\/setup$/);
  });
});
