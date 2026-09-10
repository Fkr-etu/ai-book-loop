import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — first chapter writing", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("makes the first chapter immediately writable and keeps the setup character", async ({ page }) => {
    const email = `writing-${Date.now()}@bookloop-e2e.com`;
    const password = "BookLoop-E2E-123!";
    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) await cookieBanner.getByRole("button", { name: "Refuser" }).click();
    await page.getByPlaceholder("Votre nom ou pseudonyme").fill("Writing Author");
    await page.getByPlaceholder("votre@email.com").fill(email);
    await page.getByPlaceholder("8 caractères minimum").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Premier chapitre E2E");
    await page.getByLabel("De quoi parle votre histoire ?").fill("Une archiviste découvre un secret dans les souvenirs de sa ville.");
    await page.getByTestId("next-step-btn").click();
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Personnage" }).click();
    await page.getByPlaceholder("Nom du personnage").fill("Maya");
    await page.getByPlaceholder("Ce que vous savez déjà de cet élément…").fill("Archiviste et protagoniste.");
    await page.getByRole("button", { name: "Ajouter cet élément" }).click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();
    await page.getByRole("button", { name: /C'est bien ça — commencer l'atelier/ }).click();

    const bookId = new URL(page.url()).searchParams.get("bookId");
    expect(bookId).toBeTruthy();
    await page.goto("/studio/outline");
    await page.getByRole("button", { name: "Générer le plan IA" }).click();
    await expect(page.getByRole("heading", { name: "Plan proposé", exact: true })).toBeVisible();
    await page.getByTestId("approve-outline-btn").click();
    await page.getByTestId("add-chapter-btn").click();
    await page.getByRole("button", { name: "Créer le chapitre" }).click();

    await page.goto("/studio/chapters");
    await expect(page.getByRole("button", { name: /Version 1/ })).toBeVisible();
    const editor = page.getByRole("textbox", { name: "Contenu du chapitre" });
    await editor.fill("Maya ouvre le registre et comprend que quelqu'un a réécrit son passé.");
    await page.getByRole("button", { name: "Enregistrer" }).click();
    await expect(page.getByRole("button", { name: /Version 2/ })).toBeVisible();
    await page.reload();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).toHaveValue("Maya ouvre le registre et comprend que quelqu'un a réécrit son passé.");

    await page.goto(`/studio/characters?bookId=${encodeURIComponent(bookId!)}`);
    await expect(page.getByText("Maya", { exact: true })).toBeVisible();
  });
});
