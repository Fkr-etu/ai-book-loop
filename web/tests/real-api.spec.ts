import { test, expect } from "@playwright/test";

const email = `e2e-${Date.now()}@bookloop-e2e.com`;
const password = "BookLoop-E2E-123!";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API author journey", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("registers, configures, approves the outline, completes two chapters and evolves Canon through review", async ({ page }) => {
    page.on("response", async (response) => {
      if (response.url().endsWith("/api/auth/register")) console.log(`[real-api] register ${response.status()} ${await response.text()}`);
    });

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByPlaceholder("Votre nom ou pseudonyme").fill("E2E Author");
    await page.getByPlaceholder("votre@email.com").fill(email);
    await page.getByPlaceholder("8 caractères minimum").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Le livre E2E");
    await page.getByRole("button", { name: "Fantasy" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill("Une jeune archiviste découvre que ses souvenirs ont été volontairement modifiés.");
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Qu'avez-vous envie de raconter ?" })).toBeVisible();
    await page.getByLabel("Qu'aimeriez-vous faire ressentir, raconter ou explorer ?").fill("Explorer la confiance et le choix de l'auteur face aux propositions de l'IA.");
    await page.getByRole("button", { name: "Créer du suspense" }).click();
    await page.getByRole("button", { name: "Tendu" }).click();
    await page.getByPlaceholder("Ajouter une contrainte").fill("Les décisions de l'auteur restent canoniques");
    await page.getByRole("button", { name: "Ajouter une contrainte" }).click();
    await page.getByTestId("next-step-btn").click();

    await expect(page.getByRole("heading", { name: "Quels éléments importants connaissez-vous déjà ?" })).toBeVisible();
    await page.getByRole("button", { name: "Personnage" }).click();
    await page.getByPlaceholder("Nom du personnage").fill("Maya");
    await page.getByPlaceholder("Ce que vous savez déjà de cet élément…").fill("Archiviste, protagoniste de l'histoire.");
    await page.getByRole("button", { name: "Ajouter cet élément" }).click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();

    await expect(page.getByRole("heading", { name: "Voici ce que nous avons compris" })).toBeVisible();
    await expect(page.getByText("Le livre E2E", { exact: true })).toBeVisible();
    await expect(page.getByText("Maya", { exact: true })).toBeVisible();
    await page.getByRole("button", { name: /C'est bien ça — commencer l'atelier/ }).click();

    await expect(page).toHaveURL(/\/studio\?bookId=/);
    await page.goto("/studio/outline");
    await expect(page.getByRole("heading", { name: "Plan du livre" })).toBeVisible();
    await page.getByRole("button", { name: "Générer le plan IA" }).click();
    await expect(page.getByRole("heading", { name: "Plan proposé", exact: true })).toBeVisible();
    await expect(page.getByTestId("approve-outline-btn")).toBeEnabled();
    const proposedOutline = await page.locator("pre").innerText();
    const firstChapterTitle = proposedOutline.match(/^## Chapitre 1: (.+)$/m)?.[1]?.trim();
    const secondChapterTitle = proposedOutline.match(/^## Chapitre 2: (.+)$/m)?.[1]?.trim();
    expect(firstChapterTitle).toBeTruthy();
    expect(secondChapterTitle).toBeTruthy();
    await page.getByTestId("approve-outline-btn").click();
    await expect(page.getByText("Plan approuvé")).toBeVisible();

    await page.getByTestId("add-chapter-btn").click();
    await page.locator('form input[type="text"]').nth(0).fill(firstChapterTitle!);
    await page.locator('form input[type="text"]').nth(1).fill("Poser le conflit initial.");
    const createChapterResponsePromise = page.waitForResponse((response) => response.url().includes("/api/books/") && response.url().endsWith("/chapters") && response.request().method() === "POST");
    await page.getByRole("button", { name: "Créer le chapitre" }).click();
    const createChapterResponse = await createChapterResponsePromise;
    expect(createChapterResponse.ok()).toBeTruthy();
    const createdBook = (await createChapterResponse.json()) as { chapters?: Array<{ number: number; title: string }> };
    expect(createdBook.chapters?.at(-1)).toMatchObject({ number: 1, title: firstChapterTitle });
    const bookApiBase = createChapterResponse.url().replace(/\/chapters$/, "");

    await page.goto("/studio/chapters");
    await expect(page.getByRole("heading", { name: "Écrire, relire, décider" })).toBeVisible();
    await page.getByRole("button", { name: "Générer une version" }).click();
    await expect(page.getByRole("button", { name: /Version 1 ·/ })).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await page.reload();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await expect(page.getByRole("button", { name: "Approuver" })).toBeVisible();
    await page.getByRole("button", { name: "Approuver" }).click();
    await expect(page.getByText("Chapitre approuvé")).toBeVisible();

    await page.goto("/studio/canon");
    await expect(page.getByRole("heading", { name: "Revue du Canon" })).toBeVisible();
    const acceptAssertionButton = page.getByRole("button", { name: "Accepter" }).first();
    await expect(acceptAssertionButton).toBeVisible();
    await acceptAssertionButton.click();
    await expect(page.getByText("Faits acceptés").locator("..")).toContainText("1");

    const factsResponse = await page.request.get(`${bookApiBase}/canonical-facts`);
    expect(factsResponse.ok()).toBeTruthy();
    const facts = (await factsResponse.json()) as { facts: Array<{ id: string; statement: string; version: number; active: boolean }> };
    expect(facts.facts).toHaveLength(1);
    const originalFact = facts.facts[0];
    expect(originalFact.active).toBe(true);
    expect(originalFact.version).toBe(1);

    await page.getByLabel("Nouvelle affirmation").fill(`${originalFact.statement} [corrigé]`);
    await page.getByLabel("Nouvel objet").fill("Aix-en-Provence");
    await page.getByLabel("Raison").fill("Correction validée par l'auteur.");
    await page.getByRole("button", { name: "Analyser l'impact" }).click();
    await expect(page.getByText("Analyse d'impact")).toBeVisible();
    const createProposalResponsePromise = page.waitForResponse((response) => response.url().endsWith("/canon-change-proposals") && response.request().method() === "POST");
    await page.getByRole("button", { name: "Créer la proposition" }).click();
    const createProposalResponse = await createProposalResponsePromise;
    expect(createProposalResponse.ok()).toBeTruthy();
  });
});
