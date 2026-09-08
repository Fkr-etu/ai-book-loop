import { test, expect } from "@playwright/test";

const email = `e2e-${Date.now()}@bookloop-e2e.com`;
const password = "BookLoop-E2E-123!";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API author journey", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("registers, configures, approves the outline, completes two chapters and evolves Canon through review", async ({ page }) => {
    page.on("response", async (response) => {
      if (response.url().endsWith("/api/auth/register")) {
        console.log(`[real-api] register ${response.status()} ${await response.text()}`);
      }
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
    expect(createProposalResponse.status()).toBe(201);
    const proposal = (await createProposalResponse.json()) as { id: string; status: string };
    expect(proposal.status).toBe("proposed");
    await page.getByRole("button", { name: "Accepter" }).last().click();
    await expect(page.getByText("Proposition acceptée : une nouvelle version du Canon est maintenant active.")).toBeVisible();

    const updatedFactsResponse = await page.request.get(`${bookApiBase}/canonical-facts`);
    expect(updatedFactsResponse.ok()).toBeTruthy();
    const updatedFacts = (await updatedFactsResponse.json()) as { facts: Array<{ version: number; active: boolean; previous_fact_id: string | null }> };
    expect(updatedFacts.facts).toHaveLength(1);
    expect(updatedFacts.facts[0].version).toBe(2);
    expect(updatedFacts.facts[0].active).toBe(true);
    expect(updatedFacts.facts[0].previous_fact_id).toBe(originalFact.id);

    await page.goto("/studio/outline");
    await page.getByTestId("add-chapter-btn").click();
    await page.locator('form input[type="text"]').nth(0).fill(secondChapterTitle!);
    await page.locator('form input[type="text"]').nth(1).fill("Faire évoluer le conflit à partir du Canon approuvé.");
    const createSecondChapterResponsePromise = page.waitForResponse((response) => response.url().includes("/api/books/") && response.url().endsWith("/chapters") && response.request().method() === "POST");
    await page.getByRole("button", { name: "Créer le chapitre" }).click();
    const createSecondChapterResponse = await createSecondChapterResponsePromise;
    expect(createSecondChapterResponse.ok()).toBeTruthy();
    const bookAfterSecondChapter = (await createSecondChapterResponse.json()) as { chapters?: Array<{ number: number; title: string }> };
    expect(bookAfterSecondChapter.chapters?.at(-1)).toMatchObject({ number: 2, title: secondChapterTitle });

    await page.goto("/studio/chapters");
    await expect(page.getByRole("heading", { name: secondChapterTitle!, exact: true })).toBeVisible();
    await expect(page.getByText("Chapitre 2")).toBeVisible();
    await page.getByRole("button", { name: "Générer une version" }).click();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await page.reload();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await page.getByRole("button", { name: "Analyser le chapitre" }).click();
    await expect(page.getByText(/Score|Points à revoir|Aucune analyse/).first()).toBeVisible({ timeout: 20_000 });
    await page.reload();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await page.getByRole("button", { name: "Approuver" }).click();
    await expect(page.getByText("Chapitre approuvé")).toBeVisible();
  });
});
