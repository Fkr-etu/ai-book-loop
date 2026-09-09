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
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Livre A — premier récit");
    await page.getByRole("button", { name: "Fantasy" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill("Premier projet de test multi-livres.");
    await page.getByTestId("next-step-btn").click();
    await page.getByLabel("Qu'aimeriez-vous faire ressentir, raconter ou explorer ?").fill("Construire un premier récit.");
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();
    await page.getByRole("button", { name: /C'est bien ça — commencer l'atelier/ }).click();
    await expect(page).toHaveURL(/\/studio\?bookId=/);

    await page.goto("/dashboard");
    await expect(page.getByText("Vos récits (1)")).toBeVisible();

    await page.getByRole("link", { name: "Commencer un livre" }).click();
    await expect(page).toHaveURL(/\/setup$/);
    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Livre B — récit sélectionné");
    await page.getByRole("button", { name: "Science-fiction" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill("Deuxième projet de test multi-livres.");
    await page.getByTestId("next-step-btn").click();
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();
    await page.getByRole("button", { name: /C'est bien ça — commencer l'atelier/ }).click();

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
