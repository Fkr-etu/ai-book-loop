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
    await page.getByRole("textbox").nth(0).fill("Projet quota Free");
    await page.getByRole("textbox").nth(1).fill("Fantasy");
    await page.getByRole("textbox").nth(2).fill("Vérifier que la capacité projet est imposée par le backend.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Règles, Reliques et Lieux Canoniques" })).toBeVisible();
    await page.getByPlaceholder("Ex: Dans l'Empire de Cendres, les mages utilisent l'Obsidienne pour capturer la mémoire...").fill("Une seule œuvre active est autorisée sur Free.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Ton, Voix Narrative & Verrouillage Canon" })).toBeVisible();
    await page.getByPlaceholder("Ex: Scholastique, poétique, sombre, rythme soutenu mais descriptif.").fill("Sobre et précis.");
    await page.getByRole("button", { name: "Ouvrir l'Atelier de Rédaction" }).click();

    await expect(page).toHaveURL(/\/studio(?:\?.*)?$/);
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Bibliothèque & Tableau de Bord" })).toBeVisible();
    await expect(page.getByText("Vos récits (1)")).toBeVisible();

    await page.getByRole("button", { name: "Nouveau Livre" }).click();
    await page.getByLabel("Titre").fill("Projet quota refusé");
    await page.getByLabel("Thème").fill("Fantasy");
    await page.getByLabel("Intention de l'auteur").fill("Ce projet doit être refusé par la capacité du forfait Free.");

    const createResponsePromise = page.waitForResponse(
      (response) => response.url().endsWith("/api/books") && response.request().method() === "POST"
    );
    await page.getByRole("button", { name: "Créer et ouvrir l'atelier" }).click();

    const createResponse = await createResponsePromise;
    expect(createResponse.status()).toBe(429);
    await expect(page.getByRole("alert")).toContainText("La limite de votre forfait est atteinte");
    await expect(page.getByText("Vos récits (1)")).toBeVisible();
  });
});
