import { test, expect } from "@playwright/test";

test.describe("Book Loop - Complete Page Coverage Suite", () => {
  test("1. Login Page (/login) renders and allows navigation", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/Book Loop/);
    await expect(page.getByRole("heading", { name: "Manuscript Studio" })).toBeVisible();
    await expect(page.getByPlaceholder("auteur@manuscript.studio")).toBeVisible();
    await expect(page.getByRole("button", { name: "Connexion" })).toBeVisible();
  });

  test("2. Register Page (/register) renders and plan toggle works", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: "Créer votre espace d'écrivain" })).toBeVisible();
    await expect(page.getByText("Standard")).toBeVisible();
    await expect(page.getByText("Pro Studio")).toBeVisible();
    await page.getByText("Standard").click();
  });

  test("3. Project Setup Wizard (/setup) step-by-step flow", async ({ page }) => {
    await page.goto("/setup");
    await expect(page.getByText("Titre, Genre & Thème du Livre")).toBeVisible();
    await page.getByPlaceholder("Ex: La Porte d'Obsidienne").fill("Mon Livre de Test");
    await page.getByTestId("next-step-btn").click();
    await expect(page.getByText("Règles, Reliques et Lieux Canoniques")).toBeVisible();
    await page.getByTestId("next-step-btn").click();
    await expect(page.getByText("Ton, Voix Narrative & Verrouillage Canon")).toBeVisible();
  });

  test("4. Atelier de Rédaction / Main Studio Desk (/studio)", async ({ page }) => {
    await page.goto("/studio");
    await expect(page.getByRole("button", { name: /Critique & Lint/ })).toBeVisible();
    await expect(page.getByText("Manuscript Studio — Parchment Canvas")).toBeVisible();
    const canvas = page.locator("textarea");
    await expect(canvas).toBeVisible();
    await canvas.type("\n\nUn nouveau paragraphe rédigé pendant le test automatique.");
  });

  test("5. Outline Structure Editor (/studio/outline)", async ({ page }) => {
    await page.goto("/studio/outline");
    await expect(page.getByRole("heading", { name: "Éditeur de Plan Global" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Le Murmure du Parchemin" })).toBeVisible();
    await page.getByRole("button", { name: "Nouveau Chapitre" }).click();
    await page.getByPlaceholder("Titre du Chapitre (ex: Le Scriptorium Oublié)").fill("Chapitre Automatisé");
    await page.getByRole("button", { name: "Créer le Chapitre" }).click();
    await expect(page.getByText("Chapitre Automatisé")).toBeVisible();
  });

  test("6. Character Deep Editor (/studio/characters) renders", async ({ page }) => {
    await page.goto("/studio/characters");
    await expect(page.getByRole("heading", { name: "Éditeur de Personnages Profonds" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Archiviste Valerius" })).toBeVisible();
  });

  test("7. World Bible / Lore (/studio/lore) renders", async ({ page }) => {
    await page.goto("/studio/lore");
    await expect(page.getByRole("heading", { name: "Ancrage du Lore & Codex" })).toBeVisible();
    await expect(page.getByText("L'Obsidienne Stellaire")).toBeVisible();
  });

  test("8. Lore Relationship Graph (/studio/lore-graph) renders", async ({ page }) => {
    await page.goto("/studio/lore-graph");
    await expect(page.getByRole("heading", { name: "Graphe de Relations Lore & Personnages" })).toBeVisible();
    await expect(page.locator(".react-flow")).toBeVisible();
  });

  test("9. Creative Intention Lab (/studio/intention-lab) renders", async ({ page }) => {
    await page.goto("/studio/intention-lab");
    await expect(page.getByRole("heading", { name: "Laboratoire d'Intention" })).toBeVisible();
  });

  test("10. Validation Loop (/studio/validation-loop) renders", async ({ page }) => {
    await page.goto("/studio/validation-loop");
    await expect(page.getByRole("heading", { name: "Boucle de Validation (Linter + AI Review)" })).toBeVisible();
  });

  test("11. Export Studio (/studio/export) renders", async ({ page }) => {
    await page.goto("/studio/export");
    await expect(page.getByRole("heading", { name: "Studio d'Exportation" })).toBeVisible();
  });

  test("12. Dashboard & Book Hub (/dashboard) renders", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Bibliothèque & Tableau de Bord" })).toBeVisible();
  });

  test("13. Pricing Page (/pricing) renders", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.getByRole("heading", { name: "Payez pour créer. Pas pour compter les tokens." })).toBeVisible();
    await expect(page.getByText("Creator", { exact: true })).toBeVisible();
  });

  test("14. Legal pages expose the required public documents", async ({ page }) => {
    for (const route of ["/mentions-legales", "/politique-confidentialite", "/cgv"]) {
      await page.goto(route);
      await expect(page.locator("main")).toBeVisible();
      await expect(page.getByText(/Version du contenu/)).toBeVisible();
    }
  });

  test("15. Cookie consent is explicit and persisted", async ({ page }) => {
    await page.goto("/mentions-legales");
    const banner = page.getByRole("complementary", { name: "Préférences de cookies" });
    await expect(banner).toBeVisible();
    await page.getByRole("button", { name: "Refuser" }).click();
    await expect(banner).toBeHidden();
    await page.reload();
    await expect(banner).toBeHidden();
  });
});
