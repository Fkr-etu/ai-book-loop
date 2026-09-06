import { test, expect } from "@playwright/test";

const email = `e2e-${Date.now()}@example.test`;
const password = "BookLoop-E2E-123!";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API author journey", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("registers, configures, approves the outline and generates a chapter", async ({ page }) => {
    await page.goto("/register");
    await page.getByPlaceholder("Votre nom ou pseudonyme").fill("E2E Author");
    await page.getByPlaceholder("votre@email.com").fill(email);
    await page.getByPlaceholder("8 caractères minimum").fill(password);
    await page.getByRole("button", { name: "Démarrer le Setup du Premier Projet" }).click();

    await expect(page).toHaveURL(/\/setup$/);
    await page.getByRole("textbox").nth(0).fill("Le livre E2E");
    await page.getByRole("textbox").nth(1).fill("Fantasy");
    await page.getByRole("textbox").nth(2).fill("Le choix de l'auteur face aux propositions de l'IA.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Règles, Reliques et Lieux Canoniques" })).toBeVisible();
    await page.getByPlaceholder("Ex: Dans l'Empire de Cendres, les mages utilisent l'Obsidienne pour capturer la mémoire...").fill("Un monde où les décisions de l'auteur restent canoniques.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Ton, Voix Narrative & Verrouillage Canon" })).toBeVisible();
    await page.getByPlaceholder("Ex: Scholastique, poétique, sombre, rythme soutenu mais descriptif.").fill("Sobre, immersif et précis.");
    await page.getByRole("button", { name: "Ouvrir l'Atelier de Rédaction" }).click();

    await expect(page).toHaveURL(/\/studio$/);
    await page.goto("/studio/outline");
    await expect(page.getByRole("heading", { name: "Plan global" })).toBeVisible();

    await page.getByRole("button", { name: "Générer le plan IA" }).click();
    await expect(page.getByText("Plan proposé")).toBeVisible();
    await expect(page.getByTestId("approve-outline-btn")).toBeEnabled();
    await page.getByTestId("approve-outline-btn").click();
    await expect(page.getByText("Plan approuvé")).toBeVisible();

    await page.getByTestId("add-chapter-btn").click();
    await page.locator('form input[type="text"]').nth(0).fill("Le premier seuil");
    await page.locator('form input[type="text"]').nth(1).fill("Poser le conflit initial.");
    await page.getByRole("button", { name: "Créer le chapitre" }).click();
    await expect(page.getByRole("heading", { name: "Le premier seuil" })).toBeVisible();

    await page.goto("/studio/chapters");
    await expect(page.getByRole("heading", { name: "Rédiger, vérifier, décider" })).toBeVisible();
    await page.getByRole("button", { name: "Générer" }).click();

    await expect(page.getByRole("status")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole("button", { name: /v1 ·/ })).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");

    await page.reload();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await expect(page.getByText("Version courante")).toBeVisible();
  });
});
