import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API multi-book selection", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("selects the second book and keeps it selected after refresh", async ({ page }) => {
    const email = `e2e-multi-book-${Date.now()}@bookloop-e2e.com`;
    const password = "BookLoop-E2E-123!";

    await page.goto("/register");

    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByPlaceholder("Votre nom ou pseudonyme").fill("E2E Multi Book Author");
    await page.getByPlaceholder("votre@email.com").fill(email);
    await page.getByPlaceholder("8 caractères minimum").fill(password);
    await page.getByRole("button", { name: "Démarrer le Setup du Premier Projet" }).click();

    await expect(page).toHaveURL(/\/setup$/);
    await page.getByRole("textbox").nth(0).fill("Livre A — premier récit");
    await page.getByRole("textbox").nth(1).fill("Fantasy");
    await page.getByRole("textbox").nth(2).fill("Premier projet de test multi-livres.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Lore et règles du monde" })).toBeVisible();
    await page.getByPlaceholder("Ex: Dans l'Empire de Cendres, les mages utilisent l'Obsidienne pour capturer la mémoire...").fill("Lore du livre A.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Contraintes du livre" })).toBeVisible();
    await page.getByRole("button", { name: "Ouvrir l'Atelier de Rédaction" }).click();
    await expect(page).toHaveURL(/\/studio$/);

    await page.goto("/dashboard");
    await expect(page.getByText("Vos récits (1)")).toBeVisible();

    await page.getByRole("button", { name: "Nouveau Livre" }).click();
    await page.getByLabel("Titre").fill("Livre B — récit sélectionné");
    await page.getByLabel("Thème").fill("Science-fiction");
    await page.getByLabel("Intention de l'auteur").fill("Deuxième projet de test multi-livres.");
    await page.getByRole("button", { name: "Créer et ouvrir l'atelier" }).click();

    await expect(page).toHaveURL(/\/studio\?bookId=/);
    await expect(page.getByText("Livre B — récit sélectionné", { exact: true })).toBeVisible();

    const selectedBookUrl = page.url();
    expect(selectedBookUrl).toContain("bookId=");

    await page.reload();

    await expect(page).toHaveURL(selectedBookUrl);
    await expect(page.getByText("Livre B — récit sélectionné", { exact: true })).toBeVisible();
    await expect(page.getByText("Livre A — premier récit", { exact: true })).not.toBeVisible();
  });
});
