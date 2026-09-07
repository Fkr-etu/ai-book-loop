import { test, expect } from "@playwright/test";

const email = `e2e-${Date.now()}@bookloop-e2e.com`;
const password = "BookLoop-E2E-123!";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API author journey", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("registers, configures, approves the outline and generates a chapter", async ({ page }) => {
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
    await expect(page.getByRole("heading", { name: "Plan global" })).toBeVisible();

    await page.getByRole("button", { name: "Générer le plan IA" }).click();
    await expect(page.getByRole("heading", { name: "Plan proposé", exact: true })).toBeVisible();
    await expect(page.getByTestId("approve-outline-btn")).toBeEnabled();
    await page.getByTestId("approve-outline-btn").click();
    await expect(page.getByText("Plan approuvé")).toBeVisible();

    const proposedOutline = await page.locator("pre").innerText();
    const firstChapterTitle = proposedOutline.match(/^## Chapitre 1: (.+)$/m)?.[1]?.trim();
    expect(firstChapterTitle).toBeTruthy();

    await page.getByTestId("add-chapter-btn").click();
    await page.locator('form input[type="text"]').nth(0).fill(firstChapterTitle!);
    await page.locator('form input[type="text"]').nth(1).fill("Poser le conflit initial.");

    const createChapterResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes("/api/books/") &&
        response.url().endsWith("/chapters") &&
        response.request().method() === "POST"
    );
    await page.getByRole("button", { name: "Créer le chapitre" }).click();

    const createChapterResponse = await createChapterResponsePromise;
    expect(createChapterResponse.ok()).toBeTruthy();
    const createdBook = (await createChapterResponse.json()) as {
      chapters?: Array<{ number: number; title: string }>;
    };
    const createdChapter = createdBook.chapters?.at(-1);
    expect(createdChapter?.number).toBe(1);
    expect(createdChapter?.title).toBe(firstChapterTitle);

    await expect(page.getByRole("heading", { name: firstChapterTitle!, exact: true })).toBeVisible();

    await page.goto("/studio/chapters");
    await expect(page.getByRole("heading", { name: "Rédiger, vérifier, décider" })).toBeVisible();
    await page.getByRole("button", { name: "Générer" }).click();

    await expect(page.getByRole("button", { name: /v1 ·/ })).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");

    await page.reload();
    await expect(page.getByRole("textbox", { name: "Contenu du chapitre" })).not.toHaveValue("");
    await expect(page.getByText("Version courante")).toBeVisible();

    await expect(page.getByRole("button", { name: "Approuver" })).toBeVisible();
    await page.getByRole("button", { name: "Approuver" }).click();
    await expect(page.getByText("Canon approuvé")).toBeVisible();

    await page.goto("/studio/canon");
    await expect(page.getByRole("heading", { name: "Revue du Canon" })).toBeVisible();
    await expect(page.getByText("Proposition IA").first()).toBeVisible();
    await expect(page.getByText("Aucune proposition ne devient canonique sans décision humaine.")).toBeVisible();

    const acceptButton = page.getByRole("button", { name: "Accepter" });
    await expect(acceptButton).toBeVisible();
    await acceptButton.click();
    await expect(page.getByText("Propositions à décider").locator("..")).toContainText("0");
    await expect(page.getByText("Faits acceptés").locator("..")).toContainText("1");

    const analyzeImpactButton = page.getByRole("button", { name: "Analyser l'impact" }).first();
    await expect(analyzeImpactButton).toBeVisible();
    await analyzeImpactButton.click();
    await expect(page.getByText("Fait analysé")).toBeVisible();
    await expect(page.getByText("Aucune preuve source affectée trouvée")).toBeVisible();
  });
});
