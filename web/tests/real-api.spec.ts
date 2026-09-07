import { test, expect } from "@playwright/test";

const email = `e2e-${Date.now()}@bookloop-e2e.com`;
const password = "BookLoop-E2E-123!";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — real API author journey", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("registers, configures, approves the outline, generates a chapter and evolves Canon through review", async ({ page }) => {
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

    const acceptAssertionButton = page.getByRole("button", { name: "Accepter" });
    await expect(acceptAssertionButton).toBeVisible();
    await acceptAssertionButton.click();
    await expect(page.getByText("Propositions à décider").locator("..")).toContainText("0");
    await expect(page.getByText("Faits acceptés").locator("..")).toContainText("1");

    const analyzeImpactButton = page.getByRole("button", { name: "Analyser l'impact" }).first();
    await expect(analyzeImpactButton).toBeVisible();
    await analyzeImpactButton.click();
    await expect(page.getByText("Fait analysé")).toBeVisible();
    await expect(page.getByText("Aucune preuve source affectée trouvée")).toBeVisible();

    const factsBeforeProposalResponse = await page.request.get(/api\/books\/[^/]+\/canonical-facts/);
    expect(factsBeforeProposalResponse.ok()).toBeTruthy();
    const factsBeforeProposal = (await factsBeforeProposalResponse.json()) as {
      facts: Array<{ id: string; statement: string; object: string; version: number; active: boolean }>;
    };
    expect(factsBeforeProposal.facts).toHaveLength(1);
    const originalFact = factsBeforeProposal.facts[0];
    expect(originalFact.active).toBe(true);
    expect(originalFact.version).toBe(1);

    // Golden path: active Canon fact -> impact analysis -> proposal -> accept -> new version/history.
    await page.getByLabel("Nouvelle affirmation").fill("Céleste vit à Aix-en-Provence.");
    await page.getByLabel("Nouvel objet").fill("Aix-en-Provence");
    await page.getByLabel("Raison").fill("Correction validée par l'auteur.");

    await page.getByRole("button", { name: "Analyser l'impact" }).click();
    await expect(page.getByText("Analyse d'impact")).toBeVisible();

    const createProposalResponsePromise = page.waitForResponse(
      (response) =>
        response.url().endsWith("/canon-change-proposals") &&
        response.request().method() === "POST"
    );
    await page.getByRole("button", { name: "Créer la proposition" }).click();
    const createProposalResponse = await createProposalResponsePromise;
    expect(createProposalResponse.status()).toBe(201);

    const proposal = (await createProposalResponse.json()) as {
      id: string;
      canonical_fact_id: string;
      statement: string;
      object: string;
      status: string;
    };
    expect(proposal.canonical_fact_id).toBe(originalFact.id);
    expect(proposal.statement).toBe("Céleste vit à Aix-en-Provence.");
    expect(proposal.object).toBe("Aix-en-Provence");
    expect(proposal.status).toBe("proposed");
    await expect(page.getByText("La proposition a été enregistrée. Le Canon actif n'a pas encore changé.")).toBeVisible();
    await expect(page.getByText("À décider").first()).toBeVisible();

    const reviewAcceptResponsePromise = page.waitForResponse(
      (response) =>
        response.url().endsWith(`/canon-change-proposals/${proposal.id}/review`) &&
        response.request().method() === "POST"
    );
    await page.getByRole("button", { name: "Accepter" }).last().click();
    const reviewAcceptResponse = await reviewAcceptResponsePromise;
    expect(reviewAcceptResponse.ok()).toBeTruthy();
    expect((await reviewAcceptResponse.json()).decision).toBe("accept");
    await expect(page.getByText("Proposition acceptée : une nouvelle version du Canon est maintenant active.")).toBeVisible();

    const factsAfterAcceptResponse = await page.request.get(/api\/books\/[^/]+\/canonical-facts/);
    expect(factsAfterAcceptResponse.ok()).toBeTruthy();
    const factsAfterAccept = (await factsAfterAcceptResponse.json()) as {
      facts: Array<{ id: string; assertion_id: string; statement: string; object: string; version: number; active: boolean; previous_fact_id: string | null }>;
    };
    expect(factsAfterAccept.facts).toHaveLength(1);
    const acceptedFact = factsAfterAccept.facts[0];
    expect(acceptedFact.id).not.toBe(originalFact.id);
    expect(acceptedFact.assertion_id).toBe(originalFact.id);
    expect(acceptedFact.statement).toBe("Céleste vit à Aix-en-Provence.");
    expect(acceptedFact.object).toBe("Aix-en-Provence");
    expect(acceptedFact.version).toBe(2);
    expect(acceptedFact.active).toBe(true);
    expect(acceptedFact.previous_fact_id).toBe(originalFact.id);

    const proposalsAfterAcceptResponse = await page.request.get(/api\/books\/[^/]+\/canon-change-proposals/);
    expect(proposalsAfterAcceptResponse.ok()).toBeTruthy();
    const proposalsAfterAccept = (await proposalsAfterAcceptResponse.json()) as {
      proposals: Array<{ id: string; status: string }>;
    };
    expect(proposalsAfterAccept.proposals.find((item) => item.id === proposal.id)?.status).toBe("accepted");

    // Reject path: a rejected proposal must never mutate the active Canon.
    await page.getByLabel("Nouvelle affirmation").fill("Céleste vit à Marseille.");
    await page.getByLabel("Nouvel objet").fill("Marseille");
    await page.getByLabel("Raison").fill("Proposition volontairement rejetée par l'auteur.");

    const rejectProposalResponsePromise = page.waitForResponse(
      (response) =>
        response.url().endsWith("/canon-change-proposals") &&
        response.request().method() === "POST"
    );
    await page.getByRole("button", { name: "Créer la proposition" }).click();
    const rejectProposalResponse = await rejectProposalResponsePromise;
    expect(rejectProposalResponse.status()).toBe(201);
    const rejectedProposal = (await rejectProposalResponse.json()) as { id: string; status: string };
    expect(rejectedProposal.status).toBe("proposed");

    await expect(page.getByText("À décider").first()).toBeVisible();
    const reviewRejectResponsePromise = page.waitForResponse(
      (response) =>
        response.url().endsWith(`/canon-change-proposals/${rejectedProposal.id}/review`) &&
        response.request().method() === "POST"
    );
    await page.getByRole("button", { name: "Rejeter" }).last().click();
    const reviewRejectResponse = await reviewRejectResponsePromise;
    expect(reviewRejectResponse.ok()).toBeTruthy();
    expect((await reviewRejectResponse.json()).decision).toBe("reject");
    await expect(page.getByText("Proposition rejetée : le Canon actif reste inchangé.")).toBeVisible();

    const factsAfterRejectResponse = await page.request.get(/api\/books\/[^/]+\/canonical-facts/);
    expect(factsAfterRejectResponse.ok()).toBeTruthy();
    const factsAfterReject = (await factsAfterRejectResponse.json()) as {
      facts: Array<{ id: string; statement: string; object: string; version: number; active: boolean; previous_fact_id: string | null }>;
    };
    expect(factsAfterReject.facts).toHaveLength(1);
    expect(factsAfterReject.facts[0]).toMatchObject({
      id: acceptedFact.id,
      statement: "Céleste vit à Aix-en-Provence.",
      object: "Aix-en-Provence",
      version: 2,
      active: true,
      previous_fact_id: originalFact.id,
    });

    const proposalsAfterRejectResponse = await page.request.get(/api\/books\/[^/]+\/canon-change-proposals/);
    expect(proposalsAfterRejectResponse.ok()).toBeTruthy();
    const proposalsAfterReject = (await proposalsAfterRejectResponse.json()) as {
      proposals: Array<{ id: string; status: string }>;
    };
    expect(proposalsAfterReject.proposals.find((item) => item.id === rejectedProposal.id)?.status).toBe("rejected");
  });
});
